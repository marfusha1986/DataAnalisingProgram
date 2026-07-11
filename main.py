import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog,ttk


class DataAnaliseApp:

    def __init__(self,window):
        self.window = window
        self.window.geometry('500x450')
        self.window.title('Data Analising Program')

        self.df=None

    #Dosya yukleme Butonu
        self.button_upload = tk.Button(window, text='Veri Seti Yükle', command=self.file_upload)
        self.button_upload.pack(pady=5)

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
            print('Veri başarıyla yüklşendi,sütunlar kutulara doldu!')

            print(self.df.head(10))

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

