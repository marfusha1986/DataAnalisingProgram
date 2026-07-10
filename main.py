import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk


class DataAnaliseApp:

    def __init__(self,window):
        self.window = window
        self.window.geometry('500x400')
        self.window.title('Data Analising Program')

        self.df=None

        button_upload = tk.Button(window, text='Veri Seti Yükle', command=self.file_upload)
        button_upload.pack(pady=5)

        # X ekseni için
        lbl_x = tk.Label(window, text='X Ekseni Seçin: ')
        lbl_x.pack()
        self.combo_x = ttk.Combobox(window)
        self.combo_x.pack()

        # Y ekseni için
        lbl_y = tk.Label(window, text='Y Ekseni Seçin: ')
        lbl_y.pack()
        self.combo_y = ttk.Combobox(window)
        self.combo_y.pack()

        button_graphic = tk.Button(window, text='Grafik çiz', command=self.graphic)
        button_graphic.pack(pady=5)


    def file_upload(self):
        file_path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])

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

        if chosen_x != '' and chosen_y != '':
            sns.scatterplot(data=self.df, x=chosen_x, y=chosen_y, hue='diagnosis', palette='Set1', alpha=0.8)
            plt.xlabel(chosen_x)
            plt.ylabel(chosen_y)
            plt.title(f'{chosen_x} ve {chosen_y} İlişkisi')
            plt.show()
        else:
            print('Lutfen grafiği çizdirmek için X ve Y eksenlerini seçip butona tekrar basın!')


if __name__ == '__main__':
    root = tk.Tk()
    app = DataAnaliseApp(root)
    root.mainloop()

