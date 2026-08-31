import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog
from mpl_toolkits.mplot3d import Axes3D
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
import requests
import subprocess
import platform
import sys
import threading
import re
from sklearn.preprocessing import StandardScaler
from ui_oncology import OncologyUI
from ui_cardiology import CardiologyUI
from ui_neurology import NeurologyUI
from ui_internal_disease import InternalDiseaseUI


#---16 Branslık tam liste---

BRANCHES = [
     "pediatrics",
    "cardiology",
    "endocrinology",
    "nephrology",
    "gastroenterology",
    "pulmonology",
    "neurology",
    "oncology",
    "dermatology",
    "urology",
    "rheumatology",
    "orthopedics",
    "psychiatry",
    "cardiovascular_surgery",
    "endocrine_surgery",
    "anesthesia_icu",
    "internal_disease"
]

class DataAnalyseLogic:
    def __init__(self):
        self.df = None
        self.model = None

        import shutil
        print("Ollama PATH: ",shutil.which("ollama"))

    def load_data(self, file_path):
        # Try several encodings to avoid UnicodeDecodeError for files saved with different encodings
        encodings = ['utf-8', 'latin1', 'cp1254', 'iso-8859-1']
        df = None
        for enc in encodings:
            try:
                df = pd.read_csv(file_path, encoding=enc)
                print(f"read_csv succeeded with encoding: {enc}")
                break
            except UnicodeDecodeError:
                print(f"read_csv encoding {enc} failed (UnicodeDecodeError)")
            except Exception as e:
                print(f"read_csv encoding {enc} failed: {e}")

        if df is None:
            # Last-resort: replace invalid chars
            try:
                df = pd.read_csv(file_path, encoding='utf-8', errors='replace')
                print("read_csv succeeded with encoding utf-8 and errors='replace'")
            except Exception as e:
                print("read_csv final attempt failed:", e)
                raise

        self.df = df

        # Unnamed kolonları temizle
        self.df = self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]

        #---? işareti olanları eksik değere çevirdik
        self.df = self.df.replace("?",pd.NA)

        # Temel dtype dönüşümü
        #self.df = self.df.convert_dtypes()

        #Numeric kolonları numeric'e çevirme
        for col in self.df.columns:
            #Eğer kolon sayısal gibi görünüyorsa numeric'e çevir
            if self.df[col].astype(str).str.replace(".","",1).str.isnumeric().any():
                self.df[col] = pd.to_numeric(self.df[col],errors='coerce')
        #---String --> Category
        for col in self.df.columns:
            if self.df[col].dtype == "object":
                self.df[col] = self.df[col].astype("category")
        self.df_original = self.df.copy()
        return list(self.df.columns)


    def train(self, target, features,model_type):
        X = self.df[features].copy()
        y = self.df[target].copy()

        #Hedef kolon kategorik mi?
        is_categorical = (self.df[target].dtype == "object")


        #Kategorik hedef kolon ise encode et
        if is_categorical:
            le = LabelEncoder()
            y = le.fit_transform(y.astype(str))
            self.label_encoder = le

        # ---Feature kolonlarını Numeric'e çevir
        X = X.apply(pd.to_numeric, errors='coerce')

        # ---NaN satırları at---
        mask = X.notna().all(axis=1) & pd.notna(y)
        X = X[mask]
        y = y[mask]

        # ---Bos veri kontrolu--
        if len(X) == 0 or len(y) == 0:
            print("Filtre sonrası veri seti boş! Model eğitilemez.")
            return

        #--Model Seçimi--
        if model_type == "RandomForest":
            if is_categorical:
                from sklearn.ensemble import RandomForestClassifier
                self.model = RandomForestClassifier(n_estimators=200)
            else:
                from sklearn.ensemble import RandomForestRegressor
                self.model = RandomForestRegressor(n_estimators=200)

        elif model_type == "LogisticRegression":
            if not is_categorical:
                print("LogisticRegression sadece kategorik hedef kolonlarda çalışır!")
                return
            from sklearn.linear_model import LogisticRegression
            self.model = LogisticRegression(max_iter=2000)
        else:
            print("Bilinmeyen model türü!")
            return

        #----Sadece numeric kolonları seç----
        numeric_X = X.select_dtypes(include=["float64", "int64"])
        # Kolon isimlerini kaydet
        self.feature_names = numeric_X.columns.tolist()

        #---Ölçekleme / Numpy dönüşümü---

        if model_type == "LogisticRegression":
            scaler = StandardScaler()
            numeric_X = scaler.fit_transform(numeric_X)
            self.scaler = scaler
        else:
            numeric_X = numeric_X.values

        # -- Train-test split ---
        X_train, X_test, y_train, y_test = train_test_split(
            numeric_X, y, test_size=0.2, random_state=42)

        #Model Eğit
        self.model.fit(X_train, y_train)

        #Feature İmportance için gerekli
        self.X_train = X_train
        self.y_train = y_train

        return self.model.score(X_test, y_test)

    def predict(self, input_dict):
        feature_values = []
        # 1)FEature kolonlarını sırayla alıyor
        for col in self.feature_names:
            val = input_dict.get(col,None)

            if val is None:
                print(f"{col} için değer bulunamadı!")
                return None

            try:
                val = float(val)
            except:
                print(f"{col} numeric değil!")
                return None

            feature_values.append(val)

        # 2) Logistic Regression ise ölçekleme yap
        if hasattr(self,"scaler"):
            feature_values = self.scaler.transform([feature_values])
        else:
            feature_values = [feature_values]

        # 3) Tahmin yap
        pred = self.model.predict(feature_values)

        # 4) Eğer hedef kolon encode edildiyse geri çevir
        if hasattr(self,"label_encoder"):
            pred = self.label_encoder.inverse_transform(pred)

        return pred[0]

    def null_analysis(self):
        if self.df is None:
            print("Lütfen önce veri yükleyin!")
            return

        nulls = self.df.isnull().sum()
        print("\n--- Eksik Değer Analizi ---")
        for col, count in nulls.items():
            print(f"{col}: {count} adet eksik değer")
        print("---------------------------------------")

    def show_corr(self):
        if self.df is None:
            print("Lütfen önce veri yükleyin!")
            return

        numeric_df = self.df.select_dtypes(include=['float64', 'int64'])
        corr = numeric_df.corr()

        fig = plt.Figure(figsize=(12, 8))
        ax = fig.add_subplot(111)

        sns.heatmap(corr, annot=False, cmap='coolwarm',ax=ax)
        ax.set_title('Korelasyon Matrisi Heatmap')
        return fig

    def plot_scatter(self,x_col,y_col,color_col=None):
        fig = plt.Figure(figsize=(6,4))
        ax = fig.add_subplot(111)

        #Eğer renk kolonunu seçmişse ve kolon kategorikse
        if color_col and color_col in self.df.columns:
            unique_vals = self.df[color_col].unique()

            for val in unique_vals:
                subset = self.df[self.df[color_col] == val]
                ax.scatter(subset[x_col],subset[y_col],label=str(val))
            ax.legend()
        else:
            ax.scatter(self.df[x_col],self.df[y_col])

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{x_col} vs {y_col}")

        return fig


    def plot_line(self,x_col,y_col):
        fig = plt.Figure(figsize=(8,6))
        ax = fig.add_subplot(111)

        ax.plot(self.df[x_col],self.df[y_col])
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{x_col} vs {y_col} (Line Plot)")

        return fig


    def plot_box(self,col):
        if not pd.api.types.is_numeric_dtype(self.df[col]):
            print(f"{col} kolonunun tipi sayısal değil,boxplot çizilemez!")
            return

        fig = plt.Figure(figsize=(8,6))
        ax = fig.add_subplot(111)

        ax.boxplot(self.df[col])
        ax.set_title(f"{col} Boxplot")

        return fig

    def plot_hist(self,x_col,bins=30):
        if not pd.api.types.is_numeric_dtype(self.df[x_col]):
            print(f"{x_col} kolonunun tipi sayısal değil,histogram çizilemez!")
            return

        fig = plt.Figure(figsize=(8,6))
        ax = fig.add_subplot(111)

        ax.hist(self.df[x_col],bins=bins,color='skyblue',edgecolor='black')
        ax.set_xlabel(x_col)
        ax.set_ylabel("Frekans")
        ax.set_title(f"{x_col} Histogram")

        return fig

    def get_numeric_columns(self):
        numeric_cols = []
        for col in self.df.columns:
            try:
                pd.to_numeric(self.df[col],errors="raise")
                numeric_cols.append(col)
            except:
                pass
        return numeric_cols

    def get_categorical_columns(self):
        cat_cols = []

        for col in self.df.columns:
            #Eğer kolon string/object ise kategoriktir
            if self.df[col].dtype in ["string","object","category"]:
                cat_cols.append(col)
                continue

            #Eğer kolon numeric ama unique değer sayısı azsa kategoriktir
            if pd.api.types.is_numeric_dtype(self.df[col]):
                if self.df[col].nunique() <= 10: #Eşik 10
                    cat_cols.append(col)

        return cat_cols

    def column_stats(self,col):
        if col not in self.df.columns:
            return None

        stats = {}
        series = self.df[col]

        stats['mean'] = series.mean()
        stats['median'] = series.median()
        stats['mode'] = series.mode()
        stats['min'] = series.min()
        stats['max'] = series.max()
        stats['std'] = series.std()
        stats['var'] = series.var()
        stats['count'] = series.count()
        stats['unique'] = series.nunique()
        stats['top'] = series.mode()[0]
        stats['quantiles'] = series.quantile([0.25,0.5,0.75]).to_dict()

        return stats

    def mixed_stats(self,series):
        # Sayısal değerleri ayıklar
        numeric_vals = pd.to_numeric(series,errors='coerce')
        #Metinleri ayıklar
        text_vals = series[numeric_vals.isna()]

        result = {}
        #--Sayısal deger varsa ortalama
        if numeric_vals.notna().any():
            result["mean"] = numeric_vals.mean()
        #--Metin varsa ve mode bos değilse
        if not text_vals.empty:
            mode_vals = text_vals.mode()
            if len(mode_vals) > 0:
                result["mode"] = mode_vals.iloc[0]

        return result

    #Pairplot
    def plot_pairplot(self):
        pp = sns.pairplot(self.df)

        fig = pp.figure

        return fig

    #Countplot
    def plot_countplot(self,col):
        fig = plt.Figure(figsize=(16,9))
        ax = fig.add_subplot(111)

        sns.countplot(x=self.df[col],ax=ax)
        ax.set_title(f"{col} Countplot")
        return fig

    #Violin
    def plot_violin(self,col):
        fig = plt.Figure(figsize=(9,6))
        ax = fig.add_subplot(111)

        sns.violinplot(y=self.df[col],ax=ax)
        ax.set_title(f"{col} Violin Plot")

        return fig

    #KDE
    def plot_kde(self,col):
        #Kolon numeric'e çevirmeyi dene
        series = self.df[col]
        numeric_vals = pd.to_numeric(series,errors='coerce')

        #Sadece numeric olanları al
        numeric_vals = numeric_vals.dropna()

        #Eğer numeric yoksa uyarı ver
        if numeric_vals.empty:
            print(f"{col} kolonunda numeric veri yok,KDE plot çizilemez!")
        fig = plt.Figure(figsize=(12,8))
        ax = fig.add_subplot(111)

        sns.kdeplot(numeric_vals,fill=True,ax=ax)
        ax.set_title(f"{col} KDE Plot")

        return fig


    #Jointplot
    def plot_joint(self,x,y):
        jp = sns.jointplot(data=self.df,x=x,y=y,kind="scatter")

        #Jointplot figurunu al
        fig = jp.figure

        return fig

    #3D Scatter
    def plot_3d_scatter(self,x,y,z):
        #--Kolonları numeric"e çevir
        X = pd.to_numeric(self.df[x],errors="coerce")
        Y = pd.to_numeric(self.df[y],errors="coerce")
        Z = pd.to_numeric(self.df[z],errors="coerce")

        #--NaN satırları at
        mask = X.notna() & Y.notna() & Z.notna()
        X = X[mask]
        Y = Y[mask]
        Z = Z[mask]

        if len(X) == 0:
            print("Seçilen kolonlarda numeric yok,3D scatter çizilemez!")
            return

        fig = plt.Figure(figsize=(12,8))
        ax = fig.add_subplot(111,projection="3d")
        ax.scatter(X,Y,Z)

        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_zlabel(z)
        ax.set_title("3D Scatter Plot")

        return fig

    def feature_importance(self):
        if self.model is None:
            print("Model henüz eğitilmedi!")
            return None

        if self.X_train is None:
            print("X_train bulunamadı! Model eğitimi tamamlanmamış.")
            return None

        if not hasattr(self.model,"feature_importances_"):
            print("Bu model feature_importances_ desteklemiyor.")
            return None

        # X_train NumPy array -> kolon isimleri burdan alınıyor
        if hasattr(self,"feature_names"):
            feature_names = self.feature_names
        else:
            feature_names = [f"feature_{i}" for i in range(len(self.model.feature_importances_))]

        importances = self.model.feature_importances_

        return dict(zip(feature_names,importances))

    def plot_feature_importance(self):
        if self.model is None or not hasattr(self.model,"feature_importances_") or not hasattr(self,"X_train"):
            print("Model henüz eğitilmedi!")
            return

        importances = self.model.feature_importances_
        feature_names = self.X_train.columns
        fig = plt.Figure(figsize=(12,8))
        ax = fig.add_subplot(111)

        ax.barh(feature_names,importances)
        ax.set_xlabel("Önem Skoru")
        ax.set_title("Feature İmportance")

        return fig

    def apply_filter(self,col,op,value):
        try:
            #Kolonu numeric"e çevir
            series = pd.to_numeric(self.df[col],errors="coerce")

            #Değeri sayıya çevirmeyi dene
            value = pd.to_numeric(value,errors="coerce")

            #Eğer kolon numeric değilse uyarı ver
            if series.isna().all():
                print("Bu kolon sayısal değil,filtre uygulanamaz.!")
                return

            #Karşılaştırmayı numeric üzerinden yap
            if op == ">":
                self.df = self.df[series > value]
            elif op == "<":
                self.df = self.df[series < value]
            elif op == ">=":
                self.df = self.df[series >= value]
            elif op == "<=":
                self.df = self.df[series <= value]
            elif op == "==":
                self.df = self.df[series == value]
            elif op == "!=":
                self.df = self.df[series != value]

            print(f"Filtre uygulandı: {col} {op} {value}")

        except Exception as e:
            print("Filtreleme hatası: ",e)



    def generate_ai_report(self,col,value):
        # Değeri sınıflandır
        classification = self.classify_value(col,value)

        # Metni oluştur
        report=(
            f"{col} değeri: {value}\n"
            f"Sınıflandırma :{classification}\n"
            "Bu bulgu klinik olarak ne ifade ediyor?"
        )

        return report


    # ANSI temizleyici
    def clean_ansi(self, text):
        if not text:
            return ""
        # Tüm ANSI escape kodlarını temizler
        return re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', text)

    # Klinik analiz

    def get_ai_backend(self):
        system = platform.system()

        if system == "Windows":
            return {
                "type": "Ollama",
                "endpoint":"httpm://localhost:11434",
                "model":"llama3.1:8b"
            }
        elif system =="Linux":
            return {
                "type":"lmstudio",
                "endpoint":"http://localhost:1234/v1/chat/completions",
                "model":"Meta-Llama-8-8B-Instruct-GGUF"
            }
        return None

    def ask_ai(self, prompt):
        print("LOGIC.ASK_AI çağrıldı")
        backend = self.get_ai_backend()
        try:
            print("PROMPT:", repr(prompt))
            #------------------------------------
            #WINDOWS -> OLLAMA (SUBPROCES)
            #----------------------------------------
            if backend["type"] == "ollama":
                result = subprocess.run(
                    ["ollama", "run", "llama3.1:8b"],
                    input=prompt,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=320,
                    text=True,# stdout'u str olarak alır
                    encoding="utf-8"
                    )

                raw = result.stdout
                print("RAW AI:", repr(raw))

                clean = self.clean_ansi(raw)
                print("CLEAN AI:", repr(clean))

                return clean.strip()
            #-----------------------------------
            #LINUX -> STUDIO (HTTP API)
            #-----------------------------

            elif backend["type"] == "lmstudio":

                payload = {
                    "model": backend["model"],
                    "messages": [
                        {"role": "system", "content": "You are a clinical assistant. Reply with a short, professional Turkish clinical evaluation using only the provided columns. Do NOT wrap the response in JSON, dictionaries, or code blocks — return plain text only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.0,
                    "max_tokens": 800
                }

                resp = requests.post(
                    backend["endpoint"],
                    json=payload,
                    timeout=240
                )


                try:
                    resp.raise_for_status()
                except Exception as e:
                    print("LMStudio HTTP error:", e, "status:", getattr(resp, 'status_code', None), "text:", getattr(resp, 'text', None))
                    raise

                try:
                    data = resp.json()
                except Exception as e:
                    print("LMStudio JSON decode error:", e, "text:", getattr(resp, 'text', None))
                    raise

                print("LMStudio response keys:", list(data.keys()) if isinstance(data, dict) else type(data))

                raw = None


                if raw is None:
                    raw = data.get("text") or data.get("content")
                elif isinstance(data, list) and data:
                    first = data[0]
                    if isinstance(first, dict):
                        raw = first.get("content") or first.get("text")

                if not raw:
                    raise ValueError(f"Beklenmeyen yanıt yapısı: {data!r}")

                print("RAW AI", repr(raw))
                clean = self.clean_ansi(raw)
                print("CLEAN AI:", repr(clean))

            else:
                return "AI backend bulunamadı"

        except Exception as e:
            return f"AI hatası: {e}"

    # Çeviri
    def ask_ai_translate(self, text):
        print("LOGIC.ASK_AI_TRANSLATE çağrıldı")
        backend = self.get_ai_backend()

        try:
            #---Windows + OLLAMA---
            if backend["type"] == "ollama":
                result = subprocess.run(
                    ["ollama", "run", "llama3.1:8b"],
                    input=text,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=120,
                    text=True,
                    encoding="utf-8"
                    )

                raw = result.stdout
                print("RAW TR:", repr(raw))

                clean = self.clean_ansi(raw)
                print("CLEAN TR:", repr(clean))

                return clean.strip()
            elif backend["type"] == "lmstudio":
                resp = requests.post(
                    backend["endpoint"],
                    json={
                        "model": backend["model"],
                        "messages": [{"role": "user", "content": text}]
                    },
                    timeout=120
                )

                data = resp.json()
                raw = data["choices"][0]["message"]["content"]
                print("RAW TR:", repr(raw))

                clean = self.clean_ansi(raw)
                print("CLEAN TR:", repr(clean))

                return clean.strip()

            else:
                return "AI backend bulunamadı."

        except Exception as e:
            return f"AI TRANSLATE hatası: {e}"

class DataAnalyseGUI:
    def __init__(self, root,logic):
        self.root = root
        self.root.geometry("1400x950")
        try:
            self.root.state("zoomed")
        except:
            self.root.attributes("-zoomed",True)
        self.root.title("Data Analysing Program")
        self.logic = logic
        self.current_module = None
        self.ui_oncology = None

        #---- Sol taraf----
        self.frame_left = tk.Frame(self.root)
        self.frame_left.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)

        #---Sol Orta Kısım
        self.frame_middle_left = tk.Frame(self.root)
        self.frame_middle_left.grid(row=0,column=1,sticky="nsew",pady=5,padx=5)

        # ---Orta taraf----
        self.frame_center = tk.Frame(self.root)
        self.frame_center.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        #--- Sağ Orta Kısım ----
        self.frame_middle_right = tk.Frame(self.root)
        self.frame_middle_right.grid(row=0,column=3,sticky="nsew",pady=5,padx=5)

        # ---SAĞ TARAF---
        self.frame_right = tk.Frame(self.root)
        self.frame_right.grid(row=0, column=4, sticky="nsew", pady=10, padx=10)

        # --Enties dict---
        self.entries = {}

        # --- Root'u Responsive Yap
        self.root.grid_rowconfigure(0,weight=1)
        self.root.grid_columnconfigure(0,weight=1)
        self.root.grid_columnconfigure(1,weight=1)
        self.root.grid_columnconfigure(2,weight=2)
        self.root.grid_columnconfigure(3,weight=1)
        self.root.grid_columnconfigure(4,weight=1)

        #----Sol Orta Kısım Respınsive---
        self.frame_middle_left.grid_rowconfigure(0,weight=1)
        self.frame_middle_left.grid_columnconfigure(0,weight=1)

        #--- frame_center responsive ---
        self.frame_center.grid_rowconfigure(0,weight=0)
        self.frame_center.grid_rowconfigure(1, weight=0)
        self.frame_center.grid_rowconfigure(2, weight=0)
        self.frame_center.grid_rowconfigure(3, weight=0)
        self.frame_center.grid_rowconfigure(4, weight=0)
        self.frame_center.grid_rowconfigure(5, weight=0)
        self.frame_center.grid_rowconfigure(6, weight=0)
        self.frame_center.grid_rowconfigure(7, weight=0)
        self.frame_center.grid_rowconfigure(8, weight=0)
        self.frame_center.grid_rowconfigure(9, weight=0)
        self.frame_center.grid_columnconfigure(0,weight=1)

        #---Sağ Orta Kısım Responsive ----
        self.frame_middle_right.grid_rowconfigure(0,weight=1)
        self.frame_middle_right.grid_columnconfigure(0,weight=1)

        # ---frame_right responsive yap
        self.frame_right.grid_rowconfigure(0,weight=0)
        self.frame_right.grid_rowconfigure(1, weight=0)
        self.frame_right.grid_rowconfigure(2, weight=1)
        self.frame_right.grid_rowconfigure(3, weight=1)
        self.frame_right.grid_rowconfigure(4, weight=1)
        self.frame_right.grid_rowconfigure(5, weight=0)
        self.frame_right.grid_columnconfigure(0,weight=1)

        # ----VERİ YÜKLEME---
        self.button_upload = tk.Button(self.frame_left, text='Veri Seti Yükle', command=self.file_upload)
        self.button_upload.grid(row=1, column=0, pady=10)

        # ---SÜTUN TİPLERİ----
        self.lbl_types = tk.Label(self.frame_left, text='Sütun Türleri:')
        self.lbl_types.grid(row=2,column=0,sticky="w")

        list_frame = tk.Frame(self.frame_left)
        list_frame.grid(row=3,column=0,sticky="nsew")

        #Listbox
        self.list_types = tk.Listbox(list_frame, height=6)
        self.list_types.grid(row=0,column=0,pady=5)

        #Scrollbar
        list_scroll = tk.Scrollbar(list_frame,orient="vertical",command=self.list_types.yview)
        list_scroll.grid(row=0,column=1,sticky="ns")

        self.list_types.config(yscrollcommand=list_scroll.set)


        self.button_null = tk.Button(self.frame_left, text='Eksik Değer Analizi', command=self.null_analysis_gui)
        self.button_null.grid(row=4, column=0, pady=10)


        # ---EKSİK DEĞER DOLDURMA----
        self.lbl_fill = tk.Label(self.frame_left, text='Eksik Değer Doldurma:')
        self.lbl_fill.grid(row=5,column=0,pady=5)

        self.combo_fill_col = ttk.Combobox(self.frame_left,state="readonly")
        self.combo_fill_col.grid(row=6,column=0,pady=5)

        self.combo_fill_type = ttk.Combobox(self.frame_left, values=['mean', 'median', 'mode'])
        self.combo_fill_type.set('mean')
        self.combo_fill_type.grid(row=7,column=0,pady=5)

        self.button_fill = tk.Button(self.frame_left, text='Eksik Değer Doldur', command=self.fill_nulls_gui)
        self.button_fill.grid(row=8, column=0, pady=10)

        # ---KORELASYON MATRİSİ---
        self.button_corr = tk.Button(self.frame_left, text='Korelasyon Matrisi (Heatmap)', command=self.show_corr_gui)
        self.button_corr.grid(row=9, column=0, pady=10)

        #----KOLON İSTATİKLERİ---
        self.lbl_stats_col = tk.Label(self.frame_left,text="İstatistik Kolonu")
        self.lbl_stats_col.grid(row=10,column=0,pady=5)

        self.combo_stats_col = ttk.Combobox(self.frame_left,state="readonly")
        self.combo_stats_col.grid(row=11,column=0,pady=5)

        self.button_stats = tk.Button(self.frame_left,text='Kolon İstatistikleri',command=self.mixed_stats_gui)
        self.button_stats.grid(row=12,column=0,pady=5)

        self.combo_x = ttk.Combobox(self.frame_left, state="readonly")
        self.combo_x.grid(row=13, column=0, pady=5)

        self.combo_y = ttk.Combobox(self.frame_left, state="readonly")
        self.combo_y.grid(row=14, column=0, pady=5)

        #--- Renk Kolon Seçimi ---
        self.lbl_color = tk.Label(self.frame_left,text="Renk Kolonu:")
        self.lbl_color.grid(row=15,column=0,pady=5)

        self.combo_color=ttk.Combobox(self.frame_left,state='readonly')
        self.combo_color.grid(row=16,column=0,pady=5)

        #----GRAFİK ÇİZİMİ----
        self.graph_window = None

        self.lbl_plot_type = tk.Label(self.frame_left,text="Grafik Türü: ")
        self.lbl_plot_type.grid(row=17,column=0,pady=5)

        self.combo_plot_type = ttk.Combobox(self.frame_left,state="readonly",
                                            values=[
                                                'scatter',
                                                'line',
                                                'boxplot',
                                                'histogram',
                                                "pairplot",
                                                "countplot",
                                                "violin",
                                                "kde",
                                                "jointplot",
                                                "3d_scatter",
                                                "feature_importance"
                                            ])
        self.combo_plot_type.grid(row=18,column=0,pady=5)
        self.combo_plot_type.set('scatter') #varsayılan

        self.btn_scatter = tk.Button(self.frame_left,text="Grafik Çiz", command=self.draw_plot)
        self.btn_scatter.grid(row=19,column=0,pady=10)

        # HEDEF KOLON
        self.lbl_target = tk.Label(self.frame_center, text='Hedef Kolon (Label):')
        self.lbl_target.grid(row=1, column=0, pady=5)

        self.combo_target = ttk.Combobox(self.frame_center)
        self.combo_target.grid(row=2, column=0, pady=5)

        #Model Seçimi
        self.lbl_model = tk.Label(self.frame_center,text="Model Türü:")
        self.lbl_model.grid(row=3,column=0,pady=5)

        self.combo_model = ttk.Combobox(
            self.frame_center,
            state="readonly",
            values=["RandomForest","LogisticRegression"]
        )
        self.combo_model.grid(row=4,column=0,pady=5)
        self.combo_model.set("RandomForest")

        # ÖZELLİK KOLONLARI
        self.lbl_features = tk.Label(self.frame_center, text='Özellik Kolonları (Features):')
        self.lbl_features.grid(row=5, column=0, pady=5)

        #---Frame içine alıyorum---
        features_frame = tk.Frame(self.frame_center)
        features_frame.grid(row=6,column=0,sticky="nsew")

        #---Fatures_frame Responsive yaptm---
        features_frame.grid_rowconfigure(0,weight=1)
        features_frame.grid_columnconfigure(0,weight=1)

        #---Listbox---
        self.list_features = tk.Listbox(features_frame, selectmode='multiple', height=10)
        self.list_features.grid(row=0, column=0, sticky="nsew")

        #---Scrollbar---
        features_scroll = tk.Scrollbar(features_frame,orient="vertical",command=self.list_features.yview)
        features_scroll.grid(row=0,column=1,sticky="ns")

        self.list_features.config(yscrollcommand=features_scroll.set)

        self.lbl_score = tk.Label(self.frame_center, text="Henüz model eğitilmedi!")
        self.lbl_score.grid(row=7, column=0, pady=5)

        # ---MODEL EĞİTME---
        self.button_train = tk.Button(self.frame_center, text='Modeli Eğit', command=self.train_model)
        self.button_train.grid(row=8, column=0, pady=10)

        # ---TAHMİN---
        self.button_predict = tk.Button(self.frame_center, text='Tahmin Yap', command=self.predict_row)
        self.button_predict.grid(row=9,column=0,pady=10)


        #---Sağ panel branş seçimi---
        self.branch_var = tk.StringVar()

        self.branch_dropdown = ttk.Combobox(
            self.frame_right,
            textvariable=self.branch_var,
            values=BRANCHES,
            state="readonly",
            width=30
        )

        self.result_label = tk.Label(
            self.frame_right,
            text="Branş Seçiniz...",
            font=("Arial", 12)
        )

        self.result_label.grid(row=0, column=0, padx=10, pady=10)
        self.branch_dropdown.grid(row=1, column=0, padx=10, pady=10)
        self.branch_dropdown.bind("<<ComboboxSelected>>", self.on_branch_selected)

        #--- SAĞ panel: Filtreleme + AI
        self.filter_frame = tk.LabelFrame(self.frame_right,text="Filtreleme + AI")
        self.filter_frame.grid(row=3,column=0,sticky="nsew",pady=10)

        #--- BASİT FİLTRELEME---
        self.lbl_filter = tk.Label(self.filter_frame,text="Veri Filtreleme:")
        self.lbl_filter.grid(row=0,column=0,pady=5)

        self.combo_filter_col = ttk.Combobox(self.filter_frame,state="readonly")
        self.combo_filter_col.grid(row=1,column=0,pady=5)

        self.combo_filter_op = ttk.Combobox(self.filter_frame,state="readonly",
                                            values=["<",">",">=","<=","==","!="])
        self.combo_filter_op.grid(row=2,column=0,pady=5)
        self.combo_filter_op.set("==")

        self.entry_filter_value = tk.Entry(self.filter_frame)
        self.entry_filter_value.grid(row=3,column=0,pady=5)

        #Filtreleme düğmesi
        self.btn_apply_filter = tk.Button(self.filter_frame,text="Filtre Uygula",command=self.apply_filter_button)
        self.btn_apply_filter.grid(row=4,column=0,pady=10)

        self.btn_clear_filter = tk.Button(self.filter_frame, text="Filtreyi Kaldır", command=self.clear_filter_gui)
        self.btn_clear_filter.grid(row=5, column=0, columnspan=3, pady=5)


        # Türkce AI Yorum
        self.ai_text = tk.Text(
            self.filter_frame,
            height=10,
            width=40,
            font=("Arial",11),
            wrap="word"
        )

        self.ai_text.grid(row=7,column=0,padx=10,pady=10)

        scroll = tk.Scrollbar(self.filter_frame,orient="vertical",command=self.ai_text.yview)
        scroll.grid(row=7,column=1,sticky="ns")
        self.ai_text.config(yscrollcommand=scroll.set)
        tk.Frame(self.filter_frame, height=70).grid(row=8, column=0)


    def file_upload(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        columns = self.logic.load_data(file_path)
        if self.ui_oncology is not None:
            print("OncologyUI bulundu -> update_rows çağrılıyor")
            self.ui_oncology.update_rows(self.logic.df)
        else:
            print("OncologyUI yok -> update_rows cağırılmadı")

        print("file upload içindeki self:",self)
        print("ui_oncology var mı",hasattr(self,"ui_oncology"))

        # ---Target sadece kategorik kolonlar---
        categorical_cols = self.logic.df.select_dtypes(include=['object','string',"category","int64","float64"]).columns
        self.combo_target['values'] = list(categorical_cols)

        # ---Feature listesine sadece sayısal kolonlar---
        numeric_cols = self.logic.df.select_dtypes(include=['float64', 'int64']).columns
        self.list_features.delete(0, tk.END)
        for col in numeric_cols:
            self.list_features.insert(tk.END, col)

        # ---Eksik değer doldurma kolonları----
        self.combo_fill_col['values'] = columns

        # ---Sütun tipleri---
        self.list_types.delete(0, tk.END)
        for col, dtype in self.logic.df.dtypes.items():
            self.list_types.insert(tk.END, f"{col} ---> {dtype}")

        print("Veri başarıyla yüklendi, sütunlar kutulara doldu!")
        cols = list(self.logic.df.columns)
        self.combo_x['values'] = cols
        self.combo_y['values'] = cols

        #---RENK SEÇİMİ---
        cat_cols = self.logic.get_categorical_columns()
        self.combo_color['values']=cat_cols
        self.combo_color.set("")

        if len(cat_cols) == 0:
            self.combo_color.config(state="disabled")
        else:
            self.combo_color.config(state="readonly")

        #Sayısal Kolon Kontrolu
        numeric_cols = self.logic.get_numeric_columns()
        if len(numeric_cols) < 2:
            self.btn_scatter.config(state="disabled")
        else:
            self.btn_scatter.config(state="normal")

        self.combo_stats_col['values'] = list(self.logic.df.columns)
        self.combo_stats_col.set("")

        self.combo_filter_col["values"] = list(self.logic.df.columns)


    def collect_patient_data(self):
        patient_data = {}
        for key ,widget in self.entries.items():
            value = widget.get().strip()
            if value == "":
                continue
            try:
                patient_data[key] = float(value)
            except:
                patient_data[key] = value
        return patient_data

    def analyze_patient_data(self,patient_data,module):
        if module is None:
            return "Seçilen branş modül içinde bulunamadı!"

        analysis_lines = []

        for section_name,section_data in module.items():
            analysis_lines.append(f"\n ---- {section_name.upper()}---")

            for test_name,ranges in section_data.items():
                if test_name not in patient_data:
                    continue

                value = patient_data[test_name]
                result = " Referans Bulunamadı!"

                if isinstance(ranges,dict):
                    if "child" in ranges or "adult" in ranges or "elderly" in ranges:
                        age_group = "adult"
                        if age_group in ranges:
                            for low, high, label in ranges[age_group]:
                                if low <= value <= high:
                                    result= label
                                    break
                    else:
                        for low,high,label in ranges:
                            if low <= value <= high:
                                result = label
                                break
                else:
                    for low, high, label in ranges:
                        if low <= value <= high:
                            result = label
                            break

                analysis_lines.append(f"{test_name} : {value} -> {result}")
        return "\n".join(analysis_lines)

    def train_model(self):
        target = self.combo_target.get()
        if target == "":
            print("Lütfen hedef kolon seçin!")
            return
        elif target == int or target == float:
            print("Hedef kolon sayı olamaz! ")

        features = [self.list_features.get(i) for i in self.list_features.curselection()]
        if not features:
            print("Lütfen en az bir özellik kolon seçin!")
            return

        model_type = self.combo_model.get()
        accuracy = self.logic.train(target, features,model_type)
        # --- Eğer model eğitilmediyse ---
        if accuracy is None:
            self.lbl_score.config(text="Model eğitilmedi!")
            return

        self.model = self.logic.model
        self.lbl_score.config(text=f"Model Başarı Oranı: {accuracy:.2f}")
        print(f"Model Başarı oranı: {accuracy:.2f}")

        if self.logic.df is None or len(self.logic.df) == 0:
            return

        summary = self.generate_full_summary()
        if not summary.strip():
            print("AI analiz için yeterli veri yok!")
            return
        self.ask_ai_async(summary)

    def predict_row(self):
        if self.logic.model is None:
            print("Lütfen önce modeli eğitin!")
            return

        #--- veri seti boşmu?---
        if self.logic.df is None or len(self.logic.df) == 0:
            print("Veri seti boş!Tahmin yapılamaz!")
            return

        #---Filtre sonrası kalan satır sayısını göster
        total_rows = len(self.logic.df)
        print(f"Filtre sonrası kalan satır sayısı: {total_rows}")

        #Kullanıcıdan satır numarası al(geçerli aralık içinde)
        try:
            row_index = simpledialog.askinteger("Satır seç",
                                                f"Tahmin yapılacak satır numarası: (0- {total_rows - 1}):")
            if row_index is None:
                return

            if row_index < 0 or row_index >= total_rows:
                print("Geçersiz satır numarası!")
                return

            # Kullanıcının seçtiği feature kolonlarını al
            features = [self.list_features.get(i) for i in self.list_features.curselection()]
            if not features:
                print("Lütfen en az bir özellik kolon seçin!")
                return

            # Satırdan feature değerlerini çek -> input_dict oluştur

            row = self.logic.df.iloc[row_index]
            input_dict = {}

            for col in features:
                val = row[col]
                input_dict[col] = val

            #Tahmin yap
            prediction = self.logic.predict(input_dict)
            print(f"Tahmin: {prediction}")

        except Exception as e:
            print("Tahmin sırasında hata oluştu: ",e)
            return

        summary = self.generate_full_summary()
        if not summary.strip():
            print("AI analiz için yeterli veri yok!")
            return
        self.ask_ai_async(summary)

    def null_analysis_gui(self):
        self.logic.null_analysis()

    def show_corr_gui(self):
        fig = self.logic.show_corr()

        if fig is None:
            print("Heatmap oluşturulmadı! ")
            return

        #---Eğer pencere yoksa oluştur---
        if self.graph_window is None or not self.graph_window.winfo_exists():
            self.graph_window = tk.Toplevel(self.root)
            self.graph_window.title("Korelasyon Matrisi")

        #--- Eski grafiği temizle---
        for widget in self.graph_window.winfo_children():
            widget.destroy()

        # --- Yeni grafiği pencereye ekle ---
        canvas = FigureCanvasTkAgg(fig,master=self.graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both",expand=True)

        if self.logic.df is None or len(self.logic.df) == 0:
            return

        summary = self.generate_full_summary()
        self.ask_ai_async(summary)

    def fill_nulls_gui(self):
        if self.logic.df is None:
            print("Lütfen önce veri yükleyin!")
            return

        col = self.combo_fill_col.get()
        method = self.combo_fill_type.get()

        if col == "":
            print("Lütfen bir kolon seçin!")
            return

        #Sayısal Kolon Kontrolü(Eğer sayısal değise mean kullanılamaz
        if method in ["mean","median"]:
            if not pd.api.types.is_numeric_dtype(self.logic.df[col]):
                print(f"{col} kolonunun tipi sayısal değil,'{method}' uygulanamaz!")
                return

        if method == "mean":
            value = self.logic.df[col].mean()
        elif method == "median":
            value = self.logic.df[col].median()
        else:
            value = self.logic.df[col].mode()[0]

        #Int64 kolonuna float yazmayı engelle
        if str(self.logic.df[col].dtype) == "Int64":
            value = int(value)

        self.logic.df[col] = self.logic.df[col].fillna(value)
        print(f"{col} kolonundaki eksik değerler '{method}' ile dolduruldu.")

        if self.logic.df is None or len(self.logic.df) == 0:
            return

        summary = self.generate_full_summary()
        if not summary.strip():
            print("AI analiz için yeterli veri yok!")
            return
        self.ask_ai_async(summary)

    def scatter_plot(self):
        x = self.combo_x.get()
        y = self.combo_y.get()
        color=self.combo_color.get()

        self.logic.plot_scatter(x,y,color)

    def draw_plot(self):
        plot_type = self.combo_plot_type.get()
        x = self.combo_x.get()
        y = self.combo_y.get()
        color = self.combo_color.get()

        fig = None #Logicten gelecek olan figür

        if plot_type == "scatter":
            fig =self.logic.plot_scatter(x,y,color)
        elif plot_type == "line":
            fig = self.logic.plot_line(x,y)
        elif plot_type == "boxplot":
            fig = self.logic.plot_box(x)
        elif plot_type == "histogram":
            fig = self.logic.plot_hist(x)

        #Gelişmiş grafikler
        elif plot_type == "pairplot":
            fig = self.logic.plot_pairplot()

        elif plot_type == "countplot":
            col = self.combo_stats_col.get()
            if col == "":
                print("Lütfen bir kolon seçin!")
                return
            fig = self.logic.plot_countplot(col)

        elif plot_type == "violin":
            col = self.combo_stats_col.get()
            if col == "":
                print("Lütfen bir kolon seçin!")
                return
            fig = self.logic.plot_violin(col)

        elif plot_type == "kde":
            col = self.combo_stats_col.get()
            if col == "":
                print("Lütfen bir kolon seçin!")
                return
            fig = self.logic.plot_kde(col)

        elif plot_type == "jointplot":
            if x == "" or y == "":
                print("Lütfen X ve Y kolonlarını seçin!")
                return
            fig = self.logic.plot_joint(x,y)

        elif plot_type == "3d_scatter":
            z = self.combo_stats_col.get()
            if x == "" or y == "" or z == "":
                print("Lütfen X, Y ve Z kolonlarını seçin!")
                return
            fig = self.logic.plot_3d_scatter(x, y,z)

        elif plot_type == "feature_importance":
            if self.logic.model is None:
                print("Model henüz eğitilmedi!")
                return
            fig = self.logic.plot_feature_importance()

        if fig is None:
            print("Grafik oluşturulmadı!")
            return
        # --- Eğer pencere yoksa Yeni pencere ac ---
        if self.graph_window is None or not self.graph_window.winfo_exists():
            self.graph_window = tk.Toplevel(self.root)
            self.graph_window.title("Grafik")

        # --- Eski Grafiği temizle---
        for widget in self.graph_window.winfo_children():
            widget.destroy()

        #--- Yeni Grafiği Pencereye ekle
        canvas = FigureCanvasTkAgg(fig,master=self.graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both",expand=True)

        if self.logic.df is None or len(self.logic.df) == 0:
            return

        summary = self.generate_full_summary()
        self.ask_ai_async(summary)

    def show_stats(self):
        col = self.combo_stats_col.get()
        if col == "":
            print('Lütfen bir kolon seçin')
            return

        stats = self.logic.column_stats(col)
        if stats is None:
            print("İstatistik alınamadı")
            return

        print("\n---Kolon İstatistikler ---")
        for key ,value in stats.items():
            print(f"{key} : {value}")
        print("-------------------------------")

    def mixed_stats_gui(self):
       col = self.combo_stats_col.get()
       if col != "":
           report = self.logic.mixed_stats(self.logic.df[col])
           print(report)
           return

       print("Lütfen bir kolon seçin!")


    def apply_filter_gui(self):
        col = self.combo_filter_col.get()
        op = self.combo_filter_op.get()
        value = self.entry_filter_value.get()

        if col == "" or value == "":
            print("Lütfen bir kolon ve değer seçin!")
            return

        #---Sayısal kolon kontrolu
        if not pd.api.types.is_numeric_dtype(self.logic.df[col]):
            print("Bu kolon sayısal değil,filtre uygulanamaz!")
            return

        #---Filtreyi uygula---
        self.logic.apply_filter(col,op,value)
        print("Filtre uygulandı.")

        remaining = len(self.logic.df)


        if self.logic.df is None or remaining == 0:
            print(f"Filtre uygulandı fakat hiç satır bulunamadı!({col} {op} {value}")
            return

        print(f"Fiktre uygulandı: {col} {op} {value} -> Kalan sayır: {remaining}")

        # AI analiz için veri varsa devam et
        summary = self.generate_full_summary()
        if not summary.strip():
            print("AI analiz için yeterli veri yok!")
            return
        self.ask_ai_async(summary)

    def apply_filter_button(self):
        col = self.combo_filter_col.get()
        op = self.combo_filter_op.get()
        value = self.entry_filter_value.get()

        #Filtreyi uygula
        self.logic.apply_filter(col,op,value)

        #AI raporunu oluştur
        report = self.logic.generate_ai_report(col,value)

        # AI çağrısı
        self.ask_ai_async(report)

        if self.logic.df is None or len(self.logic.df) == 0:
            return

        summary = self.generate_full_summary()
        if not summary.strip():
            print("AI analiz için yeterli veri yok!")
            return
        self.ask_ai_async(summary)

    def generate_full_summary(self):

        if self.logic.df is None:
            return "AI:Veri seti henüz yüklenmedi.Lütfen önce bir veri seti yükleyin."
        summary = ""

        # ---  Veri Seti Bilgisi ---

        df = self.logic.df
        summary += "=== VERİ SETİ BİLGİSİ ===\n"
        if df is None or len(df) ==0:
            summary += "Veri seti yüklenmemiş veya boş.\n\n"
        else:
            summary += f"Toplam satır: {len(df)} \n"
            summary += f"Toplam kolon: {len(df.columns)}\n"
            summary += "Kolonlar ve tipleri:\n"
            for col,dtype in df.dtypes.items():
                summary += f"-- {col}: {dtype}\n"

            summary += "\nSayısal kolon istatistikleri:\n"
            numeric_cols = self.logic.get_numeric_columns()
            for col in numeric_cols:
                try:
                    summary += (f"{col} -> mean: {df[col].mean():.2f},"
                                f"min:{df[col].min():.2f}"
                                f"max: {df[col].max():.2f}\n")
                except:
                    pass

        summary += "\n"

        # --- FİLTRE Bilgisi
        summary += "===FİLTRE BİLGİSİ===\n"

        filter_col = self.combo_filter_col.get()
        filter_op = self.combo_filter_op.get()
        filter_val = self.entry_filter_value.get()

        if filter_col != "" or filter_val != "":
            summary += f"Uygulanan filtre: {filter_col} {filter_op} {filter_val} \n"
            summary += f"Filtre sonrası satır sayısı: {len(df)}\n"
        else:
            summary += "Aktif filtre yok.\n"

        summary += "\n"

        # --- MODEL Bilgisi ---

        summary += "===MODEL BİLGİSİ===\n"

        target = self.combo_target.get()
        summary += f"Hedef kolon (Label): {target if target else 'Seçilmedi'} \n"

        model_type = self.combo_model.get()
        summary += f"Model türü: {model_type if model_type else 'Seçilmedi'}\n"

        #Seçilen featurelar
        features = [self.list_features.get(i) for i in self.list_features.curselection()]
        summary += f"Özellik kolonları (Features): {features if features else 'Seçilmedi'}\n"

        #Model Başarı oranı
        score_text = self.lbl_score.cget("text")
        summary += f"Model başarı oranı: {score_text}\n"


        # --- Tahmin Bilgisi ---
        summary += "=== TAHMİN BİLGİSİ ===\n"
        summary += "Tahmin fonksiyonu hazır,kullanıcı seçtiğinde çalışır.\n"

        summary += "\n"

        #----GRAFİK BİLGİSİ ----
        summary += "===GRAFİK BİLGİSİ===\n"

        plot_type = self.combo_plot_type.get()
        summary += f"Seçilen grafik türü: {plot_type if plot_type else 'Seçilmedi'}\n"

        x = self.combo_x.get()
        y = self.combo_y.get()
        color = self.combo_color.get()

        summary += f"X kolon: {x if x else 'Seçilmedi'}\n"
        summary += f"Y kolon: {y if y else 'Seçilmedi'}\n"
        summary += f"Renk kolon: {color if color else 'Seçilmedi'}\n"

        # ---FEATURE_IMPORTANCE varsa ekle ----
        if self.logic.model is not None and hasattr(self.logic.model, "feature_importances_"):

            try:
                fi = self.logic.feature_importance()
                if fi:
                    summary += "\n Feature Importance:\n"
                    for k, v in fi.items():
                        summary += f" - {k}: {v:.4f} \n"
            except:
                summary += "\n Feature importance hesaplanamadı.\n"
        summary += "\n"

        summary += "\n=== GENEL DEĞERLENDİRME İSTEĞİ ===\n"
        summary += (
                    "Bu veriye,filtreye,modele,istatistiklere ve grafik"
                    "seçimlerine dayanarak analitik ve klinik bir değerlendirme yap."
                    "Veri setinin genel yapısını,modelin performansını,filtre etkisini"
                    " ve istatiksel bulguları yorumlar.\n "
                    )

        summary += "\n === KLİNİK ANALİZ VE TANI İSTEĞİ ==="

        summary += (
            "Bu veri setine,filtreye,modele,istatistiklere ve grafik seçimlerine dayanarak"
            "detaylı bir klinik analiz yap.Bulguları tek tek değerlendir.\n"
            "Ardından EN SONUNDA şu soruya tek cümleyle,NET ve DOĞRUDAN cevap ver:\n"
            "\"Bu hastada en olası klinik tabı nedir?\"\n"
            "Yuvarlak ifadeler kullanma.Kesin bir tanı cümlesi kur.\n"
            "Örnek:'Bu bulgular koroner arter hastalığı ile uyumludur'\n"
        )



        summary += "\n=== ÖZET SONU ==="

        summary += (
            "\n=== BAĞLAM SIFIRLAMA===\n"
            "Bu analiz tamamen bağımsızdır.Önceki analizlerle bağlantı kurma."
            "Bu veri setini tek başına değerlendir."
        )

        return summary[:3000]

    def run_ai_analysis(self, summary):
        try:
            result = self.logic.ask_ai(summary)
            self.ai_text.delete("1.0", "end")
            self.ai_text.insert("end", result)
        except Exception as e:
            self.ai_text.insert("end", f"\n\nAI analiz hatası: {e}")

    def ask_ai_async(self,summary):
        thread = threading.Thread(target=self.run_ai_analysis,args=(summary,))
        thread.daemon=True
        thread.start()

    def translate_to_turkish(self, text):
        prompt = f"""
        Aşağıdaki metni tıbbi anlamı bozulmadan Türkçeye çevir:

        {text}
        """
        return self.logic.ask_ai(prompt)

    def update_ai_text(self,ai_response):
        #GUİ güvenli yazma
        self.ai_text.delete("1.0", tk.END)
        #Gelen yaniti stringe cevirip guvenli yaziyoruz
        text_to_display = str(ai_response) if ai_response is not None else ""
        self.ai_text.insert(tk.END, text_to_display)

    def clear_filter_gui(self):
        print("Filtre kaldırıldı,veri yeniden yüklendi!")
        if hasattr(self.logic,"df_original") and self.logic.df_original is not None:
            self.logic.df = self.logic.df_original.copy()

            #Ekrandaki tabloyu da sifirlanmis ceriyle gunceller
            if hasattr(self,"update_table"):
                self.update_table(self.logic.df)

            self.ask_ai_async(self.generate_full_summary())

    def on_branch_selected(self,event):
        print("Branş seçildi",self.branch_var.get())
        selected = self.branch_var.get()
        self.result_label.config(text=f"Seçilen Branş:{selected}")

        #Modul cek
        self.current_module = None

        #---Brans Mapping(Branş adı,Modül adı,Sınıf adı)---
        branch_map = {
            "oncology": ("ui_oncology", "OncologyUI"),
            "cardiology": ("ui_cardiology", "CardiologyUI"),
            "neurology": ("ui_neurology", "NeurologyUI"),
            "internal_disease": ("ui_internal_disease", "InternalDiseaseUI")
        }

        if selected not in branch_map:
            print("Bu branş için UI henüz oluşturulmadı")
            return

        #--- Acik pencere kontrolu (Ayni pencere aciksa one getir)---
        attr_name = f"ui_{selected}"
        if hasattr(self,attr_name):
            existing_ui = getattr(self,attr_name)
            if existing_ui and hasattr(existing_ui, "root") and existing_ui.root.winfo_exists:
                existing_ui.root.lift()
                existing_ui.root.focus_force()
                return

        #---Dinamik yükleme ---
        module_name,class_name = branch_map[selected]

        #Modülü ihtiyaç anında dinamik çağırıyoruz
        import importlib
        module = importlib.import_module(module_name)
        ui_class = getattr(module,class_name)

        #Pencereyi ve UI sınıfnı tek noktadan olusturuyo
        new_window = tk.Toplevel(self.root)
        branch_ui_instance = ui_class(new_window,self.logic,self.current_module,self)

        #Nesneyi dinamik olarak değişkene atadım
        setattr(self,attr_name,branch_ui_instance)

       #---Veri  yükleme----
        if hasattr(self.logic,"df") and self.logic.df is not None:
            print("CSV zaten vardı -> update_rows çağrılıyor")
        branch_ui_instance.update_rows(self.logic.df)






if __name__ == "__main__":
    root = tk.Tk()
    root.tk.call("encoding","system","utf-8")
    logic = DataAnalyseLogic()
    gui = DataAnalyseGUI(root,logic)
    root.mainloop()
