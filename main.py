import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


class DataAnalyseLogic:
    def __init__(self):
        self.df = None
        self.model = None

    def load_data(self, file_path):
        self.df = pd.read_csv(file_path)
        # Unnamed kolonları temizle
        self.df = self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]
        self.df = self.df.convert_dtypes()
        return list(self.df.columns)


    def train(self, target, features):
        X = self.df[features]
        y = self.df[target]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = RandomForestClassifier(n_estimators=200)
        self.model.fit(X_train, y_train)
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

        plt.figure(figsize=(12, 8))
        sns.heatmap(corr, annot=False, cmap='coolwarm')
        plt.title('Korelasyon Matrisi Heatmap')
        plt.show()

    def plot_scatter(self,x_col,y_col,color_col=None):
        plt.figure(figsize=(6,4))
        #Eğer renk kolonunu seçmişse ve kolon kategorikse
        if color_col and color_col in self.df.columns:
            unique_vals = self.df[color_col].unique()

            for val in unique_vals:
                subset = self.df[self.df[color_col] == val]
                plt.scatter(subset[x_col],subset[y_col],label=str(val))
            plt.legend()
        else:
            plt.scatter(self.df[x_col],self.df[y_col])

        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"{x_col} vs {y_col}")
        plt.show()

    def plot_line(self,x_col,y_col):
        plt.figure(figsize=(6,4))
        plt.plot(self.df[x_col],self.df[y_col])
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"{x_col} vs {y_col} (Line Plot)")
        plt.show()

    def plot_box(self,col):
        plt.figure(figsize=(6,4))
        plt.boxplot(self.df[col])
        plt.title(f"{col} Boxplot")
        plt.show()

    def plot_hist(self,x_col,bins=30):
        if not pd.api.types.is_numeric_dtype(self.df[x_col]):
            print(f"{x_col} kolonunun tipi sayısal değil,histogram çizilemez!")
            return

        plt.figure(figsize=(6,4))
        plt.hist(self.df[x_col],bins=bins,color='skyblue',edgecolor='black')
        plt.xlabel(x_col)
        plt.ylabel("Frekans")
        plt.title(f"{x_col} Histogram")
        plt.show()

    def get_numeric_columns(self):
        return list(self.df.select_dtypes(include=['float64','int64']).columns)

    def get_categorical_columns(self):
        return list(self.df.select_dtypes(include=["string","object"]).columns)


