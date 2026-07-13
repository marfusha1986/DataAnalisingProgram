import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog,ttk


class DataAnaliseApp:

    def __init__(self,window):
        self.window = window
        self.window.geometry('800x750')
        self.window.title('Data Analising Program')

        self.df=None

    #Dosya yukleme Butonu
        self.button_upload = tk.Button(window, text='Veri Seti Yükle', command=self.file_upload)
        self.button_upload.pack(pady=5)

        self.lbl_types = tk.Label(self.window, text='Sütun Türleri: ')
        self.lbl_types.pack()

        self.list_types = tk.Listbox(self.window, height=6)
        self.list_types.pack(pady=5)

        self.button_null = tk.Button(self.window, text='Eksik Değer Analizi',command=self.null_analises)
        self.button_null.pack(pady=5)

        self.lbl_fill = tk.Label(self.window,text='Eksik Değer Doldurma: ')
        self.lbl_fill.pack()

        #Kolon seçimi
        self.combo_fill_col = ttk.Combobox(self.window)
        self.combo_fill_col.pack(pady=3)

        #Doldurma Türü seçimi
        self.combo_fill_type =ttk.Combobox(self.window)
        self.combo_fill_type['values'] = ['mean','median','mode']
        self.combo_fill_type.set('mean') #Varsayılan
        self.combo_fill_type.pack()

        #Doldurma butonu
        self.button_fill =tk.Button(self.window,text='Eksik Değer Doldur',command=self.fill_nulls)
        self.button_fill.pack(pady=5)

        #Korelasyon matrisi butonu
        self.button_corr=tk.Button(self.window,text='Korelasyon Matrisi (Heatmap)',command=self.show_corr)
        self.button_corr.pack(pady=5)

        # X ekseni için
        self.lbl_x = tk.Label(self.window, text='X Ekseni Seçin: ')
        self.lbl_x.pack()
        self.combo_x = ttk.Combobox(self.window)
        self.combo_x.pack()

        # Y ekseni için
        self.lbl_y = tk.Label(self.window, text='Y Ekseni Seçin: ')
        self.lbl_y.pack()
        self.combo_y = ttk.Combobox(self.window)
        self.combo_y.pack()

#Grafik Türü Seçimi
        self.lbl_tur = tk.Label(self.window,text='Grafik Türü Seçin: ')
        self.lbl_tur.pack()
        self.combo_tur = ttk.Combobox(self.window)



        #Kullanıcıya Seçenek Sunalım
        self.combo_tur['values'] = [
            'Saçılım Grafiği (Scatter)',
            'Çizgi Grafiği (Line)',
            'Kutu Grafiği (Boxplot)'
        ]
        self.combo_tur.set('Saçılım Grafiği (Scatter)') #Varsayılan seçim
        self.combo_tur.pack()
        #============================================

        #Grafik çizme butonu
        self.button_graphic = tk.Button(self.window, text='Grafik çiz', command=self.graphic)
        self.button_graphic.pack(pady=10)


    def file_upload(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('CSV Files', '*.csv')]
        )

        if file_path:
            self.df = pd.read_csv(file_path)
            columns = list(self.df.columns)

            self.combo_x['values']=columns
            self.combo_y['values']=columns
            self.combo_fill_col['values']=columns
            print('Veri başarıyla yüklşendi,sütunlar kutulara doldu!')

            self.df = self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]

        print(self.df.head(10))
        self.list_types.delete(0,tk.END)
        for col,dtype in self.df.dtypes.items():
            self.list_types.insert(tk.END,f'{col}  ---> {dtype}')

    def null_analises(self):
        if self.df is None:
            print('Lütfen önce veri yükleyin!')
            return

        nulls =self.df.isnull().sum()

        print('\n --- Eksik Değer Analizi ---')
        for col,count in nulls.items():
            print(f'{col}: {count} adet eksik değer')
        print('---------------------------------------------')


    def fill_nulls(self):
        if self.df is None:
            print('Lütfen önce veri yükleyin!')
            return

        col = self.combo_fill_col.get()
        method = self.combo_fill_type.get()

        if col =='':
            print('Lütfen bir kolon seçin!')
            return

        if method == 'mean':
            value = self.df[col].mean()
        elif method == 'median':
            value = self.df[col].median()
        elif method == 'mode':
            value = self.df[col].mode()[0]

        #Doldurma işlemi:
        self.df[col] = self.df[col].fillna(value)
        print(f"{col} kolonundaki eksik değerler '{method}' yöntemiyle dolduruldu.")

    def show_corr(self):
        if self.df is None:
            print('Lütfen önce veri yükleyin!')
            return

        #Sadece sayısal kolonları al
        numeric_df = self.df.select_dtypes(include=['float64','int64'])

        #Korelasyon matrisi
        corr = numeric_df.corr()

        #Heatmap çizimi
        plt.figure(figsize=(12,8))
        sns.heatmap(corr,annot=False,cmap='coolwarm')
        plt.title('Korelasyon Matrisi Heatmap')
        plt.show()

    def graphic(self):
        if self.df is None:
            print('Lütfen önce bir veri seti yükleyin!')
            return

        chosen_x=self.combo_x.get()
        chosen_y=self.combo_y.get()
        chosen_tur = self.combo_tur.get()

        if chosen_x != '' and chosen_y != '':
            plt.figure(figsize=(8,5))

            #Grafik türü kontrolu
            if chosen_tur == 'Saçılım Grafiği (Scatter)':
                sns.scatterplot(
                    data=self.df,
                    x=chosen_x,
                    y=chosen_y,
                    hue='diagnosis',
                    palette='Set1',
                    alpha=0.8)
            elif chosen_tur == 'Çizgi Grafiği (Line)':
                sns.lineplot(
                    data=self.df,
                    x=chosen_x,
                    y=chosen_y,
                    hue='diagnosis',
                    palette='Set1',
                    errorbar=None
                )
            elif chosen_tur == 'Kutu Grafiği (Boxplot)':
                sns.boxplot(
                    data=self.df,
                    x=chosen_x,
                    y=chosen_y,
                    hue='diagnosis',
                    palette='Set1'

                )
            #==========================================
            plt.xlabel(chosen_x)
            plt.ylabel(chosen_y)
            plt.title(f'{chosen_tur} : {chosen_x} ve {chosen_y} İlişkisi')
            plt.show()
        else:
            print('Lutfen grafiği çizdirmek için X ve Y eksenlerini seçip butona tekrar basın!')


if __name__ == '__main__':
    root = tk.Tk()
    app = DataAnaliseApp(root)
    root.mainloop()

