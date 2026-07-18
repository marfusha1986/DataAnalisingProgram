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


class DataAnalyseGUI:
    def __init__(self, root):
        self.window = root
        self.window.geometry("800x750")
        self.window.title("Data Analysing Program")

        self.logic = DataAnalyseLogic()

        # VERİ YÜKLEME
        self.button_upload = tk.Button(self.window, text='Veri Seti Yükle', command=self.file_upload)
        self.button_upload.pack(pady=10)

        # SÜTUN TİPLERİ
        self.lbl_types = tk.Label(self.window, text='Sütun Türleri:')
        self.lbl_types.pack()
        self.list_types = tk.Listbox(self.window, height=6)
        self.list_types.pack(pady=5)

        # EKSİK DEĞER ANALİZİ
        self.button_null = tk.Button(self.window, text='Eksik Değer Analizi', command=self.null_analysis_gui)
        self.button_null.pack(pady=10)

        # EKSİK DEĞER DOLDURMA
        self.lbl_fill = tk.Label(self.window, text='Eksik Değer Doldurma:')
        self.lbl_fill.pack()

        self.combo_fill_col = ttk.Combobox(self.window)
        self.combo_fill_col.pack(pady=3)

        self.combo_fill_type = ttk.Combobox(self.window, values=['mean', 'median', 'mode'])
        self.combo_fill_type.set('mean')
        self.combo_fill_type.pack()

        self.button_fill = tk.Button(self.window, text='Eksik Değer Doldur', command=self.fill_nulls_gui)
        self.button_fill.pack(pady=10)

        # KORELASYON MATRİSİ
        self.button_corr = tk.Button(self.window, text='Korelasyon Matrisi (Heatmap)', command=self.show_corr_gui)
        self.button_corr.pack(pady=10)

        # HEDEF KOLON
        self.lbl_target = tk.Label(self.window, text='Hedef Kolon (Label):')
        self.lbl_target.pack()
        self.combo_target = ttk.Combobox(self.window)
        self.combo_target.pack(pady=3)

        # ÖZELLİK KOLONLARI
        self.lbl_features = tk.Label(self.window, text='Özellik Kolonları (Features):')
        self.lbl_features.pack()
        self.list_features = tk.Listbox(self.window, selectmode='multiple', height=10)
        self.list_features.pack(pady=3)

        # MODEL EĞİTME
        self.button_train = tk.Button(self.window, text='Modeli Eğit', command=self.train_model)
        self.button_train.pack(pady=10)

        # TAHMİN
        self.button_predict = tk.Button(self.window, text='Tahmin Yap', command=self.predict_row)
        self.button_predict.pack(pady=10)

        self.lbl_score = tk.Label(self.window,text="Henüz model eğitilmedi!")
        self.lbl_score.pack()

    def file_upload(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        columns = self.logic.load_data(file_path)
        # Target sadece kategorik kolonlar
        categorical_cols = self.logic.df.select_dtypes(include=['object','string']).columns
        self.combo_target['values'] = list(categorical_cols)

        # Feature listesine sadece sayısal kolonlar
        numeric_cols = self.logic.df.select_dtypes(include=['float64', 'int64']).columns
        self.list_features.delete(0, tk.END)
        for col in numeric_cols:
            self.list_features.insert(tk.END, col)

        # Eksik değer doldurma kolonları
        self.combo_fill_col['values'] = columns

        # Sütun tipleri
        self.list_types.delete(0, tk.END)
        for col, dtype in self.logic.df.dtypes.items():
            self.list_types.insert(tk.END, f"{col} ---> {dtype}")

        print("Veri başarıyla yüklendi, sütunlar kutulara doldu!")

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

        if method == "mean":
            value = self.logic.df[col].mean()
        elif method == "median":
            value = self.logic.df[col].median()
        else:
            value = self.logic.df[col].mode()[0]

        self.logic.df[col] = self.logic.df[col].fillna(value)
        print(f"{col} kolonundaki eksik değerler '{method}' ile dolduruldu.")


if __name__ == "__main__":
    root = tk.Tk()
    app = DataAnalyseGUI(root)
    root.mainloop()
