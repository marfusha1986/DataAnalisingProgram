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
import sys
import threading
from googletrans import Translator
from sklearn.preprocessing import StandardScaler

#---REFERANS ARALIKLAR TABLOSU----

REFERENCE_RANGES = {
    "internal_medicine": {
        # Karaciğer Fonksiyonları
        "sgpt": [(0,40,"normal"), (41,100,"hafif yüksek"), (101,300,"orta yüksek"), (300,9999,"ciddi yüksek")],
        "sgot": [(0,40,"normal"), (41,100,"hafif yüksek"), (101,300,"orta yüksek"), (300,9999,"ciddi yüksek")],
        "alkphos": [(40,130,"normal"), (131,300,"hafif yüksek"), (300,9999,"yüksek")],
        "tot_bilirubin": [(0,1.2,"normal"), (1.3,3,"hafif yüksek"), (3,9999,"yüksek")],
        "direct_bilirubin": [(0,0.3,"normal"), (0.4,1,"hafif yüksek"), (1,9999,"yüksek")],
        "albumin": [(3.5,5.5,"normal"), (0,3.49,"düşük")],
        "tot_proteins": [(6.0,8.3,"normal"), (0,5.99,"düşük"), (8.31,9999,"yüksek")],
        "ag_ratio": [(1.0,2.2,"normal"), (0,0.99,"düşük"), (2.21,9999,"yüksek")],

        # Böbrek Fonksiyonları
        "urea": [(10,50,"normal"), (51,100,"hafif yüksek"), (101,9999,"yüksek")],
        "creatinine": [(0.6,1.3,"normal"), (1.4,2.0,"hafif yüksek"), (2.1,9999,"yüksek")],
        "gfr": [(90,9999,"normal"), (60,89,"hafif düşük"), (30,59,"orta düşük"), (0,29,"ciddi düşük")],

        # Kan Şekeri ve Metabolizma
        "glucose": [(70,99,"normal"), (100,125,"prediyabet"), (126,9999,"diyabet")],
        "hba1c": [(4.0,5.6,"normal"), (5.7,6.4,"prediyabet"), (6.5,9999,"diyabet")],
        "insulin": [(2,25,"normal"), (26,9999,"yüksek")],
        "homa_ir": [(0,2,"normal"), (2.1,2.9,"hafif yüksek"), (3,9999,"insülin direnci")],

        # Elektrolitler
        "sodium": [(135,145,"normal"), (146,160,"yüksek"), (0,134,"düşük")],
        "potassium": [(3.5,5.0,"normal"), (5.1,6.0,"hafif yüksek"), (6.1,9999,"ciddi yüksek")],
        "chloride": [(98,106,"normal"), (107,120,"yüksek"), (0,97,"düşük")],
        "calcium": [(8.5,10.5,"normal"), (10.6,12,"hafif yüksek"), (12.1,9999,"ciddi yüksek")],
        "phosphorus": [(2.5,4.5,"normal"), (4.6,9999,"yüksek"), (0,2.4,"düşük")],
        "magnesium": [(1.7,2.2,"normal"), (2.3,9999,"yüksek"), (0,1.6,"düşük")],

        # Tiroid Fonksiyonları
        "tsh": [(0.4,4.0,"normal"), (4.1,10,"hafif yüksek"), (10.1,9999,"ciddi yüksek")],
        "ft4": [(0.8,1.8,"normal"), (0,0.79,"düşük"), (1.81,9999,"yüksek")],
        "ft3": [(2.3,4.2,"normal"), (0,2.29,"düşük"), (4.21,9999,"yüksek")],

        # Vitamin ve Mineral Paneli
        "vitamin_d": [(30,100,"normal"), (20,29,"hafif düşük"), (0,19,"ciddi düşük")],
        "b12": [(200,900,"normal"), (0,199,"düşük"), (901,9999,"yüksek")],
        "folate": [(3,17,"normal"), (0,2.9,"düşük")],
        "iron": [(60,170,"normal"), (0,59,"düşük"), (171,9999,"yüksek")],
        "ferritin": [(30,400,"normal"), (0,29,"düşük"), (401,9999,"yüksek")],

        # Lipid Paneli
        "cholesterol_total": [(0,200,"normal"), (201,239,"hafif yüksek"), (240,9999,"yüksek")],
        "ldl": [(0,100,"optimal"), (101,129,"iyi"), (130,159,"sınır yüksek"), (160,189,"yüksek"), (190,9999,"çok yüksek")],
        "hdl": [(60,9999,"iyi"), (40,59,"orta"), (0,39,"düşük")],
        "triglycerides": [(0,150,"normal"), (151,199,"hafif yüksek"), (200,499,"yüksek"), (500,9999,"çok yüksek")]
    },
    "cardiology":{
    # Kalp Enzimleri
        "troponin_i": [
        (0, 0.04, "normal"),
        (0.05, 0.39, "hafif yüksek"),
        (0.40, 9999, "ciddi yüksek")
        ],
        "troponin_t": [
        (0, 0.01, "normal"),
        (0.02, 0.09, "hafif yüksek"),
        (0.10, 9999, "ciddi yüksek")
        ],
        "ck_mb": [
        (0, 5, "normal"),
        (6, 24, "hafif yüksek"),
        (25, 9999, "ciddi yüksek")
        ],
         "myoglobin": [
        (0, 85, "normal"),
        (86, 9999, "yüksek")
        ],

         # Kalp Yetmezliği Belirteçleri
        "bnp": [
        (0, 100, "normal"),
        (101, 300, "hafif yüksek"),
        (301, 9999, "ciddi yüksek")
        ],
        "nt_pro_bnp": [
        (0, 125, "normal"),
        (126, 450, "hafif yüksek"),
        (451, 9999, "ciddi yüksek")
        ],

        # Pıhtılaşma ve Tromboz
        "d_dimer": [
        (0, 0.5, "normal"),
        (0.51, 1.0, "hafif yüksek"),
        (1.01, 9999, "ciddi yüksek")
        ],

        # Lipid Paneli (kardiyoloji için yeniden bağlanıyor)
        "cholesterol_total": [
        (0, 200, "normal"),
        (201, 239, "hafif yüksek"),
        (240, 9999, "yüksek")
        ],
        "ldl": [
        (0, 100, "optimal"),
        (101, 129, "iyi"),
        (130, 159, "sınır yüksek"),
        (160, 189, "yüksek"),
        (190, 9999, "çok yüksek")
        ],
        "hdl": [
        (60, 9999, "iyi"),
        (40, 59, "orta"),
        (0, 39, "düşük")
        ],
        "triglycerides": [
        (0, 150, "normal"),
        (151, 199, "hafif yüksek"),
        (200, 499, "yüksek"),
        (500, 9999, "çok yüksek")
        ],

         # Kas Enzimleri (kardiyak olmayan ama kardiyolojiye bağlı)
        "ck_total": [
        (0, 200, "normal"),
        (201, 9999, "yüksek")
        ]


    },
    "endocrinology":{

     # Tiroid Fonksiyonları
        "tsh": [
        (0.4, 4.0, "normal"),
        (4.1, 10, "hafif yüksek"),
        (10.1, 9999, "ciddi yüksek")
        ],
        "ft4": [
        (0.8, 1.8, "normal"),
        (0, 0.79, "düşük"),
        (1.81, 9999, "yüksek")
        ],
        "ft3": [
        (2.3, 4.2, "normal"),
        (0, 2.29, "düşük"),
        (4.21, 9999, "yüksek")
        ],

        # Diyabet ve Metabolizma
         "glucose_fasting": [
        (70, 99, "normal"),
        (100, 125, "prediyabet"),
        (126, 9999, "diyabet")
        ],
        "glucose_pp": [
        (70, 140, "normal"),
        (141, 199, "prediyabet"),
        (200, 9999, "diyabet")
        ],
        "hba1c": [
        (4.0, 5.6, "normal"),
        (5.7, 6.4, "prediyabet"),
        (6.5, 9999, "diyabet")
         ],
        "insulin": [
        (2, 25, "normal"),
        (26, 9999, "yüksek")
        ],
        "homa_ir": [
        (0, 2, "normal"),
        (2.1, 2.9, "hafif yüksek"),
        (3, 9999, "insülin direnci")
        ],

        # Adrenal Bez (Böbrek Üstü)
        "cortisol_morning": [
        (6, 23, "normal"),
        (0, 5.9, "düşük"),
        (24, 9999, "yüksek")
        ],
        "acth": [
        (10, 60, "normal"),
        (0, 9.9, "düşük"),
        (61, 9999, "yüksek")
        ],
        "dhea_s": [
        (35, 430, "normal"),
        (0, 34, "düşük"),
        (431, 9999, "yüksek")
        ],

        # Kadın Hormonları
        "estradiol": [
        (30, 400, "normal"),
        (0, 29, "düşük"),
        (401, 9999, "yüksek")
        ],
        "progesterone": [
        (5, 20, "normal (luteal)"),
        (0, 4.9, "düşük"),
        (21, 9999, "yüksek")
        ],
        "fsh": [
        (3, 10, "normal"),
        (11, 20, "hafif yüksek"),
        (21, 9999, "ciddi yüksek")
        ],
        "lh": [
        (2, 12, "normal"),
        (13, 9999, "yüksek")
        ],

        # Erkek Hormonları
        "testosterone_total": [
        (300, 1000, "normal"),
        (0, 299, "düşük"),
        (1001, 9999, "yüksek")
        ],
        "testosterone_free": [
        (5, 25, "normal"),
        (0, 4.9, "düşük"),
        (26, 9999, "yüksek")
        ],

         # Prolaktin
        "prolactin": [
        (4, 15, "normal"),
        (16, 25, "hafif yüksek"),
        (26, 9999, "ciddi yüksek")
         ]


    },

    "hematology":{

        # Beyaz Kan Hücreleri (Enfeksiyon / Lösemi)
        "wbc": [
        (4.0, 11.0, "normal"),
        (11.1, 15.0, "hafif yüksek"),
        (15.1, 9999, "ciddi yüksek"),
        (0, 3.9, "düşük")
        ],

        # Kırmızı Kan Hücreleri
        "rbc": [
        (4.5, 6.0, "normal"),
        (0, 4.49, "düşük"),
        (6.01, 9999, "yüksek")
        ],

        # Hemoglobin
        "hgb": [
        (13.5, 17.5, "normal"),
        (0, 13.49, "düşük"),
        (17.6, 9999, "yüksek")
        ],

        # Hematokrit
        "hct": [
        (38, 50, "normal"),
        (0, 37.9, "düşük"),
        (50.1, 9999, "yüksek")
        ],

        # Trombositler
        "plt": [
        (150, 450, "normal"),
        (0, 149, "düşük"),
        (451, 9999, "yüksek")
        ],

         # RDW (Kırmızı Hücre Dağılım Genişliği)
        "rdw": [
        (11.5, 14.5, "normal"),
        (14.6, 9999, "yüksek")
        ],

        # MCV (Ortalama Eritrosit Hacmi)
        "mcv": [
        (80, 100, "normal"),
        (0, 79, "mikrositik"),
        (101, 9999, "makrositik")
        ],

        # MCH (Ortalama Hemoglobin İçeriği)
        "mch": [
        (27, 33, "normal"),
        (0, 26.9, "düşük"),
        (33.1, 9999, "yüksek")
        ],

        # MCHC (Hemoglobin Konsantrasyonu)
        "mchc": [
        (32, 36, "normal"),
        (0, 31.9, "düşük"),
        (36.1, 9999, "yüksek")
        ],

        # Pıhtılaşma Testleri
        "inr": [
        (0.8, 1.2, "normal"),
        (1.3, 2.0, "hafif yüksek"),
        (2.1, 9999, "ciddi yüksek")
        ],
        "aptt": [
        (25, 35, "normal"),
        (36, 9999, "uzamış")
        ],
        "fibrinogen": [
        (200, 400, "normal"),
        (0, 199, "düşük"),
        (401, 9999, "yüksek")
        ],

         # Demir Paneli
        "iron": [
        (60, 170, "normal"),
        (0, 59, "düşük"),
        (171, 9999, "yüksek")
        ],
        "tibc": [
        (250, 450, "normal"),
        (451, 9999, "yüksek"),
        (0, 249, "düşük")
        ],
        "ferritin": [
        (30, 400, "normal"),
        (0, 29, "düşük"),
        (401, 9999, "yüksek")
        ],

        # B12 ve Folat (Anemi değerlendirmesi)
        "b12": [
        (200, 900, "normal"),
        (0, 199, "düşük"),
        (901, 9999, "yüksek")
        ],
        "folate": [
        (3, 17, "normal"),
        (0, 2.9, "düşük")
        ]


    },

    "infectious_disease":{

        # Prokalsitonin (Sepsis göstergesi)
        "procalcitonin": [
        (0, 0.1, "normal"),
        (0.11, 0.5, "hafif yüksek"),
        (0.51, 2.0, "orta yüksek"),
        (2.01, 9999, "ciddi yüksek (sepsis şüphesi)")
        ],

        # CRP (C-Reaktif Protein)
        "crp": [
        (0, 5, "normal"),
        (6, 20, "hafif yüksek"),
        (21, 50, "orta yüksek"),
        (51, 9999, "ciddi yüksek")
        ],

        # ESR (Sedimantasyon)
        "esr": [
        (0, 20, "normal"),
        (21, 40, "hafif yüksek"),
        (41, 9999, "yüksek")
        ],

        # Laktat (Sepsis / hipoperfüzyon)
        "lactate": [
        (0.5, 2.0, "normal"),
        (2.1, 4.0, "hafif yüksek"),
        (4.1, 9999, "ciddi yüksek (laktik asidoz)")
        ],

        # Ferritin (inflamasyon / enfeksiyon / sitokin fırtınası)
        "ferritin": [
        (30, 400, "normal"),
        (401, 1000, "hafif yüksek"),
        (1001, 9999, "ciddi yüksek (hiperinflamasyon)")
         ],

        # D-dimer (pıhtılaşma / enfeksiyon / emboli)
        "d_dimer": [
        (0, 0.5, "normal"),
        (0.51, 1.0, "hafif yüksek"),
        (1.01, 9999, "ciddi yüksek")
        ],

        # WBC (hematoloji ile bağlantılı)
         "wbc": [
        (4.0, 11.0, "normal"),
        (11.1, 15.0, "hafif yüksek"),
        (15.1, 9999, "ciddi yüksek"),
        (0, 3.9, "düşük")
         ],

        # Lenfosit (viral enfeksiyon göstergesi)
        "lymphocytes": [
        (1.0, 3.0, "normal"),
        (0, 0.99, "düşük (viral enfeksiyon?)"),
        (3.01, 9999, "yüksek")
        ],

        # Nötrofil (bakteriyel enfeksiyon göstergesi)
        "neutrophils": [
        (2.0, 7.0, "normal"),
        (7.1, 9999, "yüksek (bakteriyel enfeksiyon?)"),
        (0, 1.99, "düşük")
        ]
    },

    "nephrology":{

        # Böbrek Fonksiyonları
        "urea": [
        (10, 50, "normal"),
        (51, 100, "hafif yüksek"),
        (101, 9999, "ciddi yüksek")
        ],
        "creatinine": [
        (0.6, 1.3, "normal"),
        (1.4, 2.0, "hafif yüksek"),
        (2.1, 9999, "ciddi yüksek")
        ],
        "gfr": [
        (90, 9999, "normal"),
        (60, 89, "evre 2 böbrek hastalığı"),
        (30, 59, "evre 3 böbrek hastalığı"),
        (15, 29, "evre 4 böbrek hastalığı"),
        (0, 14, "evre 5 (son dönem böbrek yetmezliği)")
         ],

        # Elektrolitler (Böbrek ile çok ilişkili)
        "sodium": [
        (135, 145, "normal"),
        (146, 160, "yüksek"),
        (0, 134, "düşük")
        ],
        "potassium": [
        (3.5, 5.0, "normal"),
        (5.1, 6.0, "hafif yüksek"),
        (6.1, 9999, "ciddi yüksek (hiperkalemi)")
        ],
        "chloride": [
        (98, 106, "normal"),
        (107, 120, "yüksek"),
        (0, 97, "düşük")
        ],
        "calcium": [
        (8.5, 10.5, "normal"),
        (10.6, 12, "hafif yüksek"),
        (12.1, 9999, "ciddi yüksek")
        ],
        "phosphorus": [
        (2.5, 4.5, "normal"),
        (4.6, 9999, "yüksek"),
        (0, 2.4, "düşük")
        ],
        "magnesium": [
        (1.7, 2.2, "normal"),
        (2.3, 9999, "yüksek"),
        (0, 1.6, "düşük")
        ],

         # İdrar Testleri
        "urine_protein": [
        (0, 150, "normal"),
        (151, 300, "hafif proteinüri"),
        (301, 9999, "ciddi proteinüri (nefrotik aralık)")
        ],
        "urine_albumin": [
        (0, 30, "normal"),
        (31, 300, "mikroalbüminüri"),
        (301, 9999, "makroalbüminüri")
        ],
        "urine_creatinine": [
        (20, 320, "normal"),
        (0, 19, "düşük"),
        (321, 9999, "yüksek")
        ],

        # Albümin / Kreatinin Oranı (ACR)
        "acr": [
        (0, 30, "normal"),
        (31, 300, "mikroalbüminüri"),
        (301, 9999, "makroalbüminüri")
        ],

        # Kan pH (böbrek asit-baz dengesi)
        "blood_ph": [
        (7.35, 7.45, "normal"),
        (0, 7.34, "asidoz"),
        (7.46, 9999, "alkaloz")
        ],

        # Bikarbonat (HCO3)
        "hco3": [
        (22, 26, "normal"),
        (0, 21.9, "düşük (metabolik asidoz)"),
        (26.1, 9999, "yüksek (metabolik alkaloz)")
        ]

    },

    "hepatology": {
        # ALT (SGPT)
        "alt": [
        (0, 40, "normal"),
        (41, 100, "hafif yüksek"),
        (101, 300, "orta yüksek"),
        (301, 9999, "ciddi yüksek (akut hasar?)")
        ],

        # AST (SGOT)
        "ast": [
        (0, 40, "normal"),
        (41, 100, "hafif yüksek"),
        (101, 300, "orta yüksek"),
        (301, 9999, "ciddi yüksek (akut hasar?)")
        ],

        # GGT (Kolestaz göstergesi)
        "ggt": [
        (0, 60, "normal"),
        (61, 200, "hafif yüksek"),
        (201, 9999, "ciddi yüksek (kolestaz?)")
        ],

        # Alkalen Fosfataz (ALP)
        "alp": [
        (40, 130, "normal"),
        (131, 300, "hafif yüksek"),
        (301, 9999, "ciddi yüksek (kolestaz?)")
        ],

        # Total Bilirubin
        "bilirubin_total": [
        (0, 1.2, "normal"),
        (1.3, 3.0, "hafif yüksek"),
        (3.1, 9999, "ciddi yüksek (sarılık)")
        ],

        # Direct Bilirubin
        "bilirubin_direct": [
        (0, 0.3, "normal"),
        (0.4, 1.0, "hafif yüksek"),
        (1.1, 9999, "ciddi yüksek")
        ]
    },

    "gastroenterology":{

        # Pankreas Enzimleri
        "amylase": [
        (30, 110, "normal"),
        (111, 300, "hafif yüksek"),
        (301, 9999, "ciddi yüksek (pankreatit?)")
        ],
        "lipase": [
        (0, 160, "normal"),
        (161, 400, "hafif yüksek"),
        (401, 9999, "ciddi yüksek (pankreatit için daha spesifik)")
        ],

        # Fekal Kalprotektin (IBD göstergesi)
        "fecal_calprotectin": [
        (0, 50, "normal"),
        (51, 200, "hafif yüksek (IBS?)"),
        (201, 9999, "ciddi yüksek (IBD / Crohn / ÜK?)")
        ],

        # Fekal Gizli Kan (Gastrointestinal kanama)
        "fecal_occult_blood": [
        (0, 0, "negatif"),
        (1, 9999, "pozitif (GİS kanama?)")
        ],

        # Fekal Elastaz (Pankreas yetmezliği)
        "fecal_elastase": [
        (200, 500, "normal"),
        (100, 199, "hafif düşük (hafif pankreas yetmezliği)"),
        (0, 99, "ciddi düşük (ekzokrin pankreas yetmezliği)")
        ],

        # Gastrin (Zollinger-Ellison sendromu / gastrit)
        "gastrin": [
        (0, 100, "normal"),
        (101, 500, "hafif yüksek"),
        (501, 9999, "ciddi yüksek (Zollinger-Ellison?)")
        ],

        # Helicobacter pylori Antijen (peptik ülser)
        "h_pylori_antigen": [
        (0, 0, "negatif"),
        (1, 9999, "pozitif (H. pylori enfeksiyonu)")
         ],

        # Fekal pH (malabsorpsiyon / enfeksiyon)
        "fecal_ph": [
        (6.5, 7.5, "normal"),
        (0, 6.4, "asit (malabsorpsiyon?)"),
        (7.6, 9999, "alkali (enfeksiyon?)")
        ],

        # Fekal Yağ (steatore)
        "fecal_fat": [
        (0, 7, "normal"),
        (8, 14, "hafif yüksek"),
        (15, 9999, "ciddi yüksek (malabsorpsiyon / pankreas yetmezliği)")
        ]


    },

    "pediatrics":{

        # Çocuk WBC (yaşa göre değişir, ortalama değerler)
        "wbc_child": [
        (5.0, 15.0, "normal"),
        (15.1, 20.0, "hafif yüksek"),
        (20.1, 9999, "ciddi yüksek"),
        (0, 4.9, "düşük")
        ],

        # Çocuk Hemoglobin
        "hgb_child": [
        (11.0, 16.0, "normal"),
        (0, 10.9, "düşük"),
        (16.1, 9999, "yüksek")
        ],

        # Çocuk Hematokrit
        "hct_child": [
        (33, 45, "normal"),
        (0, 32.9, "düşük"),
        (45.1, 9999, "yüksek")
        ],

        # Çocuk Trombosit
        "plt_child": [
        (150, 450, "normal"),
        (0, 149, "düşük"),
        (451, 9999, "yüksek")
        ],

        # Yenidoğan Total Bilirubin (çok önemli)
        "bilirubin_newborn": [
        (0, 12, "normal"),
        (12.1, 15, "hafif yüksek"),
        (15.1, 20, "orta yüksek"),
        (20.1, 9999, "ciddi yüksek (kernikterus riski)")
        ],

        # Çocuk CRP
        "crp_child": [
        (0, 5, "normal"),
        (6, 20, "hafif yüksek"),
        (21, 50, "orta yüksek"),
        (51, 9999, "ciddi yüksek")
        ],

        # Çocuk Ferritin
        "ferritin_child": [
        (20, 200, "normal"),
        (0, 19, "düşük"),
        (201, 9999, "yüksek")
        ],

        # Çocuk Demir
        "iron_child": [
        (50, 120, "normal"),
        (0, 49, "düşük"),
        (121, 9999, "yüksek")
        ],

        # Çocuk Elektrolitler
        "sodium_child": [
        (135, 145, "normal"),
        (146, 160, "yüksek"),
        (0, 134, "düşük")
        ],

        "potassium_child": [
        (3.5, 5.5, "normal"),
        (5.6, 6.5, "hafif yüksek"),
        (6.6, 9999, "ciddi yüksek")
        ],

        "calcium_child": [
        (8.8, 10.8, "normal"),
        (10.9, 12, "hafif yüksek"),
        (12.1, 9999, "ciddi yüksek")
        ],

        # Çocuk Vitamin D
        "vitamin_d_child": [
        (30, 100, "normal"),
        (20, 29, "hafif düşük"),
        (0, 19, "ciddi düşük")
        ],

        # Çocuk B12
        "b12_child": [
        (200, 900, "normal"),
        (0, 199, "düşük"),
        (901, 9999, "yüksek")
        ]
    },

    "ob_gyn":{

        # Beta-hCG (Gebelik hormonu)
        "beta_hcg": [
        (0, 5, "negatif"),
        (6, 25, "şüpheli (tekrar test)"),
        (26, 999999, "pozitif (gebelik)")
        ],

        # Gebelik haftasına göre hCG (ortalama aralıklar)
        "hcg_week_3": [(5, 50, "normal aralık")],
        "hcg_week_4": [(10, 425, "normal aralık")],
        "hcg_week_5": [(19, 7340, "normal aralık")],
        "hcg_week_6": [(1080, 56500, "normal aralık")],
        "hcg_week_7_8": [(7650, 229000, "normal aralık")],
        "hcg_week_9_12": [(25700, 288000, "normal aralık")],

        # Progesteron (Gebelik ve ovulasyon için kritik)
        "progesterone": [
        (0, 1.5, "foliküler faz"),
        (2, 20, "luteal faz (normal)"),
        (21, 9999, "gebelik aralığı")
        ],

        # Estradiol (E2)
        "estradiol": [
        (30, 400, "normal"),
        (0, 29, "düşük"),
        (401, 9999, "yüksek")
        ],

        # FSH (Folikül uyarıcı hormon)
        "fsh": [
        (3, 10, "normal"),
        (11, 20, "hafif yüksek"),
        (21, 9999, "ciddi yüksek (menopoz?)")
        ],

        # LH (Luteinize edici hormon)
        "lh": [
        (2, 12, "normal"),
        (13, 9999, "yüksek (PCOS?)")
        ],

        # LH/FSH oranı (PCOS için kritik)
        "lh_fsh_ratio": [
        (0, 1.9, "normal"),
        (2.0, 9999, "yüksek (PCOS şüphesi)")
        ],

        # AMH (Anti-Müllerian hormon) – yumurtalık rezervi
        "amh": [
        (1.0, 4.0, "normal"),
        (0, 0.99, "düşük rezerv"),
        (4.1, 9999, "yüksek (PCOS?)")
        ],

        # Prolaktin (Hiperprolaktinemi)
        "prolactin": [
        (4, 15, "normal"),
        (16, 25, "hafif yüksek"),
        (26, 9999, "ciddi yüksek (prolaktinoma?)")
        ],

        # TSH (Gebelikte özel aralık)
        "tsh_pregnancy": [
        (0.1, 2.5, "normal (gebelik)"),
        (2.6, 9999, "yüksek (hipotiroidi?)"),
        (0, 0.09, "düşük (hipertiroidi?)")
        ],

        # DHEA-S (Androjen fazlalığı)
        "dhea_s": [
        (35, 430, "normal"),
        (431, 9999, "yüksek (PCOS / adrenal?)"),
        (0, 34, "düşük")
        ]
    },

    "oncology":{

        # CEA (Kolon kanseri belirteci)
        "cea": [
        (0, 3, "normal"),
        (3.1, 5, "hafif yüksek"),
        (5.1, 9999, "ciddi yüksek (kolon kanseri?)")
        ],

        # CA-125 (Over kanseri belirteci)
        "ca125": [
        (0, 35, "normal"),
        (36, 100, "hafif yüksek"),
        (101, 9999, "ciddi yüksek (over kanseri?)")
        ],

        # CA 19-9 (Pankreas kanseri belirteci)
        "ca19_9": [
        (0, 37, "normal"),
        (38, 100, "hafif yüksek"),
        (101, 9999, "ciddi yüksek (pankreas / safra yolu?)")
        ],

        # AFP (Karaciğer tümörleri)
         "afp": [
        (0, 10, "normal"),
        (11, 100, "hafif yüksek"),
        (101, 9999, "ciddi yüksek (hepatoselüler karsinom?)")
        ],

        # PSA (Prostat kanseri)
        "psa": [
        (0, 4, "normal"),
        (4.1, 10, "hafif yüksek"),
        (10.1, 9999, "ciddi yüksek (prostat kanseri?)")
        ],

        # Serbest PSA oranı (kanser riskini belirler)
        "free_psa_ratio": [
        (0.25, 1.0, "düşük risk"),
        (0.10, 0.24, "orta risk"),
        (0, 0.09, "yüksek risk (kanser?)")
        ],

        # LDH (Lenfoma / lösemi / metastaz)
        "ldh": [
        (140, 280, "normal"),
        (281, 9999, "yüksek (doku hasarı / malignite?)")
        ],

        # Beta-2 Mikroglobulin (Lenfoma / miyelom)
        "beta2_microglobulin": [
        (0.7, 1.8, "normal"),
        (1.9, 3.5, "hafif yüksek"),
        (3.6, 9999, "ciddi yüksek (lenfoma / miyelom?)")
        ],

        # Ferritin (çok yüksek → malignite / inflamasyon)
        "ferritin": [
        (30, 400, "normal"),
        (401, 1000, "hafif yüksek"),
        (1001, 9999, "ciddi yüksek (hiperinflamasyon / malignite?)")
        ],

        # CRP (kanser inflamasyonu)
        "crp": [
        (0, 5, "normal"),
        (6, 20, "hafif yüksek"),
        (21, 50, "orta yüksek"),
        (51, 9999, "ciddi yüksek")
        ],

        # D-dimer (kanser + pıhtılaşma)
        "d_dimer": [
        (0, 0.5, "normal"),
        (0.51, 1.0, "hafif yüksek"),
        (1.01, 9999, "ciddi yüksek (tromboz / malignite?)")
        ]
    },

    "neurology":{

        # CK (Kas hasarı / miyopati)
        "ck": [
        (30, 200, "normal"),
        (201, 1000, "hafif yüksek (kas hasarı)"),
        (1001, 9999, "ciddi yüksek (rabdomiyoliz?)")
        ],

        # Vitamin B12 (Nöropati için kritik)
        "b12": [
        (200, 900, "normal"),
        (0, 199, "düşük (nöropati riski)"),
        (901, 9999, "yüksek")
        ],

        # Folat (Nörolojik fonksiyon)
        "folate": [
        (3, 17, "normal"),
        (0, 2.9, "düşük (nörolojik etkiler)")
        ],

        # Ammonia (Hepatik ensefalopati → nörolojik)
        "ammonia": [
        (15, 45, "normal"),
        (46, 80, "hafif yüksek"),
        (81, 9999, "ciddi yüksek (ensefalopati?)")
        ],

        # Laktat (mitokondriyal hastalık / nörometabolik bozukluk)
        "lactate": [
        (0.5, 2.0, "normal"),
        (2.1, 4.0, "hafif yüksek"),
        (4.1, 9999, "ciddi yüksek (laktik asidoz)")
        ],

        # Sodyum (nöbet / bilinç değişikliği)
        "sodium": [
        (135, 145, "normal"),
        (0, 134, "düşük (nöbet riski)"),
        (146, 160, "yüksek (bilinç değişikliği)")
        ],

        # Kalsiyum (kas kasılması / nöbet)
        "calcium": [
        (8.5, 10.5, "normal"),
        (0, 8.49, "düşük (tetani / nöbet?)"),
        (10.6, 9999, "yüksek (bilinç değişikliği?)")
        ],

        # Magnezyum (nöbet / kas kasılması)
        "magnesium": [
        (1.7, 2.2, "normal"),
        (0, 1.69, "düşük (nöbet / kas kasılması)"),
        (2.3, 9999, "yüksek")
        ],

        # CRP (nöroinflamasyon)
        "crp": [
        (0, 5, "normal"),
        (6, 20, "hafif yüksek"),
        (21, 50, "orta yüksek"),
        (51, 9999, "ciddi yüksek")
        ],

        # ESR (kronik nöroinflamasyon)
        "esr": [
        (0, 20, "normal"),
        (21, 40, "hafif yüksek"),
        (41, 9999, "yüksek")
        ],

        # TSH (nöropsikiyatrik etkiler)
        "tsh": [
        (0.4, 4.0, "normal"),
        (4.1, 10, "hafif yüksek (hipotiroidi → depresyon?)"),
        (10.1, 9999, "ciddi yüksek"),
        (0, 0.39, "düşük (hipertiroidi → anksiyete?)")
        ]
    },

    "pulmonology":{

        # D-dimer (Pulmoner emboli için kritik)
        "d_dimer": [
        (0, 0.5, "normal"),
        (0.51, 1.0, "hafif yüksek"),
        (1.01, 9999, "ciddi yüksek (PE / DVT?)")
        ],

        # CRP (Enfeksiyon / inflamasyon)
        "crp": [
        (0, 5, "normal"),
        (6, 20, "hafif yüksek"),
        (21, 50, "orta yüksek"),
        (51, 9999, "ciddi yüksek")
        ],

        # Arteriyel Kan Gazı (ABG) – pH
        "abg_ph": [
        (7.35, 7.45, "normal"),
        (0, 7.34, "asidoz"),
        (7.46, 9999, "alkaloz")
        ],

        # PaO2 (oksijen basıncı)
        "pao2": [
        (80, 100, "normal"),
        (60, 79, "hafif düşük (hafif hipoksi)"),
        (40, 59, "orta düşük (orta hipoksi)"),
        (0, 39, "ciddi düşük (ağır hipoksi)")
        ],

        # PaCO2 (karbondioksit basıncı)
        "paco2": [
        (35, 45, "normal"),
        (46, 60, "yüksek (hiperkapni / solunum yetmezliği)"),
        (0, 34, "düşük (hiperventilasyon)")
        ],

        # HCO3 (bikarbonat – metabolik durum)
        "hco3": [
        (22, 26, "normal"),
        (0, 21.9, "düşük (metabolik asidoz)"),
        (26.1, 9999, "yüksek (metabolik alkaloz)")
        ],

        # O2 Saturasyonu (SpO2)
        "spo2": [
        (95, 100, "normal"),
        (90, 94, "hafif düşük"),
        (80, 89, "orta düşük"),
        (0, 79, "ciddi düşük (hipoksi)")
        ],

        # Laktat (hipoperfüzyon / sepsis / ağır solunum yetmezliği)
        "lactate": [
        (0.5, 2.0, "normal"),
        (2.1, 4.0, "hafif yüksek"),
        (4.1, 9999, "ciddi yüksek (laktik asidoz)")
        ],

        # Eozinofil (Astım / alerji)
        "eosinophils": [
        (0, 0.5, "normal"),
        (0.51, 1.0, "hafif yüksek"),
        (1.01, 9999, "ciddi yüksek (alerji / astım?)")
        ],

        # COHb (Karbonmonoksit zehirlenmesi)
        "carboxyhemoglobin": [
        (0, 2, "normal"),
        (3, 10, "hafif yüksek"),
        (11, 9999, "ciddi yüksek (CO zehirlenmesi)")
        ]
    },

    "dermatology":{

        # Vitamin D (Saç dökülmesi, egzama, bağışıklık)
        "vitamin_d": [
        (30, 100, "normal"),
        (20, 29, "hafif düşük"),
        (0, 19, "ciddi düşük (deri bariyeri zayıf)")
        ],

        # Çinko (Saç dökülmesi, yara iyileşmesi)
        "zinc": [
        (70, 120, "normal"),
        (0, 69, "düşük (saç dökülmesi / egzama?)"),
        (121, 9999, "yüksek")
        ],

        # Ferritin (Saç dökülmesi için kritik)
        "ferritin": [
        (30, 400, "normal"),
        (0, 29, "düşük (saç dökülmesi?)"),
        (401, 9999, "yüksek (inflamasyon?)")
        ],

        # IgE (Alerji / atopik dermatit)
        "ige": [
        (0, 100, "normal"),
        (101, 400, "hafif yüksek (alerji?)"),
        (401, 9999, "ciddi yüksek (atopik dermatit?)")
        ],

        # Eozinofil (Alerji / egzama)
        "eosinophils": [
        (0, 0.5, "normal"),
        (0.51, 1.0, "hafif yüksek"),
        (1.01, 9999, "ciddi yüksek (alerjik reaksiyon?)")
        ],

        # ANA (Otoimmün deri hastalıkları)
        "ana": [
        (0, 1, "negatif"),
        (2, 9999, "pozitif (lupus / otoimmün?)")
        ],

        # CRP (Deri inflamasyonu)
        "crp": [
        (0, 5, "normal"),
        (6, 20, "hafif yüksek"),
        (21, 50, "orta yüksek"),
        (51, 9999, "ciddi yüksek")
        ],

        # ESR (Kronik inflamasyon)
        "esr": [
        (0, 20, "normal"),
        (21, 40, "hafif yüksek"),
        (41, 9999, "yüksek")
        ],

        # B12 (deri sağlığı / pigmentasyon)
        "b12": [
        (200, 900, "normal"),
        (0, 199, "düşük"),
        (901, 9999, "yüksek")
        ],

        # Folat (deri yenilenmesi)
        "folate": [
        (3, 17, "normal"),
        (0, 2.9, "düşük")
        ]
    },

    "urology":{


        # PSA (Prostat kanseri taraması)
        "psa": [
        (0, 4, "normal"),
        (4.1, 10, "hafif yüksek"),
        (10.1, 9999, "ciddi yüksek (prostat kanseri?)")
        ],

        # Serbest PSA oranı (risk değerlendirmesi)
        "free_psa_ratio": [
        (0.25, 1.0, "düşük risk"),
        (0.10, 0.24, "orta risk"),
        (0, 0.09, "yüksek risk (kanser?)")
        ],

        # Kreatinin (böbrek fonksiyonu)
        "creatinine": [
        (0.6, 1.3, "normal"),
        (1.4, 2.0, "hafif yüksek"),
        (2.1, 9999, "ciddi yüksek")
        ],

        # Üre
        "urea": [
        (10, 50, "normal"),
        (51, 100, "hafif yüksek"),
        (101, 9999, "ciddi yüksek")
        ],

        # Ürik Asit (Böbrek taşı / gut)
        "uric_acid": [
        (3.5, 7.2, "normal"),
        (7.3, 9.0, "hafif yüksek"),
        (9.1, 9999, "ciddi yüksek (gut / taş?)")
        ],

        # İdrar pH (taş tipi için kritik)
        "urine_ph": [
        (5.0, 7.0, "normal"),
        (0, 4.9, "asit (ürik asit taşı?)"),
        (7.1, 9999, "alkali (fosfat taşı?)")
        ],

        # İdrar Protein (nefrotik sendrom)
        "urine_protein": [
        (0, 150, "normal"),
        (151, 300, "hafif proteinüri"),
        (301, 9999, "ciddi proteinüri (nefrotik aralık)")
        ],

        # İdrar Albümin
        "urine_albumin": [
        (0, 30, "normal"),
        (31, 300, "mikroalbüminüri"),
        (301, 9999, "makroalbüminüri")
         ],

        # ACR (Albümin/Kreatinin oranı)
        "acr": [
        (0, 30, "normal"),
        (31, 300, "mikroalbüminüri"),
        (301, 9999, "makroalbüminüri")
        ],

        # İdrar Nitrit (bakteriyel enfeksiyon)
        "urine_nitrite": [
        (0, 0, "negatif"),
        (1, 9999, "pozitif (bakteriyel İYE)")
        ],

        # İdrar Lökosit (enfeksiyon)
        "urine_leukocyte": [
        (0, 10, "normal"),
        (11, 9999, "yüksek (İYE?)")
        ],

        # İdrar Kristalleri (taş öncüsü)
        "urine_crystals": [
        (0, 0, "yok"),
        (1, 9999, "var (taş riski)")
        ]


    },

    "rheumatology":{

        # Romatoid Artrit Belirteçleri
        "rf": [
        (0, 14, "negatif"),
        (15, 30, "hafif pozitif"),
        (31, 9999, "pozitif (RA?)")
        ],
        "anti_ccp": [
        (0, 20, "negatif"),
        (21, 39, "şüpheli"),
        (40, 9999, "pozitif (RA için spesifik)")
        ],

        # Lupus Belirteçleri
        "ana": [
        (0, 1, "negatif"),
        (2, 9999, "pozitif (otoimmün?)")
        ],
        "anti_ds_dna": [
        (0, 30, "normal"),
        (31, 100, "hafif yüksek"),
        (101, 9999, "pozitif (SLE?)")
        ],
        "anti_smith": [
        (0, 1, "negatif"),
        (2, 9999, "pozitif (SLE için spesifik)")
        ],

        # Sjögren Sendromu
        "anti_ro": [
        (0, 1, "negatif"),
        (2, 9999, "pozitif (Sjögren / SLE?)")
        ],
         "anti_la": [
        (0, 1, "negatif"),
        (2, 9999, "pozitif (Sjögren?)")
        ],

        # Vaskülit Belirteçleri
        "anca_p": [
        (0, 1, "negatif"),
        (2, 9999, "pozitif (MPO-ANCA / vaskülit?)")
        ],
        "anca_c": [
        (0, 1, "negatif"),
        (2, 9999, "pozitif (PR3-ANCA / vaskülit?)")
         ],

        # Skleroderma
        "anti_scl70": [
        (0, 1, "negatif"),
        (2, 9999, "pozitif (skleroderma?)")
        ],
        "anti_centromere": [
        (0, 1, "negatif"),
        (2, 9999, "pozitif (CREST?)")
        ],

        # Behçet Hastalığı
        "crp": [
        (0, 5, "normal"),
        (6, 20, "hafif yüksek"),
        (21, 50, "orta yüksek"),
        (51, 9999, "ciddi yüksek")
        ],
        "esr": [
        (0, 20, "normal"),
        (21, 40, "hafif yüksek"),
        (41, 9999, "yüksek")
        ],

        # FMF (Ailevi Akdeniz Ateşi)
        "serum_amyloid_a": [
        (0, 6, "normal"),
        (7, 100, "yüksek (FMF atağı?)"),
        (101, 9999, "çok yüksek (amiloidoz riski)")
        ],

        # Otoinflamasyon / Sitokin Fırtınası
        "ferritin": [
        (30, 400, "normal"),
        (401, 1000, "hafif yüksek"),
        (1001, 9999, "ciddi yüksek (MAS / HLH?)")
        ],

        # Ürik Asit (Gut)
        "uric_acid": [
        (3.5, 7.2, "normal"),
        (7.3, 9.0, "hafif yüksek"),
        (9.1, 9999, "ciddi yüksek (gut?)")
        ]
    }

}

