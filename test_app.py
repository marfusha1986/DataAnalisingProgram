import unittest
import pandas as pd
from main import DataAnalyseGUI
from main import DataAnalyseLogic
import tkinter as tk
import os

class TestDataAnaliseApp(unittest.TestCase):

    def setUp(self):
        root = tk.Tk()
        self.logic = DataAnalyseLogic()
        self.logic.df = pd.DataFrame({
            'diagnosis':['M','B','M'],
            'radius_mean':[10.2,12.3,9.8],
            'texture_mean':[15.1,14.2,13.9]
        })
        root.withdraw()

    def test_target_selection(self):
        self.logic.df = pd.DataFrame({
            "diagnosis": ['M','B','M'],
            'radius_mean':[1,2,3]
        })

        categorical_cols = self.logic.df.select_dtypes(include=["string","object"]).columns
        self.assertIn('diagnosis',categorical_cols)

    def test_feature_selection(self):
        self.logic.df = pd.DataFrame({
            'diagnosis': ['M', 'B', 'M'],
            'radius_mean': [10.2, 12.3, 9.8],
            'texture_mean': [15.1, 14.2, 13.9]
        })
        numeric_cols = self.logic.df.select_dtypes(include=["float64","int64"]).columns
        self.assertIn('radius_mean',numeric_cols)

    def test_model_training(self):
        file_path = os.path.join(os.path.dirname(__file__),"archive/Breast_cancer_dataset.csv")
        self.logic.load_data(file_path)
        acc = self.logic.train('diagnosis',['radius_mean','texture_mean'])
        self.assertGreater(acc,0)

    def test_numeric_columns(self):
        numeric_cols = self.logic.df.select_dtypes(include=['float64','int64']).columns
        self.assertIn('radius_mean',numeric_cols)
        self.assertIn('texture_mean',numeric_cols)

    def test_categorical_columns(self):
        categorical_cols = self.logic.df.select_dtypes(include=['string','object']).columns
        self.assertIn('diagnosis',categorical_cols)

    if __name__ == '__main__':
        unittest.main()