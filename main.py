import tkinter

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
from sklearn.preprocessing import StandardScaler
import requests
import subprocess
import threading

from sklearn.preprocessing import StandardScaler

#---REFERANS ARALIKLAR TABLOSU----
REFERANCE_RANGES = {
    "sgpt": [(0,40,"normal"), (41,100,"hafif yüksek"), (101,300,"orta yüksek"), (300,9999,"ciddi yüksek")],
    "sgot": [(0,40,"normal"), (41,100,"hafif yüksek"), (101,300,"orta yüksek"), (300,9999,"ciddi yüksek")],
    "crp": [(0,5,"normal"), (6,20,"hafif yüksek"), (21,50,"orta yüksek"), (50,9999,"ciddi yüksek")],
    "albumin": [(3.5,5.5,"normal"), (0,3.49,"düşük")],
    "tot_bilirubin": [(0,1.2,"normal"), (1.3,3,"hafif yüksek"), (3,9999,"yüksek")],
    "direct_bilirubin": [(0,0.3,"normal"), (0.4,1,"hafif yüksek"), (1,9999,"yüksek")],
    "alkphos": [(40,130,"normal"), (131,300,"hafif yüksek"), (300,9999,"yüksek")],
    "tot_proteins": [(6.0,8.3,"normal"), (0,5.99,"düşük"), (8.31,9999,"yüksek")],
    "ag_ratio": [(1.0,2.2,"normal"), (0,0.99,"düşük"), (2.21,9999,"yüksek")]
}



class DataAnalyseLogic:
    def __init__(self):
        self.df = None
        self.model = None

        import shutil
        print("Ollama PATH: ",shutil.which("ollama"))

    def load_data(self, file_path):
        self.df = pd.read_csv(file_path)

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
        X = self.df[features]
        y = self.df[target]


        #---Numeric'e çevir
        X = X.apply(pd.to_numeric,errors='coerce')
        y = pd.to_numeric(y,errors='coerce')

        #---NaN satırları at---
        mask = X.notna().all(axis=1) & y.notna()
        X = X[mask]
        y = y[mask]

        #---Bos veri kontrolu--
        if len(X) == 0 or len(y) == 0:
            print("Filtre sonraı veri seti boş! Model eğitilemez.")
            return

        if self.df[target].dtype not in ["int64" ,"object","category"]:
            print("Hedef kolon sınıflandırma için uygun değil!")
            return

        #--Model Seçimi--

        if model_type == "RandomForest":
            self.model = RandomForestClassifier(n_estimators=200)
        elif model_type == "LogisticRegression":
            self.model = LogisticRegression(max_iter=2000)
        else:
            print("Bilinmeyen model türü!")
            return

        #Sadece numeric kolonları seç
        numeric_X = X.select_dtypes(include=["float64", "int64"])

        if model_type == "LogisticRegression":
            scaler = StandardScaler()
            numeric_X = scaler.fit_transform(numeric_X)
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

    def predict(self, row_index, features):
        row = self.df.iloc[row_index]
        X_row = pd.DataFrame([row[features].values],columns=features)
        return self.model.predict(X_row)[0]

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

        importances = self.model.feature_importances_
        feature_names = self.X_train.columns

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

    def classify_value(self,col_name,value):
        """
        Verilen Kolon değerini REFERANCE_RANGES tablosuna göre sınıflandırır.
        Örnek çıktı: "yuksek","hafif yüksek","düşük"
        """

        #Eğer kolon referans tablosunda yoksa sınıflandırma yapmaz
        if col_name not in REFERANCE_RANGES:
            return "Referans aralığı yok!"

        #Değer numeric'e çevir
        try:
            val = float(value)
        except:
            return "Geçersiz değer!"

        #Kolonun referans aralıklarını al
        ranges = REFERANCE_RANGES[col_name]

        #Aralıkları kontrol et
        for low,high,label in ranges:
            if low <= val <= high:
                return label
        return "sınıflandırılmadı"

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



class DataAnalyseGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x750")
        self.root.title("Data Analysing Program")

        self.logic = DataAnalyseLogic()

        #---- Sol taraf----
        self.frame_left = tk.Frame(self.root)
        self.frame_left.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)

        # ---Orta taraf----
        self.frame_center = tk.Frame(self.root)
        self.frame_center.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # ---SAĞ TARAF---
        self.frame_right = tk.Frame(self.root)
        self.frame_right.grid(row=0, column=2, sticky="nsew", pady=10, padx=10)

         # --- Root'u Responsive Yap
        self.root.grid_rowconfigure(0,weight=1)
        self.root.grid_columnconfigure(0,weight=0)
        self.root.grid_columnconfigure(1,weight=1)
        self.root.grid_columnconfigure(2,weight=2)

        #--- frame_center responsive ---
        self.frame_center.grid_rowconfigure(0,weight=1)
        self.frame_center.grid_columnconfigure(0,weight=1)

        # ---frame_right responsive yap
        for i in range(0, 8):
            self.frame_right.grid_rowconfigure(i, weight=1)

        self.frame_right.grid_columnconfigure(0, weight=1)

        # ----VERİ YÜKLEME---
        self.button_upload = tk.Button(self.frame_left, text='Veri Seti Yükle', command=self.file_upload)
        self.button_upload.grid(row=1, column=0, pady=10)

        # ---SÜTUN TİPLERİ----
        self.lbl_types = tk.Label(self.frame_left, text='Sütun Türleri:')
        self.lbl_types.grid(row=2,column=0,sticky="w")

        self.list_types = tk.Listbox(self.frame_left, height=6)
        self.list_types.grid(row=3,column=0,pady=5)

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

        self.combo_x = ttk.Combobox(self.frame_center, state="readonly")
        self.combo_x.grid(row=1, column=0, pady=5)

        self.combo_y = ttk.Combobox(self.frame_center, state="readonly")
        self.combo_y.grid(row=2, column=0, pady=5)

        #--- Renk Kolon Seçimi ---
        self.lbl_color = tk.Label(self.frame_center,text="Renk Kolonu:")
        self.lbl_color.grid(row=3,column=0,pady=5)

        self.combo_color=ttk.Combobox(self.frame_center,state='readonly')
        self.combo_color.grid(row=4,column=0,pady=5)

        #----GRAFİK ÇİZİMİ----
        self.graph_window = None

        self.lbl_plot_type = tk.Label(self.frame_center,text="Grafik Türü: ")
        self.lbl_plot_type.grid(row=5,column=0,pady=5)

        self.combo_plot_type = ttk.Combobox(self.frame_center,state="readonly",
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
        self.combo_plot_type.grid(row=6,column=0,pady=5)
        self.combo_plot_type.set('scatter') #varsayılan

        self.btn_scatter = tk.Button(self.frame_center,text="Grafik Çiz", command=self.draw_plot)
        self.btn_scatter.grid(row=7,column=0,pady=10)

        # HEDEF KOLON
        self.lbl_target = tk.Label(self.frame_center, text='Hedef Kolon (Label):')
        self.lbl_target.grid(row=8, column=0, pady=5)

        self.combo_target = ttk.Combobox(self.frame_center)
        self.combo_target.grid(row=9, column=0, pady=5)

        #Model Seçimi
        self.lbl_model = tk.Label(self.frame_center,text="Model Türü:")
        self.lbl_model.grid(row=10,column=0,pady=5)

        self.combo_model = ttk.Combobox(
            self.frame_center,
            state="readonly",
            values=["RandomForest","LogisticRegression"]
        )
        self.combo_model.grid(row=11,column=0,pady=5)
        self.combo_model.set("RandomForest")

        # ÖZELLİK KOLONLARI
        self.lbl_features = tk.Label(self.frame_center, text='Özellik Kolonları (Features):')
        self.lbl_features.grid(row=12, column=0, pady=5)

        self.list_features = tk.Listbox(self.frame_center, selectmode='multiple', height=10)
        self.list_features.grid(row=13, column=0, pady=5)

        self.lbl_score = tk.Label(self.frame_center, text="Henüz model eğitilmedi!")
        self.lbl_score.grid(row=14, column=0, pady=5)

        # ---MODEL EĞİTME---
        self.button_train = tk.Button(self.frame_center, text='Modeli Eğit', command=self.train_model)
        self.button_train.grid(row=15, column=0, pady=10)

        # ---TAHMİN---
        self.button_predict = tk.Button(self.frame_center, text='Tahmin Yap', command=self.predict_row)
        self.button_predict.grid(row=16,column=0,pady=10)


        #--- BASİT FİLTRELEME---
        self.lbl_filter = tk.Label(self.frame_right,text="Veri Filtreleme:")
        self.lbl_filter.grid(row=1,column=0,pady=5)

        self.combo_filter_col = ttk.Combobox(self.frame_right,state="readonly")
        self.combo_filter_col.grid(row=2,column=0,pady=5)

        self.combo_filter_op = ttk.Combobox(self.frame_right,state="readonly",
                                            values=["<",">",">=","<=","==","!="])
        self.combo_filter_op.grid(row=3,column=0,pady=5)
        self.combo_filter_op.set("==")

        self.entry_filter_value = tk.Entry(self.frame_right)
        self.entry_filter_value.grid(row=4,column=0,pady=5)

        #Filtreleme düğmesi
        self.btn_apply_filter = tk.Button(self.frame_right,text="Filtre Uygula",command=self.apply_filter_button)
        self.btn_apply_filter.grid(row=5,column=0,pady=5)

        # --- AI Yorum Kutusu ---
        self.ai_frame = tk.Frame(self.frame_right)
        self.ai_frame.grid(row=6,column=0,padx=10,pady=10)

        self.ai_textbox = tk.Text(self.ai_frame, height=10,width=40,wrap="word")
        self.ai_textbox.pack(side="left",fill="both",expand=True)

        ai_textbox_scrollbar = tk.Scrollbar(self.ai_frame,command=self.ai_textbox.yview)
        ai_textbox_scrollbar.pack(side="right",fill="y")

        self.ai_textbox.config(yscrollcommand=ai_textbox_scrollbar.set)

        self.btn_clear_filter = tk.Button(self.frame_right,text="Filtreyi Kaldır",command=self.clear_filter_gui)
        self.btn_clear_filter.grid(row=7,column=0,columnspan=3,pady=5)



    def file_upload(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        columns = self.logic.load_data(file_path)
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

        self.lbl_score.config(text=f"Model Başarı Oranı: {accuracy:.2f}")
        print(f"Model Başarı oranı: {accuracy:.2f}")

        if self.logic.df is None or len(self.logic.df) == 0:
            return

        summary = self.generate_full_summary()
        self.ask_ai_async(summary)

    def predict_row(self):
        if self.logic.model is None:
            print("Lütfen önce modeli eğitin!")
            return
        try:
            row_index = simpledialog.askinteger("Satır seç", "Tahmin yapılacak satır:")
            if row_index is None:
                return

            if row_index < 0 or row_index >= len(self.logic.df):
                print("Geçersiz satır numarası!")
                return

            features = [self.list_features.get(i) for i in self.list_features.curselection()]
            if not features:
                print("Lütfen en az bir özellik kolon seçin!")
                return

            prediction = self.logic.predict(row_index, features)
            print("Tahmin: ", prediction)

        except Exception as e:
            print("Tahmin sırasında hata oluştu: ",e)

        if self.logic.df is None or len(self.logic.df) == 0:
            return

        summary = self.generate_full_summary()
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

        if not pd.api.types.is_numeric_dtype(self.logic.df[col]):
            print("Bu kolon sayısal değil,filtre uygulanamaz!")
            return

        self.logic.apply_filter(col,op,value)
        print("Filtre uygulandı.")

        if self.logic.df is None or len(self.logic.df) == 0:
            return

        summary = self.generate_full_summary()
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

        #---FEATURE_IMPORTANCE varsa ekle ----
        if self.logic.model is not None and hasattr(self.logic.model,"feature_importances_"):
            summary += "\n Feature Importance:\n"
            fi = self.logic.feature_importance()
            for k,v in fi.items():
                summary += f" - {k}: {v} \n"

        summary += "\n"

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

        summary = summary[:3000]

        summary += (
            "\n=== BAĞLAM SIFIRLAMA===\n"
            "Bu analiz tamamen bağımsızdır.Önceki analizlerle bağlantı kurma."
            "Bu veri setini tek başına değerlendir."
        )
        return summary


    def ask_ai_async(self,text):
        thread = threading.Thread(target=self.ask_ai_worker,args=(text,))
        thread.start()

    def ask_ai_worker(self,text):
        process = subprocess.Popen(
            ["python","ai_worker.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore"

        )

        ai_response,ai_error= process.communicate(input=text)

        #--- GUI güncellemesini ana thread'e yaz ---
        self.ai_textbox.after(0, lambda: self.update_ai_textbox(ai_response))

    def update_ai_textbox(self,ai_response):
        self.ai_textbox.delete("1.0","end")
        try:
            self.ai_textbox.insert("end",ai_response)
        except Exception:
            safe_text = ai_response.encode("utf-8","ignore").decode("utf-8","ignore")
            self.ai_textbox.insert("end",safe_text)
    def clear_filter_gui(self):
        print("Filtre kaldırıldı,veri yeniden yüklendi!")
        self.logic.df = self.logic.df_original.copy()

        self.ask_ai_async(self.generate_full_summary())

if __name__ == "__main__":
    root = tk.Tk()
    root.tk.call("encoding","system","utf-8")

    app = DataAnalyseGUI(root)
    root.mainloop()