#---16 Branslık tam liste---

BRANCHES = [
    "Dahiliye",
    "Kardiyoloji",
    "Endokrinoloji",
    "Hematoloji",
    "Enfeksiyon",
    "Nefroloji",
    "Hepatoloji",
    "Gastroenteroloji",
    "Pediatri",
    "Kadın Doğum",
    "Onkoloji",
    "Nöroloji",
    "Göğüs Hastalıkları",
    "Dermatoloji",
    "Üroloji",
    "Romatoloji"
]








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

    def classify_value(self,col_name,value):
        """
        Verilen Kolon değerini REFERANCE_RANGES tablosuna göre sınıflandırır.
        Örnek çıktı: "yuksek","hafif yüksek","düşük"
        """

        #Eğer kolon referans tablosunda yoksa sınıflandırma yapmaz
        if col_name not in REFERENCE_RANGES:
            return "Referans aralığı yok!"

        #Değer numeric'e çevir
        try:
            val = float(value)
        except:
            return "Geçersiz değer!"

        #Kolonun referans aralıklarını al
        ranges = REFERENCE_RANGES[col_name]

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



    def translate_to_turkish(self,text):
        try:
            translator = Translator()
            result = translator.translate(text,src="en",dest="tr")
            return result.text
        except Exception as e:
            return f"Çeviri hatası {e}"



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


        #--- BASİT FİLTRELEME---
        self.lbl_filter = tk.Label(self.frame_right,text="Veri Filtreleme:")
        self.lbl_filter.grid(row=2,column=0,pady=5)

        self.combo_filter_col = ttk.Combobox(self.frame_right,state="readonly")
        self.combo_filter_col.grid(row=3,column=0,pady=5)

        self.combo_filter_op = ttk.Combobox(self.frame_right,state="readonly",
                                            values=["<",">",">=","<=","==","!="])
        self.combo_filter_op.grid(row=4,column=0,pady=5)
        self.combo_filter_op.set("==")

        self.entry_filter_value = tk.Entry(self.frame_right)
        self.entry_filter_value.grid(row=5,column=0,pady=5)

        #Filtreleme düğmesi
        self.btn_apply_filter = tk.Button(self.frame_right,text="Filtre Uygula",command=self.apply_filter_button)
        self.btn_apply_filter.grid(row=6,column=0,pady=10)

        self.btn_clear_filter = tk.Button(self.frame_right, text="Filtreyi Kaldır", command=self.clear_filter_gui)
        self.btn_clear_filter.grid(row=8, column=0, columnspan=3, pady=5)

        self.btn_ai = tk.Button(
            self.frame_right,
            text="AI Analiz Yap",
            command=self.ai_analysis_button
        )
        self.btn_ai.grid(row=9,column=0,padx=10,pady=10)

        # Türkce AI Yorum
        self.ai_text = tk.Text(
            self.frame_right,
            height=10,
            width=40,
            font=("Arial",11),
            wrap="word"
        )

        self.ai_text.grid(row=10,column=0,padx=10,pady=10)

        scroll = tk.Scrollbar(self.frame_right,command=self.ai_text.yview)
        scroll.grid(row=10,column=1,sticky="ns")
        self.ai_text.config(yscrollcommand=scroll.set)

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

    def ask_ai_async(self,summary):
        thread = threading.Thread(target=self.run_ai_analysis,args=(summary,))
        thread.daemon=True
        thread.start()



    def run_ai_analysis(self,summary):
        try:

            # 2) AI worker'ı çalıştır
            process = subprocess.Popen(
            ["python","ai_worker.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
            )

            # 3) Prompt'u AI worker'a gonder
            ai_output_bytes,error_bytes = process.communicate(
                summary.encode("utf-8","ignore"))

            #---UTF-8 olarak oku---
            try:
                ai_output = ai_output_bytes.decode("utf-8","ignore")
            except:
                ai_output = "AI çıktısı UTF-8 olarak çözülemedi."

            # --- Hata varsa UTF-8 olarak oku
            try:
                error=error_bytes.decode("utf-8","ignore")
            except:
                error=""

            if error.strip():
                self.ai_text.after(0,lambda:self.update_ai_text(f"AI hata verdi:\n{error}"))
                return

            # 4) İngilizce -> Türkçe çeviri
            translator = Translator()
            try:
                turkish_output = translator.translate(ai_output,src="en",dest="tr").text
            except:
                turkish_output = "Çeviri yapılamadı."


            # 5)GUI'ye  yaz
            self.ai_text.after(0, lambda: self.update_ai_text(turkish_output))
        except Exception as e:
            self.ai_text.after(0,lambda:self.update_ai_text(f"AI çalışırken hata oluştu: {e}"))

    def update_ai_text(self,ai_response):
        #GUİ güvenli yazma
        self.ai_text.delete("1.0", tk.END)
        self.ai_text.insert(tk.END, ai_response)

    def clear_filter_gui(self):
        print("Filtre kaldırıldı,veri yeniden yüklendi!")
        self.logic.df = self.logic.df_original.copy()

        self.ask_ai_async(self.generate_full_summary())

    def on_branch_selected(self,event):
        selected = self.branch_var.get()
        self.result_label.config(text=f"Seçilen Branş:{selected}")

    def ai_analysis_button(self):
        summary = self.generate_full_summary()

        if not summary.strip():
            print("AI analiz için yeterli veri yok!")
            return

        self.ask_ai_async(summary)

if __name__ == "__main__":
    root = tk.Tk()
    root.tk.call("encoding","system","utf-8")

    app = DataAnalyseGUI(root)
    root.mainloop()