class DataAnalyseGUI:
    def __init__(self, root):
        self.window = root
        self.window.geometry("800x750")
        self.window.title("Data Analysing Program")

        self.logic = DataAnalyseLogic()

        #---- Sol taraf----
        self.frame_left = tk.Frame(self.window)
        self.frame_left.pack(side="left",fill="y",padx=10,pady=10)

        # ----VERİ YÜKLEME---
        self.button_upload = tk.Button(self.frame_left, text='Veri Seti Yükle', command=self.file_upload)
        self.button_upload.grid(row=0, column=0, pady=10)

        # ---SÜTUN TİPLERİ----
        self.lbl_types = tk.Label(self.frame_left, text='Sütun Türleri:')
        self.lbl_types.grid(row=1,column=0,sticky="w")

        self.list_types = tk.Listbox(self.frame_left, height=6)
        self.list_types.grid(row=2,column=0,pady=5)

        self.button_null = tk.Button(self.frame_left, text='Eksik Değer Analizi', command=self.null_analysis_gui)
        self.button_null.grid(row=3, column=0, pady=10)


        # ---EKSİK DEĞER DOLDURMA----
        self.lbl_fill = tk.Label(self.frame_left, text='Eksik Değer Doldurma:')
        self.lbl_fill.grid(row=4,column=0,pady=5)

        self.combo_fill_col = ttk.Combobox(self.frame_left,state="readonly")
        self.combo_fill_col.grid(row=5,column=0,pady=5)

        self.combo_fill_type = ttk.Combobox(self.frame_left, values=['mean', 'median', 'mode'])
        self.combo_fill_type.set('mean')
        self.combo_fill_type.grid(row=6,column=0,pady=5)

        self.button_fill = tk.Button(self.frame_left, text='Eksik Değer Doldur', command=self.fill_nulls_gui)
        self.button_fill.grid(row=7, column=0, pady=10)

        # ---KORELASYON MATRİSİ---
        self.button_corr = tk.Button(self.frame_left, text='Korelasyon Matrisi (Heatmap)', command=self.show_corr_gui)
        self.button_corr.grid(row=8, column=0, pady=10)


        #---Sağ taraf----
        self.frame_right = tk.Frame(self.window)
        self.frame_right.pack(side="right",fill="y",padx=10,pady=10)

        self.combo_x = ttk.Combobox(self.frame_right, state="readonly")
        self.combo_x.grid(row=0, column=0, pady=5)

        self.combo_y = ttk.Combobox(self.frame_right, state="readonly")
        self.combo_y.grid(row=1, column=0, pady=5)

        #--- Renk Kolon Seçimi ---
        self.lbl_color = tk.Label(self.frame_right,text="Renk Kolonu:")
        self.lbl_color.grid(row=2,column=0,pady=5)

        self.combo_color=ttk.Combobox(self.frame_right,state='readonly')
        self.combo_color.grid(row=3,column=0,pady=5)

        #----GRAFİK ÇİZİMİ----
        self.lbl_plot_type = tk.Label(self.frame_right,text="Grafik Türü: ")
        self.lbl_plot_type.grid(row=4,column=0,pady=5)

        self.combo_plot_type = ttk.Combobox(self.frame_right,state="readonly",
                                            values=['scatter','line','boxplot','histogram'])
        self.combo_plot_type.grid(row=5,column=0,pady=5)
        self.combo_plot_type.set('scatter') #varsayılan

        self.btn_scatter = tk.Button(self.frame_right,text="Grafik Çiz", command=self.draw_plot)
        self.btn_scatter.grid(row=6,column=0,pady=10)

        # HEDEF KOLON
        self.lbl_target = tk.Label(self.frame_right, text='Hedef Kolon (Label):')
        self.lbl_target.grid(row=7, column=0, pady=5)

        self.combo_target = ttk.Combobox(self.frame_right)
        self.combo_target.grid(row=8, column=0, pady=5)

        # ÖZELLİK KOLONLARI
        self.lbl_features = tk.Label(self.frame_right, text='Özellik Kolonları (Features):')
        self.lbl_features.grid(row=9, column=0, pady=5)

        self.list_features = tk.Listbox(self.frame_right, selectmode='multiple', height=10)
        self.list_features.grid(row=10, column=0, pady=5)

        self.lbl_score = tk.Label(self.frame_right, text="Henüz model eğitilmedi!")
        self.lbl_score.grid(row=11, column=0, pady=5)

        # ---MODEL EĞİTME---
        self.button_train = tk.Button(self.frame_right, text='Modeli Eğit', command=self.train_model)
        self.button_train.grid(row=12, column=0, pady=10)

        # ---TAHMİN---
        self.button_predict = tk.Button(self.frame_right, text='Tahmin Yap', command=self.predict_row)
        self.button_predict.grid(row=13,column=0,pady=10)

    def file_upload(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        columns = self.logic.load_data(file_path)
        # ---Target sadece kategorik kolonlar---
        categorical_cols = self.logic.df.select_dtypes(include=['object','string']).columns
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

    def train_model(self):
        target = self.combo_target.get()
        if target == "":
            print("Lütfen hedef kolon seçin!")
            return

        features = [self.list_features.get(i) for i in self.list_features.curselection()]
        if not features:
            print("Lütfen en az bir özellik kolon seçin!")
            return

        accuracy = self.logic.train(target, features)
        self.lbl_score.config(text=f"Model Başarı Oranı: {accuracy:.2f}")
        print(f"Model Başarı oranı: {accuracy:.2f}")

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

    def null_analysis_gui(self):
        self.logic.null_analysis()

    def show_corr_gui(self):
        self.logic.show_corr()

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

        self.logic.df[col] = self.logic.df[col].fillna(value)
        print(f"{col} kolonundaki eksik değerler '{method}' ile dolduruldu.")

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

        if plot_type == "scatter":
            self.logic.plot_scatter(x,y,color)
        elif plot_type == "line":
            self.logic.plot_line(x,y)
        elif plot_type == "boxplot":
            self.logic.plot_box(x)
        elif plot_type == "histogram":
            self.logic.plot_hist(x)

if __name__ == "__main__":
    root = tk.Tk()
    app = DataAnalyseGUI(root)
    root.mainloop()
