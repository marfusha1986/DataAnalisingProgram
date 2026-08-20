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

AGE_GROUPS = {
    "newborn": (0, 0.1),      # 0–1 ay
    "infant": (0.1, 1),       # 1 ay–1 yaş
    "toddler": (1, 3),        # 1–3 yaş
    "child": (4, 12),         # 4–12 yaş
    "adolescent": (13, 18),   # 13–18 yaş
    "adult": (19, 64),        # 19–64 yaş
    "elderly": (65, 200)      # 65+
}

PREGNANCY_STAGES = {
    "non_pregnant": None,
    "first_trimester": (0, 13),
    "second_trimester": (14, 27),
    "third_trimester": (28, 42)
}


REFERENCE_RANGES = {
    "internal_medicine": {
        'lab':{
            "liver_panel": {
                "sgpt": [(0,40,"normal"), (41,100,"hafif yüksek"), (101,300,"orta yüksek"), (300,9999,"ciddi yüksek")],
                "sgot": [(0,40,"normal"), (41,100,"hafif yüksek"), (101,300,"orta yüksek"), (300,9999,"ciddi yüksek")],
                "alkphos": [(40,130,"normal"), (131,300,"hafif yüksek"), (300,9999,"yüksek")],
                "tot_bilirubin": [(0,1.2,"normal"), (1.3,3,"hafif yüksek"), (3,9999,"yüksek")],
                "direct_bilirubin": [(0,0.3,"normal"), (0.4,1,"hafif yüksek"), (1,9999,"yüksek")],
                "albumin": [(3.5,5.5,"normal"), (0,3.49,"düşük")],
                "tot_proteins": [(6.0,8.3,"normal"), (0,5.99,"düşük"), (8.31,9999,"yüksek")],
                "ag_ratio": [(1.0,2.2,"normal"), (0,0.99,"düşük"), (2.21,9999,"yüksek")]
            },

            "kidney_panel": {
                "urea": [(10,50,"normal"), (51,100,"hafif yüksek"), (101,9999,"yüksek")],
                "creatinine": [(0.6,1.3,"normal"), (1.4,2.0,"hafif yüksek"), (2.1,9999,"yüksek")],
                "gfr": [(90,9999,"normal"), (60,89,"hafif düşük"), (30,59,"orta düşük"), (0,29,"ciddi düşük")]
            },

            "metabolism_panel": {
                "glucose": [(70,99,"normal"), (100,125,"prediyabet"), (126,9999,"diyabet")],
                "hba1c": [(4.0,5.6,"normal"), (5.7,6.4,"prediyabet"), (6.5,9999,"diyabet")],
                "insulin": [(2,25,"normal"), (26,9999,"yüksek")],
                "homa_ir": [(0,2,"normal"), (2.1,2.9,"hafif yüksek"), (3,9999,"insülin direnci")]
            },

            "electrolytes": {
                "sodium": [(135,145,"normal"), (146,160,"yüksek"), (0,134,"düşük")],
                "potassium": [(3.5,5.0,"normal"), (5.1,6.0,"hafif yüksek"), (6.1,9999,"ciddi yüksek")],
                "chloride": [(98,106,"normal"), (107,120,"yüksek"), (0,97,"düşük")],
                "calcium": [(8.5,10.5,"normal"), (10.6,12,"hafif yüksek"), (12.1,9999,"ciddi yüksek")],
                "phosphorus": [(2.5,4.5,"normal"), (4.6,9999,"yüksek"), (0,2.4,"düşük")],
                "magnesium": [(1.7,2.2,"normal"), (2.3,9999,"yüksek"), (0,1.6,"düşük")]
            },

            "thyroid_panel": {
                "tsh": [(0.4,4.0,"normal"), (4.1,10,"hafif yüksek"), (10.1,9999,"ciddi yüksek")],
                "ft4": [(0.8,1.8,"normal"), (0,0.79,"düşük"), (1.81,9999,"yüksek")],
                "ft3": [(2.3,4.2,"normal"), (0,2.29,"düşük"), (4.21,9999,"yüksek")]
            },

            "vitamin_minerals": {
                "vitamin_d": [(30,100,"normal"), (20,29,"hafif düşük"), (0,19,"ciddi düşük")],
                "b12": [(200,900,"normal"), (0,199,"düşük"), (901,9999,"yüksek")],
                "folate": [(3,17,"normal"), (0,2.9,"düşük")],
                "iron": [(60,170,"normal"), (0,59,"düşük"), (171,9999,"yüksek")],
                "ferritin": [(30,400,"normal"), (0,29,"düşük"), (401,9999,"yüksek")]
            },

            "lipid_panel": {
                "cholesterol_total": [(0,200,"normal"), (201,239,"hafif yüksek"), (240,9999,"yüksek")],
                "ldl": [(0,100,"optimal"), (101,129,"iyi"), (130,159,"sınır yüksek"), (160,189,"yüksek"), (190,9999,"çok yüksek")],
                "hdl": [(60,9999,"iyi"), (40,59,"orta"), (0,39,"düşük")],
                "triglycerides": [(0,150,"normal"), (151,199,"hafif yüksek"), (200,499,"yüksek"), (500,9999,"çok yüksek")]
            }
        },
        "ultrasound": {
            "liver_size": [(0, 15, "normal"), (15.1, 999, "hepatomegali")],
            "spleen_size": [(0, 12, "normal"), (12.1, 999, "splenomegali")],
            "kidney_size": [(9, 12, "normal"), (0, 8.9, "küçük"), (12.1, 999, "büyük")],
            "gallbladder_wall": [(0, 3, "normal"), (3.1, 999, "kalınlaşma")],
            "ascites": [(0, 0, "yok"), (1, 999, "var")]
        },

        "mri": {
            "liver_fat": [(0, 5, "normal"), (6, 15, "hafif yağlanma"), (16, 999, "ciddi yağlanma")],
            "iron_load": [(0, 1, "normal"), (2, 4, "hafif"), (5, 999, "yüksek")],
            "kidney_cysts": [(0, 0, "yok"), (1, 999, "var")],
            "pancreas_edema": [(0, 0, "yok"), (1, 999, "var")]
        },

        "ct": {
            "lymph_nodes": [(0, 1, "normal"), (2, 999, "büyümüş")],
            "lung_infiltrates": [(0, 0, "yok"), (1, 999, "var")],
            "liver_lesions": [(0, 0, "yok"), (1, 999, "var")]
        },

        "clinical": {
            "symptoms": {
                "fever": [(0, 0, "yok"), (1, 999, "var")],
                "fatigue": [(0, 0, "yok"), (1, 999, "var")],
                "abdominal_pain": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "hepatomegaly": [(0, 0, "yok"), (1, 999, "var")],
                "splenomegaly": [(0, 0, "yok"), (1, 999, "var")],
                "edema": [(0, 0, "yok"), (1, 999, "var")]
            },

            "vitals": {
                "heart_rate": [(60, 100, "normal"), (0, 59, "düşük"), (101, 999, "yüksek")],
                "blood_pressure_sys": [(90, 140, "normal"), (141, 999, "yüksek"), (0, 89, "düşük")],
                "temperature": [(36, 37.5, "normal"), (37.6, 999, "ateş")]
            }
        }

    },
    "cardiology": {
        "lab": {
            "cardiac_markers": {
                "troponin_i": [(0,0.04,"normal"), (0.05,0.39,"hafif yüksek"), (0.40,9999,"ciddi yüksek")],
                "troponin_t": [(0,0.01,"normal"), (0.02,0.09,"hafif yüksek"), (0.10,9999,"ciddi yüksek")],
                "ck_mb": [(0,5,"normal"), (6,24,"hafif yüksek"), (25,9999,"ciddi yüksek")],
                "myoglobin": [(0,85,"normal"), (86,9999,"yüksek")]
            },

            "heart_failure_markers": {
                "bnp": [(0,100,"normal"), (101,300,"hafif yüksek"), (301,9999,"ciddi yüksek")],
                "nt_pro_bnp": [(0,125,"normal"), (126,450,"hafif yüksek"), (451,9999,"ciddi yüksek")]
            },

            "thrombosis_panel": {
                "d_dimer": [(0,0.5,"normal"), (0.51,1.0,"hafif yüksek"), (1.01,9999,"ciddi yüksek")]
            },

            "lipid_panel": {
                "cholesterol_total": [(0,200,"normal"), (201,239,"hafif yüksek"), (240,9999,"yüksek")],
                "ldl": [(0,100,"optimal"), (101,129,"iyi"), (130,159,"sınır yüksek"), (160,189,"yüksek"), (190,9999,"çok yüksek")],
                "hdl": [(60,9999,"iyi"), (40,59,"orta"), (0,39,"düşük")],
                "triglycerides": [(0,150,"normal"), (151,199,"hafif yüksek"), (200,499,"yüksek"), (500,9999,"çok yüksek")]
            }
        },

        "imaging": {
            "echo": {
                "ef": [(55,70,"normal"), (41,54,"hafif düşük"), (31,40,"orta düşük"), (0,30,"ciddi düşük")],
                "lv_mass": [(0,150,"normal"), (151,200,"hafif yüksek"), (201,9999,"yüksek")],
                "rv_pressure": [(0,35,"normal"), (36,50,"hafif yüksek"), (51,9999,"yüksek")],
                "wall_motion": [(0,0,"normal"), (1,999,"bozuk")],
                "mitral_regurgitation": [(0,0,"yok"), (1,1,"hafif"), (2,2,"orta"), (3,999,"ciddi")],
                "aortic_stenosis": [(0,0,"yok"), (1,1,"hafif"), (2,2,"orta"), (3,999,"ciddi")]
            },

            "cardiac_mri": {
                "late_gadolinium_enhancement": [(0, 0, "yok"), (1, 999, "var")],
                "edema": [(0, 0, "yok"), (1, 999, "var")],
                "fibrosis": [(0, 0, "yok"), (1, 999, "var")],
                "rv_function": [(45, 70, "normal"), (30, 44, "hafif düşük"), (0, 29, "ciddi düşük")]
            },

            "cardiac_ct": {
                "calcium_score": [(0,10,"normal"), (11,100,"hafif"), (101,400,"orta"), (401,9999,"ciddi")],
                "stenosis_percent": [(0,20,"normal"), (21,49,"hafif"), (50,69,"orta"), (70,999,"ciddi")]
            }
        },

    "clinical": {
        "ekg": {
            "st_elevation": [(0,0,"yok"), (1,999,"var")],
            "st_depression": [(0,0,"yok"), (1,999,"var")],
            "qrs_width": [(70,110,"normal"), (111,140,"geniş"), (141,999,"çok geniş")],
            "pr_interval": [(120,200,"normal"), (201,999,"uzamış")],
            "qt_interval": [(350,450,"normal"), (451,999,"uzamış")],
            "rhythm": [(0,0,"sinüs"), (1,999,"aritmi")]
        },

        "holter": {
            "pvc_count": [(0, 100, "normal"), (101, 1000, "hafif"), (1001, 9999, "yüksek")],
            "pac_count": [(0, 100, "normal"), (101, 9999, "yüksek")],
            "af_burden": [(0, 0, "yok"), (1, 10, "hafif"), (11, 999, "yüksek")],
            "longest_pause": [(0, 2, "normal"), (3, 999, "uzun")]
        },

        "symptoms": {
            "chest_pain": [(0,0,"yok"), (1,999,"var")],
            "dyspnea": [(0,0,"yok"), (1,999,"var")],
            "palpitation": [(0,0,"yok"), (1,999,"var")],
            "syncope": [(0,0,"yok"), (1,999,"var")]
        }
    }


    },

    "endocrinology": {
        "lab": {

            "thyroid_panel": {
                "tsh": [(0.4,4.0,"normal"), (4.1,10,"hafif yüksek"), (10.1,9999,"ciddi yüksek")],
                "ft4": [(0.8,1.8,"normal"), (0,0.79,"düşük"), (1.81,9999,"yüksek")],
                "ft3": [(2.3,4.2,"normal"), (0,2.29,"düşük"), (4.21,9999,"yüksek")]
            },

            "diabetes_panel": {
                "glucose_fasting": [(70,99,"normal"), (100,125,"prediyabet"), (126,9999,"diyabet")],
                "glucose_pp": [(70,140,"normal"), (141,199,"prediyabet"), (200,9999,"diyabet")],
                "hba1c": [(4.0,5.6,"normal"), (5.7,6.4,"prediyabet"), (6.5,9999,"diyabet")],
                "insulin": [(2,25,"normal"), (26,9999,"yüksek")],
                "homa_ir": [(0,2,"normal"), (2.1,2.9,"hafif yüksek"), (3,9999,"insülin direnci")]
            },

            "adrenal_panel": {
                "cortisol_morning": [(6,23,"normal"), (0,5.9,"düşük"), (24,9999,"yüksek")],
                "acth": [(10,60,"normal"), (0,9.9,"düşük"), (61,9999,"yüksek")],
                "dhea_s": [(35,430,"normal"), (0,34,"düşük"), (431,9999,"yüksek")]
            },

            "gonadal_panel": {
                "estradiol": [(30,400,"normal"), (0,29,"düşük"), (401,9999,"yüksek")],
                "progesterone": [(5,20,"normal (luteal)"), (0,4.9,"düşük"), (21,9999,"yüksek")],
                "fsh": [(3,10,"normal"), (11,20,"hafif yüksek"), (21,9999,"ciddi yüksek")],
                "lh": [(2,12,"normal"), (13,9999,"yüksek")],
                "testosterone_total": [(300,1000,"normal"), (0,299,"düşük"), (1001,9999,"yüksek")],
                "testosterone_free": [(5,25,"normal"), (0,4.9,"düşük"), (26,9999,"yüksek")]
            },

            "prolactin_panel": {
                "prolactin": [(4,15,"normal"), (16,25,"hafif yüksek"), (26,9999,"ciddi yüksek")]
            }
        },

        "imaging": {
            "thyroid_ultrasound": {
                "thyroid_size": [(0,25,"normal"), (26,999,"büyük")],
                "nodule_count": [(0,0,"yok"), (1,999,"var")],
                "nodule_size": [(0,1,"küçük"), (1.1,3,"orta"), (3.1,999,"büyük")],
                "vascularity": [(0,0,"normal"), (1,999,"artmış")]
            },

            "adrenal_imaging": {
                "adrenal_mass": [(0,0,"yok"), (1,999,"var")],
                "mass_size": [(0,1,"küçük"), (1.1,4,"orta"), (4.1,999,"büyük")],
                "fat_content": [(0,10,"normal"), (11,999,"yüksek")],
                "pheochromocytoma_signs": [(0,0,"yok"), (1,999,"var")]
            }
        },

        "clinical": {
            "symptoms": {
                "fatigue": [(0,0,"yok"), (1,999,"var")],
                "weight_gain": [(0,0,"yok"), (1,999,"var")],
                "weight_loss": [(0,0,"yok"), (1,999,"var")],
                "palpitation": [(0,0,"yok"), (1,999,"var")],
                "polyuria": [(0,0,"yok"), (1,999,"var")],
                "polydipsia": [(0,0,"yok"), (1,999,"var")]
            },

            "physical_exam": {
                "goiter": [(0,0,"yok"), (1,999,"var")],
                "acanthosis_nigricans": [(0,0,"yok"), (1,999,"var")],
                "hirsutism": [(0,0,"yok"), (1,999,"var")]
            },

            "risk_scores": {
                "diabetes_risk": [(0,5,"düşük"), (6,10,"orta"), (11,999,"yüksek")],
                "thyroid_risk": [(0,3,"düşük"), (4,6,"orta"), (7,999,"yüksek")]
            }
        }

    },

    "hematology": {
        "lab": {

            "cbc": {
                "wbc": [(4.0,11.0,"normal"), (11.1,15.0,"hafif yüksek"), (15.1,9999,"ciddi yüksek"), (0,3.9,"düşük")],
                "rbc": [(4.5,6.0,"normal"), (0,4.49,"düşük"), (6.01,9999,"yüksek")],
                "hgb": [(13.5,17.5,"normal"), (0,13.49,"düşük"), (17.6,9999,"yüksek")],
                "hct": [(38,50,"normal"), (0,37.9,"düşük"), (50.1,9999,"yüksek")],
                "plt": [(150,450,"normal"), (0,149,"düşük"), (451,9999,"yüksek")],
                "rdw": [(11.5,14.5,"normal"), (14.6,9999,"yüksek")],
                "mcv": [(80,100,"normal"), (0,79,"mikrositik"), (101,9999,"makrositik")],
                "mch": [(27,33,"normal"), (0,26.9,"düşük"), (33.1,9999,"yüksek")],
                "mchc": [(32,36,"normal"), (0,31.9,"düşük"), (36.1,9999,"yüksek")]
            },

            "coagulation": {
                "inr": [(0.8,1.2,"normal"), (1.3,2.0,"hafif yüksek"), (2.1,9999,"ciddi yüksek")],
                "aptt": [(25,35,"normal"), (36,9999,"uzamış")],
                "fibrinogen": [(200,400,"normal"), (0,199,"düşük"), (401,9999,"yüksek")]
            },

            "iron_panel": {
                "iron": [(60,170,"normal"), (0,59,"düşük"), (171,9999,"yüksek")],
                "tibc": [(250,450,"normal"), (451,9999,"yüksek"), (0,249,"düşük")],
                "ferritin": [(30,400,"normal"), (0,29,"düşük"), (401,9999,"yüksek")]
            },

            "b12_folate": {
                "b12": [(200,900,"normal"), (0,199,"düşük"), (901,9999,"yüksek")],
                "folate": [(3,17,"normal"), (0,2.9,"düşük")]
            },

            "inflammation": {
                "crp": [(0,5,"normal"), (6,20,"hafif yüksek"), (21,50,"orta yüksek"), (50,9999,"ciddi yüksek")],
                "esr": [(0,20,"normal"), (21,50,"hafif yüksek"), (51,9999,"yüksek")],
                "procalcitonin": [(0,0.5,"normal"), (0.51,2,"orta"), (2.1,9999,"ciddi yüksek")]
            }
        },

        "imaging": {
            "ultrasound": {
                "spleen_size": [(0,12,"normal"), (12.1,999,"splenomegali")],
                "liver_size": [(0,15,"normal"), (15.1,999,"hepatomegali")],
                "lymph_nodes": [(0,0,"normal"), (1,999,"büyümüş")]
            },

            "ct_mri": {
                "lymphadenopathy": [(0,0,"yok"), (1,999,"var")],
                "bone_marrow_infiltration": [(0,0,"yok"), (1,999,"var")],
                "splenic_infarct": [(0,0,"yok"), (1,999,"var")]
            }
        },

        "clinical": {
            "symptoms": {
                "fatigue": [(0,0,"yok"), (1,999,"var")],
                "pallor": [(0,0,"yok"), (1,999,"var")],
                "fever": [(0,0,"yok"), (1,999,"var")],
                "night_sweats": [(0,0,"yok"), (1,999,"var")],
                "weight_loss": [(0,0,"yok"), (1,999,"var")]
            },

            "physical_exam": {
                "lymph_nodes": [(0, 0, "normal"), (1, 999, "büyümüş")],
                "splenomegaly": [(0, 0, "yok"), (1, 999, "var")],
                "hepatomegaly": [(0, 0, "yok"), (1, 999, "var")],
                "petechiae": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "anemia_risk": [(0,5,"düşük"), (6,10,"orta"), (11,999,"yüksek")],
                "leukemia_risk": [(0,3,"düşük"), (4,6,"orta"), (7,999,"yüksek")]
            }
        }

    },


    "infectious_disease":{

        "lab": {

            "infection_panel": {
                "wbc": [(4.0, 11.0, "normal"), (11.1, 15.0, "hafif yüksek"), (15.1, 9999, "ciddi yüksek"),
                        (0, 3.9, "düşük")],
                "neutrophils_percent": [(40, 70, "normal"), (71, 90, "yüksek"), (0, 39, "düşük")],
                "lymphocytes_percent": [(20, 40, "normal"), (0, 19, "düşük"), (41, 999, "yüksek")],
                "crp": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 50, "orta yüksek"), (51, 9999, "ciddi yüksek")],
                "esr": [(0, 20, "normal"), (21, 50, "hafif yüksek"), (51, 9999, "yüksek")],
                "procalcitonin": [(0, 0.5, "normal"), (0.51, 2, "orta"), (2.1, 9999, "ciddi yüksek")]
            },

            "sepsis_panel": {
                "lactate": [(0, 2, "normal"), (2.1, 4, "orta"), (4.1, 9999, "ciddi yüksek")],
                "platelets": [(150, 450, "normal"), (0, 149, "düşük"), (451, 9999, "yüksek")],
                "bilirubin": [(0, 1.2, "normal"), (1.3, 3, "hafif yüksek"), (3.1, 9999, "yüksek")]
            },

            "viral_panel": {
                "alt": [(0, 40, "normal"), (41, 100, "hafif yüksek"), (101, 9999, "yüksek")],
                "ast": [(0, 40, "normal"), (41, 100, "hafif yüksek"), (101, 9999, "yüksek")],
                "ldh": [(140, 280, "normal"), (281, 9999, "yüksek")]
            }
        },

        "imaging": {

            "chest_imaging": {
                "chest_xray_infiltrates": [(0, 0, "yok"), (1, 999, "var")],
                "ct_ground_glass": [(0, 0, "yok"), (1, 999, "var")],
                "pleural_effusion": [(0, 0, "yok"), (1, 999, "var")]
            },

            "abdominal_imaging": {
                "abscess": [(0, 0, "yok"), (1, 999, "var")],
                "organ_enlargement": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "symptoms": {
                "fever": [(0, 0, "yok"), (1, 999, "var")],
                "chills": [(0, 0, "yok"), (1, 999, "var")],
                "cough": [(0, 0, "yok"), (1, 999, "var")],
                "dyspnea": [(0, 0, "yok"), (1, 999, "var")],
                "abdominal_pain": [(0, 0, "yok"), (1, 999, "var")],
                "diarrhea": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "tachycardia": [(0, 0, "yok"), (1, 999, "var")],
                "hypotension": [(0, 0, "yok"), (1, 999, "var")],
                "rash": [(0, 0, "yok"), (1, 999, "var")],
                "lymphadenopathy": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "sepsis_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "pneumonia_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
            }
        }
    },

    "nephrology": {
        "lab": {

            "kidney_panel": {
                "urea": [(10,50,"normal"), (51,100,"hafif yüksek"), (101,9999,"yüksek")],
                "creatinine": [(0.6,1.3,"normal"), (1.4,2.0,"hafif yüksek"), (2.1,9999,"yüksek")],
                "gfr": [(90,9999,"normal"), (60,89,"hafif düşük"), (30,59,"orta düşük"), (0,29,"ciddi düşük")]
            },

            "electrolytes": {
                "sodium": [(135,145,"normal"), (146,160,"yüksek"), (0,134,"düşük")],
                "potassium": [(3.5,5.0,"normal"), (5.1,6.0,"hafif yüksek"), (6.1,9999,"ciddi yüksek")],
                "chloride": [(98,106,"normal"), (107,120,"yüksek"), (0,97,"düşük")],
                "calcium": [(8.5,10.5,"normal"), (10.6,12,"hafif yüksek"), (12.1,9999,"ciddi yüksek")],
                "phosphorus": [(2.5,4.5,"normal"), (4.6,9999,"yüksek"), (0,2.4,"düşük")],
                "magnesium": [(1.7,2.2,"normal"), (2.3,9999,"yüksek"), (0,1.6,"düşük")]
            },

            "urine_tests": {
                "urine_protein": [(0,150,"normal"), (151,300,"hafif proteinüri"), (301,9999,"nefrotik aralık")],
                "urine_albumin": [(0,30,"normal"), (31,300,"mikroalbüminüri"), (301,9999,"makroalbüminüri")],
                "acr": [(0,30,"normal"), (31,300,"mikroalbüminüri"), (301,9999,"makroalbüminüri")],
                "urine_creatinine": [(20,320,"normal"), (0,19,"düşük"), (321,9999,"yüksek")]
            },

            "acid_base": {
                "blood_ph": [(7.35,7.45,"normal"), (0,7.34,"asidoz"), (7.46,9999,"alkaloz")],
                "hco3": [(22,26,"normal"), (0,21.9,"düşük"), (26.1,9999,"yüksek")]
            }
        },

        "imaging": {
            "kidney_ultrasound": {
                "kidney_size": [(9,12,"normal"), (0,8.9,"küçük"), (12.1,999,"büyük")],
                "cortical_thickness": [(6,10,"normal"), (0,5.9,"azalmış")],
                "hydronephrosis": [(0,0,"yok"), (1,1,"hafif"), (2,2,"orta"), (3,999,"ciddi")],
                "renal_cysts": [(0,0,"yok"), (1,999,"var")],
                "stones": [(0,0,"yok"), (1,999,"var")]
            },

            "ct_mri": {
                "renal_mass": [(0,0,"yok"), (1,999,"var")],
                "perirenal_fluid": [(0,0,"yok"), (1,999,"var")],
                "renal_artery_stenosis": [(0,0,"yok"), (1,999,"var")]
            }
        },

        "clinical": {
            "symptoms": {
                "edema": [(0,0,"yok"), (1,999,"var")],
                "fatigue": [(0,0,"yok"), (1,999,"var")],
                "nausea": [(0,0,"yok"), (1,999,"var")],
                "decreased_urine": [(0,0,"yok"), (1,999,"var")],
                "flank_pain": [(0,0,"yok"), (1,999,"var")]
            },

            "physical_exam": {
                "hypertension": [(0, 0, "yok"), (1, 999, "var")],
                "pitting_edema": [(0, 0, "yok"), (1, 999, "var")],
                "renal_bruit": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "ckd_risk": [(0,5,"düşük"), (6,10,"orta"), (11,999,"yüksek")],
                "aki_risk": [(0,5,"düşük"), (6,10,"orta"), (11,999,"yüksek")]
            }
        }
    },

    "hepatology": {
        "lab": {

            "liver_panel": {
                "alt": [(0,40,"normal"), (41,100,"hafif yüksek"), (101,300,"orta yüksek"), (301,9999,"ciddi yüksek")],
                "ast": [(0,40,"normal"), (41,100,"hafif yüksek"), (101,300,"orta yüksek"), (301,9999,"ciddi yüksek")],
                "ggt": [(0,60,"normal"), (61,200,"hafif yüksek"), (201,9999,"ciddi yüksek")],
                "alp": [(40,130,"normal"), (131,300,"hafif yüksek"), (301,9999,"ciddi yüksek")],
                "tot_bilirubin": [(0,1.2,"normal"), (1.3,3,"hafif yüksek"), (3.1,9999,"ciddi yüksek")],
                "direct_bilirubin": [(0,0.3,"normal"), (0.4,1,"hafif yüksek"), (1.1,9999,"ciddi yüksek")],
                "albumin": [(3.5,5.5,"normal"), (0,3.49,"düşük")],
                "inr": [(0.8,1.2,"normal"), (1.3,1.5,"hafif yüksek"), (1.6,9999,"ciddi yüksek")],
                "ammonia": [(15,45,"normal"), (46,80,"hafif yüksek"), (81,9999,"ciddi yüksek")]
            },

            "viral_hepatitis_panel": {
                "hbsag": [(0,0,"negatif"), (1,999,"pozitif")],
                "anti_hbs": [(10,9999,"koruyucu"), (0,9,"düşük")],
                "anti_hbc": [(0,0,"negatif"), (1,999,"pozitif")],
                "hbeag": [(0,0,"negatif"), (1,999,"pozitif")],
                "anti_hcv": [(0,0,"negatif"), (1,999,"pozitif")],
                "hcv_rna": [(0,0,"negatif"), (1,999,"pozitif")]
            },

            "autoimmune_panel": {
                "ana": [(0,0,"negatif"), (1,999,"pozitif")],
                "asma": [(0,0,"negatif"), (1,999,"pozitif")],
                "ama": [(0,0,"negatif"), (1,999,"pozitif")],
                "anti_lkm": [(0,0,"negatif"), (1,999,"pozitif")]
            },

            "fibrosis_markers": {
                "fib4": [(0,1.3,"düşük risk"), (1.31,2.67,"orta risk"), (2.68,9999,"yüksek risk")],
                "apri": [(0,0.5,"düşük"), (0.51,1.5,"orta"), (1.51,9999,"yüksek")]
            }
        },

        "imaging": {
            "ultrasound": {
                "liver_size": [(0,15,"normal"), (15.1,999,"hepatomegali")],
                "fatty_liver": [(0,0,"yok"), (1,1,"hafif"), (2,2,"orta"), (3,999,"ciddi")],
                "splenomegaly": [(0,12,"normal"), (12.1,999,"splenomegali")],
                "ascites": [(0,0,"yok"), (1,999,"var")],
                "portal_vein_diameter": [(0,13,"normal"), (13.1,999,"geniş")]
            },

            "elastography": {
                "liver_stiffness_kpa": [(0, 7, "F0-F1"), (7.1, 9.5, "F2"), (9.6, 12.5, "F3"),
                                        (12.6, 999, "F4 (siroz)")],
                "cap_score": [(0, 238, "S0"), (239, 259, "S1"), (260, 289, "S2"), (290, 999, "S3")]
            },

            "ct_mri": {
                "liver_lesions": [(0,0,"yok"), (1,999,"var")],
                "portal_hypertension": [(0,0,"yok"), (1,999,"var")],
                "varices": [(0,0,"yok"), (1,999,"var")],
                "hepatocellular_carcinoma": [(0,0,"yok"), (1,999,"var")]
            }
        },

        "clinical": {
            "symptoms": {
                "jaundice": [(0,0,"yok"), (1,999,"var")],
                "itching": [(0,0,"yok"), (1,999,"var")],
                "fatigue": [(0,0,"yok"), (1,999,"var")],
                "abdominal_distension": [(0,0,"yok"), (1,999,"var")],
                "confusion": [(0,0,"yok"), (1,999,"var")]  # ensefalopati
            },

            "physical_exam": {
                "hepatomegaly": [(0, 0, "yok"), (1, 999, "var")],
                "splenomegaly": [(0, 0, "yok"), (1, 999, "var")],
                "ascites": [(0, 0, "yok"), (1, 999, "var")],
                "spider_angio": [(0, 0, "yok"), (1, 999, "var")],
                "palmar_erythema": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "child_pugh": [(5,6,"A (iyi)"), (7,9,"B (orta)"), (10,15,"C (kötü)")],
                "meld": [(0,10,"düşük"), (11,20,"orta"), (21,999,"yüksek")]
            }
        }

    },


    "gastroenterology": {
        "lab": {

            "pancreas_panel": {
                "amylase": [(30,110,"normal"), (111,300,"hafif yüksek"), (301,9999,"ciddi yüksek")],
                "lipase": [(0,160,"normal"), (161,400,"hafif yüksek"), (401,9999,"ciddi yüksek")],
                "trypsin": [(0,310,"normal"), (311,9999,"yüksek")]
            },

            "ibd_panel": {
                "fecal_calprotectin": [(0,50,"normal"), (51,200,"hafif yüksek"), (201,9999,"ciddi yüksek")],
                "crp": [(0,5,"normal"), (6,20,"hafif yüksek"), (21,9999,"yüksek")],
                "esr": [(0,20,"normal"), (21,50,"hafif yüksek"), (51,9999,"yüksek")]
            },

            "malabsorption_panel": {
                "fecal_fat": [(0,7,"normal"), (8,14,"hafif yüksek"), (15,9999,"ciddi yüksek")],
                "fecal_elastase": [(200,500,"normal"), (100,199,"hafif düşük"), (0,99,"ciddi düşük")],
                "vitamin_b12": [(200,900,"normal"), (0,199,"düşük")],
                "folate": [(3,17,"normal"), (0,2.9,"düşük")]
            },

            "ulcer_panel": {
                "h_pylori_antigen": [(0,0,"negatif"), (1,999,"pozitif")],
                "gastrin": [(0,100,"normal"), (101,500,"hafif yüksek"), (501,9999,"ciddi yüksek")]
            },

            "gi_bleeding_panel": {
                "fecal_occult_blood": [(0,0,"negatif"), (1,999,"pozitif")],
                "hemoglobin": [(13.5,17.5,"normal"), (0,13.49,"düşük")]
            }
        },

        "imaging": {
            "ultrasound": {
                "liver_fat": [(0,0,"yok"), (1,1,"hafif"), (2,2,"orta"), (3,999,"ciddi")],
                "gallbladder_wall": [(0,3,"normal"), (3.1,999,"kalınlaşma")],
                "bile_duct_diameter": [(0,6,"normal"), (6.1,999,"geniş")],
                "pancreas_edema": [(0,0,"yok"), (1,999,"var")],
                "ascites": [(0,0,"yok"), (1,999,"var")]
            },

            "ct": {
                "appendicitis": [(0, 0, "yok"), (1, 999, "var")],
                "diverticulitis": [(0, 0, "yok"), (1, 999, "var")],
                "bowel_thickening": [(0, 0, "yok"), (1, 999, "var")],
                "pancreatitis_signs": [(0, 0, "yok"), (1, 999, "var")]
            },

            "mri": {
                "liver_iron": [(0,1,"normal"), (2,4,"hafif"), (5,999,"yüksek")],
                "pancreas_atrophy": [(0,0,"yok"), (1,999,"var")],
                "bile_duct_obstruction": [(0,0,"yok"), (1,999,"var")]
            }
        },

        "clinical": {
            "symptoms": {
                "abdominal_pain": [(0,0,"yok"), (1,999,"var")],
                "diarrhea": [(0,0,"yok"), (1,999,"var")],
                "constipation": [(0,0,"yok"), (1,999,"var")],
                "bloody_stool": [(0,0,"yok"), (1,999,"var")],
                "nausea": [(0,0,"yok"), (1,999,"var")],
                "vomiting": [(0,0,"yok"), (1,999,"var")]
            },

            "physical_exam": {
                "tenderness": [(0, 0, "yok"), (1, 999, "var")],
                "rebound": [(0, 0, "yok"), (1, 999, "var")],
                "guarding": [(0, 0, "yok"), (1, 999, "var")],
                "hepatomegaly": [(0, 0, "yok"), (1, 999, "var")],
                "splenomegaly": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "ibd_risk": [(0,5,"düşük"), (6,10,"orta"), (11,999,"yüksek")],
                "pancreatitis_risk": [(0,5,"düşük"), (6,10,"orta"), (11,999,"yüksek")]
            }
        }

    },


    "pediatrics":{

        "lab": {

            "cbc": {
                "wbc": {
                    "newborn": [(9, 30, "normal"), (0, 8.9, "düşük"), (30.1, 999, "yüksek")],
                    "infant": [(6, 17, "normal"), (0, 5.9, "düşük"), (17.1, 999, "yüksek")],
                    "child": [(5, 14.5, "normal"), (0, 4.9, "düşük"), (14.6, 999, "yüksek")],
                    "adolescent": [(4, 11, "normal"), (0, 3.9, "düşük"), (11.1, 999, "yüksek")]
                },
                "hgb": {
                    "newborn": [(14, 22, "normal"), (0, 13.9, "düşük"), (22.1, 999, "yüksek")],
                    "infant": [(10, 14, "normal"), (0, 9.9, "düşük"), (14.1, 999, "yüksek")],
                    "child": [(11.5, 15.5, "normal"), (0, 11.4, "düşük"), (15.6, 999, "yüksek")],
                    "adolescent": [(12, 16, "normal"), (0, 11.9, "düşük"), (16.1, 999, "yüksek")]
                },
                "plt": {
                    "newborn": [(150, 450, "normal"), (0, 149, "düşük"), (451, 999, "yüksek")],
                    "infant": [(150, 450, "normal"), (0, 149, "düşük"), (451, 999, "yüksek")],
                    "child": [(150, 450, "normal"), (0, 149, "düşük"), (451, 999, "yüksek")],
                    "adolescent": [(150, 450, "normal"), (0, 149, "düşük"), (451, 999, "yüksek")]
                }
            },

            "electrolytes": {
                "sodium": {
                    "newborn": [(135, 145, "normal"), (0, 134, "düşük"), (146, 999, "yüksek")],
                    "infant": [(135, 145, "normal"), (0, 134, "düşük"), (146, 999, "yüksek")],
                    "child": [(135, 145, "normal"), (0, 134, "düşük"), (146, 999, "yüksek")],
                    "adolescent": [(135, 145, "normal"), (0, 134, "düşük"), (146, 999, "yüksek")]
                },
                "potassium": {
                    "newborn": [(3.7, 5.9, "normal"), (0, 3.6, "düşük"), (6, 999, "yüksek")],
                    "infant": [(3.5, 5.5, "normal"), (0, 3.4, "düşük"), (5.6, 999, "yüksek")],
                    "child": [(3.5, 5.0, "normal"), (0, 3.4, "düşük"), (5.1, 999, "yüksek")],
                    "adolescent": [(3.5, 5.0, "normal"), (0, 3.4, "düşük"), (5.1, 999, "yüksek")]
                },
                "calcium": {
                    "infant": [(9, 11, "normal"), (0, 8.9, "düşük"), (11.1, 999, "yüksek")],
                    "child": [(8.5, 10.5, "normal"), (0, 8.4, "düşük"), (10.6, 999, "yüksek")],
                    "adolescent": [(8.5, 10.5, "normal"), (0, 8.4, "düşük"), (10.6, 999, "yüksek")]
                }
            },

            "infection_panel": {
                "crp": {
                    "newborn": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")],
                    "infant": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")],
                    "child": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")],
                    "adolescent": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")]
                },
                "procalcitonin": {
                    "newborn": [(0, 0.5, "normal"), (0.51, 2, "orta"), (2.1, 999, "ciddi yüksek")],
                    "infant": [(0, 0.5, "normal"), (0.51, 2, "orta"), (2.1, 999, "ciddi yüksek")],
                    "child": [(0, 0.5, "normal"), (0.51, 2, "orta"), (2.1, 999, "ciddi yüksek")],
                    "adolescent": [(0, 0.5, "normal"), (0.51, 2, "orta"), (2.1, 999, "ciddi yüksek")]
                }
            },

            "metabolism_panel": {
                "glucose": {
                    "newborn": [(40, 90, "normal"), (0, 39, "düşük"), (91, 999, "yüksek")],
                    "infant": [(60, 100, "normal"), (0, 59, "düşük"), (101, 999, "yüksek")],
                    "child": [(70, 99, "normal"), (100, 125, "prediyabet"), (126, 999, "diyabet")],
                    "adolescent": [(70, 99, "normal"), (100, 125, "prediyabet"), (126, 999, "diyabet")]
                }
            }
        },

        "imaging": {

            "ultrasound": {
                "appendix_diameter": [(0, 6, "normal"), (6.1, 999, "apandisit")],
                "intussusception": [(0, 0, "yok"), (1, 999, "var")],
                "hydronephrosis": [(0, 0, "yok"), (1, 999, "var")]
            },

            "chest_xray": {
                "bronchiolitis_signs": [(0, 0, "yok"), (1, 999, "var")],
                "pneumonia": [(0, 0, "yok"), (1, 999, "var")],
                "hyperinflation": [(0, 0, "yok"), (1, 999, "var")]
            },

            "ct_mri": {
                "brain_edema": [(0, 0, "yok"), (1, 999, "var")],
                "ventriculomegaly": [(0, 0, "yok"), (1, 999, "var")],
                "abdominal_mass": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "symptoms": {
                "fever": [(0, 0, "yok"), (1, 999, "var")],
                "poor_feeding": [(0, 0, "yok"), (1, 999, "var")],
                "irritability": [(0, 0, "yok"), (1, 999, "var")],
                "vomiting": [(0, 0, "yok"), (1, 999, "var")],
                "diarrhea": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "dehydration": [(0, 0, "yok"), (1, 999, "var")],
                "rash": [(0, 0, "yok"), (1, 999, "var")],
                "lymphadenopathy": [(0, 0, "yok"), (1, 999, "var")]
            },

            "development": {
                "motor_delay": [(0, 0, "yok"), (1, 999, "var")],
                "speech_delay": [(0, 0, "yok"), (1, 999, "var")],
                "growth_percentile": [(3, 97, "normal"), (0, 2.9, "düşük"), (97.1, 999, "yüksek")]
            }
        }
    },

    "ob_gyn":{

        "lab": {

            "pregnancy_panel": {
                "hcg": {
                    "non_pregnant": [(0, 5, "normal")],
                    "first_trimester": [(5000, 200000, "normal"), (0, 4999, "düşük"), (200001, 999999, "yüksek")],
                    "second_trimester": [(10000, 80000, "normal")],
                    "third_trimester": [(5000, 50000, "normal")]
                },
                "progesterone": {
                    "non_pregnant": [(5, 20, "normal")],
                    "first_trimester": [(11, 90, "normal")],
                    "second_trimester": [(25, 90, "normal")],
                    "third_trimester": [(48, 300, "normal")]
                },
                "estradiol": {
                    "non_pregnant": [(30, 400, "normal")],
                    "first_trimester": [(188, 2497, "normal")],
                    "second_trimester": [(1278, 7192, "normal")],
                    "third_trimester": [(6137, 34600, "normal")]
                }
            },

            "gynecology_hormones": {
                "fsh": {
                    "adult": [(3, 10, "normal"), (11, 20, "hafif yüksek"), (21, 999, "ciddi yüksek")],
                    "elderly": [(25, 134, "menopoz")]
                },
                "lh": {
                    "adult": [(2, 12, "normal"), (13, 999, "yüksek")],
                    "elderly": [(15, 999, "menopoz")]
                },
                "prolactin": {
                    "adult": [(4, 15, "normal"), (16, 25, "hafif yüksek"), (26, 999, "ciddi yüksek")]
                },
                "amh": {
                    "adult": [(1, 4, "normal"), (0, 0.9, "düşük"), (4.1, 999, "yüksek")]
                }
            },

            "infection_panel": {
                "vaginal_ph": [(3.8, 4.5, "normal"), (4.6, 999, "yüksek")],
                "candida_antigen": [(0, 0, "negatif"), (1, 999, "pozitif")],
                "trichomonas": [(0, 0, "negatif"), (1, 999, "pozitif")],
                "gardnerella": [(0, 0, "negatif"), (1, 999, "pozitif")]
            },

            "pregnancy_glucose": {
                "ogtt_1h": {
                    "first_trimester": [(0, 140, "normal"), (141, 999, "yüksek")],
                    "second_trimester": [(0, 140, "normal"), (141, 999, "yüksek")],
                    "third_trimester": [(0, 140, "normal"), (141, 999, "yüksek")]
                }
            }
        },

        "imaging": {

            "ob_ultrasound": {
                "crl": {  # Crown-Rump Length
                    "first_trimester": [(10, 84, "normal"), (0, 9, "düşük"), (85, 999, "yüksek")]
                },
                "bpd": {  # Biparietal Diameter
                    "second_trimester": [(40, 80, "normal")],
                    "third_trimester": [(80, 100, "normal")]
                },
                "fl": {   # Femur Length
                    "second_trimester": [(20, 40, "normal")],
                    "third_trimester": [(40, 60, "normal")]
                },
                "placenta_position": [(0, 0, "normal"), (1, 999, "previa")]
            },

            "doppler": {
                "umbilical_ri": [(0.5, 0.7, "normal"), (0.71, 999, "yüksek")],
                "uterine_artery_notch": [(0, 0, "yok"), (1, 999, "var")]
            },

            "gyn_ultrasound": {
                "endometrial_thickness": {
                    "adult": [(3, 14, "normal"), (0, 2.9, "düşük"), (14.1, 999, "yüksek")]
                },
                "ovarian_cyst": [(0, 0, "yok"), (1, 999, "var")],
                "fibroid": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "ob_symptoms": {
                "vaginal_bleeding": [(0, 0, "yok"), (1, 999, "var")],
                "abdominal_pain": [(0, 0, "yok"), (1, 999, "var")],
                "decreased_fetal_movement": [(0, 0, "yok"), (1, 999, "var")],
                "hyperemesis": [(0, 0, "yok"), (1, 999, "var")]
            },

            "gyn_symptoms": {
                "pelvic_pain": [(0, 0, "yok"), (1, 999, "var")],
                "dyspareunia": [(0, 0, "yok"), (1, 999, "var")],
                "irregular_cycles": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "cervical_motion_tenderness": [(0, 0, "yok"), (1, 999, "var")],
                "uterine_tenderness": [(0, 0, "yok"), (1, 999, "var")],
                "adnexal_mass": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "preeclampsia_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "preterm_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
            }
        }
    },

    "oncology":{

        "lab": {

            "tumor_markers": {

                "cea": {  # Kolon kanseri
                    "adult": [(0, 3, "normal"), (3.1, 5, "hafif yüksek"), (5.1, 9999, "ciddi yüksek")],
                    "elderly": [(0, 4, "normal"), (4.1, 6, "hafif yüksek"), (6.1, 9999, "ciddi yüksek")]
                },

                "ca125": {  # Over kanseri
                    "adult": [(0, 35, "normal"), (36, 100, "hafif yüksek"), (101, 9999, "ciddi yüksek")]
                },

                "ca19_9": {  # Pankreas / safra yolu
                    "adult": [(0, 37, "normal"), (38, 100, "hafif yüksek"), (101, 9999, "ciddi yüksek")]
                },

                "afp": {  # Karaciğer tümörü (HCC)
                    "child": [(0, 10, "normal"), (11, 100, "hafif yüksek"), (101, 9999, "ciddi yüksek")],
                    "adult": [(0, 10, "normal"), (11, 100, "hafif yüksek"), (101, 9999, "ciddi yüksek")]
                },

                "psa": {  # Prostat kanseri
                    "adult": [(0, 4, "normal"), (4.1, 10, "hafif yüksek"), (10.1, 9999, "ciddi yüksek")],
                    "elderly": [(0, 6, "normal"), (6.1, 10, "hafif yüksek"), (10.1, 9999, "ciddi yüksek")]
                },

                "free_psa_ratio": {
                    "adult": [(0.25, 1.0, "düşük risk"), (0.10, 0.24, "orta risk"), (0, 0.09, "yüksek risk")]
                }
            },

            "hematologic_markers": {

                "ldh": {
                    "child": [(140, 280, "normal"), (281, 9999, "yüksek")],
                    "adult": [(140, 280, "normal"), (281, 9999, "yüksek")]
                },

                "beta2_microglobulin": {
                    "adult": [(0.7, 1.8, "normal"), (1.9, 3.5, "hafif yüksek"), (3.6, 9999, "ciddi yüksek")]
                },

                "ferritin": {
                    "child": [(20, 200, "normal"), (201, 9999, "yüksek")],
                    "adult": [(30, 400, "normal"), (401, 1000, "hafif yüksek"), (1001, 9999, "ciddi yüksek")]
                }
            },

            "inflammation_panel": {
                "crp": {
                    "child": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 9999, "ciddi yüksek")],
                    "adult": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 9999, "ciddi yüksek")]
                },
                "d_dimer": {
                    "adult": [(0, 0.5, "normal"), (0.51, 1.0, "hafif yüksek"), (1.01, 9999, "ciddi yüksek")]
                }
            }
        },

        "imaging": {

            "ultrasound": {
                "liver_lesion": [(0, 0, "yok"), (1, 999, "var")],
                "thyroid_nodule": [(0, 0, "yok"), (1, 999, "var")],
                "breast_mass": [(0, 0, "yok"), (1, 999, "var")]
            },

            "ct": {
                "lung_nodule": [(0, 0, "yok"), (1, 999, "var")],
                "lymphadenopathy": [(0, 0, "yok"), (1, 999, "var")],
                "pancreas_mass": [(0, 0, "yok"), (1, 999, "var")]
            },

            "mri": {
                "brain_mass": [(0, 0, "yok"), (1, 999, "var")],
                "bone_marrow_infiltration": [(0, 0, "yok"), (1, 999, "var")]
            },

            "pet_ct": {
                "fdg_uptake": [(0, 2.5, "normal"), (2.6, 4.9, "orta"), (5, 999, "yüksek")]
            }
        },

        "clinical": {

            "symptoms": {
                "weight_loss": [(0, 0, "yok"), (1, 999, "var")],
                "night_sweats": [(0, 0, "yok"), (1, 999, "var")],
                "fatigue": [(0, 0, "yok"), (1, 999, "var")],
                "pain": [(0, 0, "yok"), (1, 999, "var")],
                "bleeding": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "lymph_nodes": [(0, 0, "normal"), (1, 999, "büyümüş")],
                "hepatomegaly": [(0, 0, "yok"), (1, 999, "var")],
                "splenomegaly": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "solid_tumor_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "lymphoma_risk": [(0, 3, "düşük"), (4, 6, "orta"), (7, 999, "yüksek")]
            }
        }
    },

    "neurology":{

        "lab": {

            "electrolytes": {
                "sodium": {
                    "child": [(135, 145, "normal"), (0, 134, "düşük"), (146, 999, "yüksek")],
                    "adult": [(135, 145, "normal"), (0, 134, "düşük"), (146, 999, "yüksek")],
                    "elderly": [(135, 147, "normal"), (0, 134, "düşük"), (148, 999, "yüksek")]
                },
                "calcium": {
                    "child": [(8.8, 10.8, "normal"), (0, 8.7, "düşük"), (10.9, 999, "yüksek")],
                    "adult": [(8.5, 10.5, "normal"), (0, 8.4, "düşük"), (10.6, 999, "yüksek")]
                },
                "magnesium": {
                    "child": [(1.7, 2.3, "normal"), (0, 1.69, "düşük"), (2.31, 999, "yüksek")],
                    "adult": [(1.7, 2.2, "normal"), (0, 1.69, "düşük"), (2.21, 999, "yüksek")]
                }
            },

            "vitamins": {
                "b12": {
                    "child": [(250, 1200, "normal"), (0, 249, "düşük"), (1201, 9999, "yüksek")],
                    "adult": [(200, 900, "normal"), (0, 199, "düşük"), (901, 9999, "yüksek")],
                    "elderly": [(180, 800, "normal"), (0, 179, "düşük"), (801, 9999, "yüksek")]
                },
                "folate": {
                    "child": [(5, 20, "normal"), (0, 4.9, "düşük")],
                    "adult": [(3, 17, "normal"), (0, 2.9, "düşük")]
                }
            },

            "neurometabolic": {
                "ammonia": {
                    "child": [(15, 45, "normal"), (46, 80, "hafif yüksek"), (81, 9999, "ciddi yüksek")],
                    "adult": [(15, 45, "normal"), (46, 80, "hafif yüksek"), (81, 9999, "ciddi yüksek")]
                },
                "lactate": {
                    "child": [(0.5, 2.0, "normal"), (2.1, 4.0, "hafif yüksek"), (4.1, 9999, "ciddi yüksek")],
                    "adult": [(0.5, 2.0, "normal"), (2.1, 4.0, "hafif yüksek"), (4.1, 9999, "ciddi yüksek")]
                }
            },

            "inflammation": {
                "crp": {
                    "child": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 9999, "yüksek")],
                    "adult": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 9999, "yüksek")]
                },
                "esr": {
                    "child": [(0, 10, "normal"), (11, 20, "hafif yüksek"), (21, 9999, "yüksek")],
                    "adult": [(0, 20, "normal"), (21, 40, "hafif yüksek"), (41, 9999, "yüksek")]
                }
            },

            "thyroid": {
                "tsh": {
                    "child": [(0.6, 4.8, "normal"), (0, 0.59, "düşük"), (4.9, 9999, "yüksek")],
                    "adult": [(0.4, 4.0, "normal"), (0, 0.39, "düşük"), (4.1, 9999, "yüksek")]
                }
            }
        },


        "imaging": {

            "brain_mri": {
                "white_matter_lesions": [(0, 0, "yok"), (1, 999, "var")],
                "cortical_atrophy": [(0, 0, "yok"), (1, 999, "var")],
                "hippocampal_volume_loss": [(0, 0, "yok"), (1, 999, "var")],
                "demyelination": [(0, 0, "yok"), (1, 999, "var")]
            },

            "brain_ct": {
                "hemorrhage": [(0, 0, "yok"), (1, 999, "var")],
                "ischemia": [(0, 0, "yok"), (1, 999, "var")],
                "mass_effect": [(0, 0, "yok"), (1, 999, "var")]
            },

            "doppler": {
                "carotid_stenosis": [(0, 0, "yok"), (1, 999, "var")],
                "vertebral_flow": [(0, 0, "normal"), (1, 999, "azalmış")]
            },

            "eeg": {
                "epileptiform_activity": [(0, 0, "yok"), (1, 999, "var")],
                "slowing": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "symptoms": {
                "headache": [(0, 0, "yok"), (1, 999, "var")],
                "dizziness": [(0, 0, "yok"), (1, 999, "var")],
                "seizure": [(0, 0, "yok"), (1, 999, "var")],
                "confusion": [(0, 0, "yok"), (1, 999, "var")],
                "weakness": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
            "motor_deficit": [(0, 0, "yok"), (1, 999, "var")],
            "sensory_loss": [(0, 0, "yok"), (1, 999, "var")],
            "reflex_changes": [(0, 0, "normal"), (1, 999, "anormal")],
            "gait_abnormality": [(0, 0, "yok"), (1, 999, "var")]
        },

        "risk_scores": {
            "stroke_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
            "dementia_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
        }
    }
},

    "pulmonology":{

        "lab": {

            "abg": {  # Arteriyel kan gazı
                "pH": {
                    "child": [(7.35, 7.45, "normal"), (0, 7.34, "asidoz"), (7.46, 999, "alkaloz")],
                    "adult": [(7.35, 7.45, "normal"), (0, 7.34, "asidoz"), (7.46, 999, "alkaloz")],
                    "elderly": [(7.34, 7.45, "normal"), (0, 7.33, "asidoz"), (7.46, 999, "alkaloz")]
                },
                "pO2": {
                    "child": [(80, 100, "normal"), (60, 79, "hafif düşük"), (40, 59, "orta düşük"),
                              (0, 39, "ciddi düşük")],
                    "adult": [(75, 100, "normal"), (60, 74, "hafif düşük"), (40, 59, "orta düşük"),
                              (0, 39, "ciddi düşük")],
                    "elderly": [(70, 95, "normal"), (50, 69, "hafif düşük"), (30, 49, "orta düşük"),
                                (0, 29, "ciddi düşük")]
                },
                "pCO2": {
                    "child": [(35, 45, "normal"), (0, 34, "düşük"), (46, 999, "yüksek")],
                    "adult": [(35, 45, "normal"), (0, 34, "düşük"), (46, 999, "yüksek")],
                    "elderly": [(35, 48, "normal"), (0, 34, "düşük"), (49, 999, "yüksek")]
                },
                "HCO3": {
                    "child": [(22, 26, "normal"), (0, 21.9, "düşük"), (26.1, 999, "yüksek")],
                    "adult": [(22, 26, "normal"), (0, 21.9, "düşük"), (26.1, 999, "yüksek")],
                    "elderly": [(23, 28, "normal"), (0, 22.9, "düşük"), (28.1, 999, "yüksek")]
                }
            },

            "oxygenation": {
                "spo2": {
                    "child": [(95, 100, "normal"), (90, 94, "hafif düşük"), (80, 89, "orta düşük"),
                              (0, 79, "ciddi düşük")],
                    "adult": [(94, 100, "normal"), (90, 93, "hafif düşük"), (80, 89, "orta düşük"),
                              (0, 79, "ciddi düşük")],
                    "elderly": [(92, 100, "normal"), (88, 91, "hafif düşük"), (80, 87, "orta düşük"),
                                (0, 79, "ciddi düşük")]
                }
            },

            "inflammation": {
                "crp": {
                    "child": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")],
                    "adult": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")]
                },
                "procalcitonin": {
                    "child": [(0, 0.5, "normal"), (0.51, 2, "orta"), (2.1, 999, "ciddi yüksek")],
                    "adult": [(0, 0.5, "normal"), (0.51, 2, "orta"), (2.1, 999, "ciddi yüksek")]
                }
            },

            "allergy_asthma": {
                "eosinophils": {
                    "child": [(0, 0.5, "normal"), (0.51, 1.0, "hafif yüksek"), (1.01, 999, "ciddi yüksek")],
                    "adult": [(0, 0.5, "normal"), (0.51, 1.0, "hafif yüksek"), (1.01, 999, "ciddi yüksek")]
                },
                "IgE": {
                    "child": [(0, 60, "normal"), (61, 200, "hafif yüksek"), (201, 9999, "ciddi yüksek")],
                    "adult": [(0, 100, "normal"), (101, 300, "hafif yüksek"), (301, 9999, "ciddi yüksek")]
                }
            },

            "cohb": {  # Karbonmonoksit zehirlenmesi
                "child": [(0, 2, "normal"), (3, 10, "hafif yüksek"), (11, 999, "ciddi yüksek")],
                "adult": [(0, 2, "normal"), (3, 10, "hafif yüksek"), (11, 999, "ciddi yüksek")]
            }
        },

        "imaging": {

            "chest_xray": {
                "infiltrates": [(0, 0, "yok"), (1, 999, "var")],
                "hyperinflation": [(0, 0, "yok"), (1, 999, "var")],
                "pleural_effusion": [(0, 0, "yok"), (1, 999, "var")]
            },

            "ct": {
                "ground_glass": [(0, 0, "yok"), (1, 999, "var")],
                "consolidation": [(0, 0, "yok"), (1, 999, "var")],
                "bronchiectasis": [(0, 0, "yok"), (1, 999, "var")],
                "emphysema": [(0, 0, "yok"), (1, 999, "var")]
            },

            "hrct": {
                "reticulation": [(0, 0, "yok"), (1, 999, "var")],
                "honeycombing": [(0, 0, "yok"), (1, 999, "var")],
                "traction_bronchiectasis": [(0, 0, "yok"), (1, 999, "var")]
            },

            "lung_ultrasound": {
                "b_lines": [(0, 0, "yok"), (1, 999, "var")],
                "pleural_thickening": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "symptoms": {
                "cough": [(0, 0, "yok"), (1, 999, "var")],
                "dyspnea": [(0, 0, "yok"), (1, 999, "var")],
                "wheezing": [(0, 0, "yok"), (1, 999, "var")],
                "chest_pain": [(0, 0, "yok"), (1, 999, "var")],
                "hemoptysis": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "rales": [(0, 0, "yok"), (1, 999, "var")],
                "ronchi": [(0, 0, "yok"), (1, 999, "var")],
                "wheezing": [(0, 0, "yok"), (1, 999, "var")],
                "cyanosis": [(0, 0, "yok"), (1, 999, "var")]
            },

            "spirometry": {
                "fev1": [(80, 100, "normal"), (50, 79, "orta düşük"), (0, 49, "ciddi düşük")],
                "fvc": [(80, 100, "normal"), (50, 79, "orta düşük"), (0, 49, "ciddi düşük")],
                "fev1_fvc_ratio": [(0.7, 1.0, "normal"), (0, 0.69, "obstrüksiyon")]
            },

            "risk_scores": {
                "copd_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "pneumonia_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
            }
        }
    },

    "dermatology":{

        "lab": {

            "allergy_panel": {
                "IgE": {
                    "child": [(0, 60, "normal"), (61, 200, "hafif yüksek"), (201, 9999, "ciddi yüksek")],
                    "adult": [(0, 100, "normal"), (101, 300, "hafif yüksek"), (301, 9999, "ciddi yüksek")]
                },
                "eosinophils": {
                    "child": [(0, 0.5, "normal"), (0.51, 1.0, "hafif yüksek"), (1.01, 999, "ciddi yüksek")],
                    "adult": [(0, 0.5, "normal"), (0.51, 1.0, "hafif yüksek"), (1.01, 999, "ciddi yüksek")]
                }
            },

            "autoimmune_panel": {
                "ana": {
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")]
                },
                "anti_dsDNA": {
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")]
                },
                "anti_ro": {
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")]
                },
                "anti_la": {
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")]
                }
            },

            "infection_panel": {
                "crp": {
                    "child": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")],
                    "adult": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")]
                },
                "esr": {
                    "child": [(0, 10, "normal"), (11, 20, "hafif yüksek"), (21, 999, "yüksek")],
                    "adult": [(0, 20, "normal"), (21, 40, "hafif yüksek"), (41, 999, "yüksek")]
                }
            },

            "vitamin_panel": {
                "vitamin_d": {
                    "child": [(20, 50, "normal"), (0, 19, "düşük"), (51, 999, "yüksek")],
                    "adult": [(20, 50, "normal"), (0, 19, "düşük"), (51, 999, "yüksek")]
                },
                "b12": {
                    "child": [(250, 1200, "normal"), (0, 249, "düşük"), (1201, 9999, "yüksek")],
                    "adult": [(200, 900, "normal"), (0, 199, "düşük"), (901, 9999, "yüksek")]
                }
            }
        },

        "imaging": {

            "dermoscopy": {
                "asymmetry": [(0, 0, "yok"), (1, 999, "var")],
                "border_irregularity": [(0, 0, "yok"), (1, 999, "var")],
                "color_variegation": [(0, 0, "yok"), (1, 999, "var")],
                "diameter_mm": [(0, 5, "normal"), (6, 999, "riskli")],
                "evolution": [(0, 0, "yok"), (1, 999, "var")]
            },

            "skin_ultrasound": {
                "dermal_thickness": [(0.5, 3.0, "normal"), (3.1, 999, "kalınlaşma")],
                "subcutaneous_edema": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "symptoms": {
                "itching": [(0, 0, "yok"), (1, 999, "var")],
                "burning": [(0, 0, "yok"), (1, 999, "var")],
                "pain": [(0, 0, "yok"), (1, 999, "var")],
                "dryness": [(0, 0, "yok"), (1, 999, "var")],
                "scaling": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "erythema": [(0, 0, "yok"), (1, 999, "var")],
                "edema": [(0, 0, "yok"), (1, 999, "var")],
                "vesicles": [(0, 0, "yok"), (1, 999, "var")],
                "pustules": [(0, 0, "yok"), (1, 999, "var")],
                "plaques": [(0, 0, "yok"), (1, 999, "var")]
            },

            "lesion_type": {
                "macule": [(0, 0, "yok"), (1, 999, "var")],
                "papule": [(0, 0, "yok"), (1, 999, "var")],
                "nodule": [(0, 0, "yok"), (1, 999, "var")],
                "patch": [(0, 0, "yok"), (1, 999, "var")],
                "plaque": [(0, 0, "yok"), (1, 999, "var")],
                "ulcer": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "melanoma_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "psoriasis_severity": [(0, 5, "hafif"), (6, 10, "orta"), (11, 999, "ciddi")]
            }
        }
    },

    "urology":{

        "lab": {

            "kidney_panel": {
                "creatinine": {
                    "child": [(0.3, 0.7, "normal"), (0, 0.29, "düşük"), (0.71, 999, "yüksek")],
                    "adult": [(0.6, 1.3, "normal"), (0, 0.59, "düşük"), (1.31, 999, "yüksek")],
                    "elderly": [(0.7, 1.4, "normal"), (0, 0.69, "düşük"), (1.41, 999, "yüksek")]
                },
                "gfr": {
                    "child": [(90, 999, "normal"), (60, 89, "hafif düşük"), (30, 59, "orta düşük"),
                              (0, 29, "ciddi düşük")],
                    "adult": [(90, 999, "normal"), (60, 89, "hafif düşük"), (30, 59, "orta düşük"),
                              (0, 29, "ciddi düşük")],
                    "elderly": [(60, 999, "normal"), (45, 59, "hafif düşük"), (30, 44, "orta düşük"),
                                (0, 29, "ciddi düşük")]
                }
            },

            "urine_panel": {
                "urine_protein": {
                    "child": [(0, 150, "normal"), (151, 300, "hafif proteinüri"), (301, 9999, "nefrotik aralık")],
                    "adult": [(0, 150, "normal"), (151, 300, "hafif proteinüri"), (301, 9999, "nefrotik aralık")]
                },
                "urine_rbc": {
                    "child": [(0, 3, "normal"), (4, 999, "hematüri")],
                    "adult": [(0, 3, "normal"), (4, 999, "hematüri")]
                },
                "urine_wbc": {
                    "child": [(0, 5, "normal"), (6, 999, "lökositüri")],
                    "adult": [(0, 5, "normal"), (6, 999, "lökositüri")]
                },
                "urine_ph": {
                    "child": [(5, 7, "normal"), (0, 4.9, "asidik"), (7.1, 999, "alkalik")],
                    "adult": [(5, 7, "normal"), (0, 4.9, "asidik"), (7.1, 999, "alkalik")]
                }
            },

            "prostate_panel": {
                "psa": {
                    "adult": [(0, 4, "normal"), (4.1, 10, "hafif yüksek"), (10.1, 999, "ciddi yüksek")],
                    "elderly": [(0, 6, "normal"), (6.1, 10, "hafif yüksek"), (10.1, 999, "ciddi yüksek")]
                },
                "free_psa_ratio": {
                    "adult": [(0.25, 1.0, "düşük risk"), (0.10, 0.24, "orta risk"), (0, 0.09, "yüksek risk")]
                }
            },

            "infection_panel": {
                "crp": {
                    "child": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")],
                    "adult": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 999, "yüksek")]
                },
                "procalcitonin": {
                    "child": [(0, 0.5, "normal"), (0.51, 2, "orta"), (2.1, 999, "ciddi yüksek")],
                    "adult": [(0, 0.5, "normal"), (0.51, 2, "orta"), (2.1, 999, "ciddi yüksek")]
                }
            }

        },

        "imaging": {

            "kidney_ultrasound": {
                "kidney_size": [(9, 12, "normal"), (0, 8.9, "küçük"), (12.1, 999, "büyük")],
                "hydronephrosis": [(0, 0, "yok"), (1, 1, "hafif"), (2, 2, "orta"), (3, 999, "ciddi")],
                "renal_cysts": [(0, 0, "yok"), (1, 999, "var")],
                "stones": [(0, 0, "yok"), (1, 999, "var")]
            },

            "bladder_ultrasound": {
                "post_void_residual": [(0, 50, "normal"), (51, 150, "orta"), (151, 999, "yüksek")],
                "bladder_wall_thickness": [(0, 3, "normal"), (3.1, 999, "kalınlaşma")]
            },

            "prostate_ultrasound": {
                "prostate_volume": {
                    "adult": [(15, 30, "normal"), (31, 50, "hafif büyük"), (51, 999, "ciddi büyük")]
                }
            },

            "ct_mri": {
                "renal_mass": [(0, 0, "yok"), (1, 999, "var")],
                "bladder_mass": [(0, 0, "yok"), (1, 999, "var")],
                "prostate_mass": [(0, 0, "yok"), (1, 999, "var")]
            },

            "doppler": {
                "renal_artery_stenosis": [(0, 0, "yok"), (1, 999, "var")],
                "testicular_flow": [(0, 0, "normal"), (1, 999, "azalmış")]
            }
        },

        "clinical": {

            "symptoms": {
                "dysuria": [(0, 0, "yok"), (1, 999, "var")],
                "frequency": [(0, 0, "yok"), (1, 999, "var")],
                "urgency": [(0, 0, "yok"), (1, 999, "var")],
                "flank_pain": [(0, 0, "yok"), (1, 999, "var")],
                "hematuria": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "cvat": [(0, 0, "yok"), (1, 999, "var")],  # costovertebral angle tenderness
                "suprapubic_tenderness": [(0, 0, "yok"), (1, 999, "var")],
                "testicular_swelling": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "uti_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "prostate_cancer_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "stone_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
            }
        }
    },

    "rheumatology":{

        "lab": {

            "autoimmune_panel": {

                "ana": {
                    "child": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "elderly": [(0, 0, "negatif"), (1, 999, "pozitif")]
                },

                "anti_dsDNA": {
                    "child": [(0, 30, "normal"), (31, 100, "hafif yüksek"), (101, 9999, "pozitif")],
                    "adult": [(0, 30, "normal"), (31, 100, "hafif yüksek"), (101, 9999, "pozitif")],
                    "elderly": [(0, 40, "normal"), (41, 120, "hafif yüksek"), (121, 9999, "pozitif")]
                },

                "anti_smith": {
                    "child": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "elderly": [(0, 0, "negatif"), (1, 999, "pozitif")]
                },

                "anti_ro": {
                    "child": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "elderly": [(0, 0, "negatif"), (1, 999, "pozitif")]
                },

                "anti_la": {
                    "child": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "elderly": [(0, 0, "negatif"), (1, 999, "pozitif")]
                }
            },

            "arthritis_panel": {

                "rf": {
                    "child": [(0, 14, "negatif"), (15, 30, "hafif pozitif"), (31, 9999, "pozitif")],
                    "adult": [(0, 14, "negatif"), (15, 30, "hafif pozitif"), (31, 9999, "pozitif")],
                    "elderly": [(0, 20, "negatif"), (21, 40, "hafif pozitif"), (41, 9999, "pozitif")]
                },

                "anti_ccp": {
                    "child": [(0, 20, "negatif"), (21, 39, "şüpheli"), (40, 9999, "pozitif")],
                    "adult": [(0, 20, "negatif"), (21, 39, "şüpheli"), (40, 9999, "pozitif")],
                    "elderly": [(0, 25, "negatif"), (26, 39, "şüpheli"), (40, 9999, "pozitif")]
                }
            },

            "vasculitis_panel": {

                "anca_p": {
                    "child": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "elderly": [(0, 0, "negatif"), (1, 999, "pozitif")]
                },

                "anca_c": {
                    "child": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "adult": [(0, 0, "negatif"), (1, 999, "pozitif")],
                    "elderly": [(0, 0, "negatif"), (1, 999, "pozitif")]
                }
            },

            "inflammation": {

                "crp": {
                    "child": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 50, "orta"), (51, 9999, "ciddi")],
                    "adult": [(0, 5, "normal"), (6, 20, "hafif yüksek"), (21, 50, "orta"), (51, 9999, "ciddi")],
                    "elderly": [(0, 8, "normal"), (9, 25, "hafif yüksek"), (26, 9999, "yüksek")]
                },

                "esr": {
                    "child": [(0, 10, "normal"), (11, 20, "hafif yüksek"), (21, 9999, "yüksek")],
                    "adult": [(0, 20, "normal"), (21, 40, "hafif yüksek"), (41, 9999, "yüksek")],
                    "elderly": [(0, 30, "normal"), (31, 50, "hafif yüksek"), (51, 9999, "yüksek")]
                }
            },

            "ferritin": {
                "child": [(20, 200, "normal"), (201, 9999, "yüksek")],
                "adult": [(30, 400, "normal"), (401, 1000, "hafif yüksek"), (1001, 9999, "ciddi yüksek")],
                "elderly": [(40, 500, "normal"), (501, 9999, "yüksek")]
            },

            "uric_acid": {
                "child": [(3.0, 5.5, "normal"), (5.6, 7.0, "hafif yüksek"), (7.1, 9999, "gut riski")],
                "adult": [(3.5, 7.2, "normal"), (7.3, 9.0, "hafif yüksek"), (9.1, 9999, "gut")],
                "elderly": [(3.5, 7.5, "normal"), (7.6, 9.5, "hafif yüksek"), (9.6, 9999, "gut")]
            },

            "serum_amyloid_a": {
                "child": [(0, 6, "normal"), (7, 100, "yüksek"), (101, 9999, "çok yüksek")],
                "adult": [(0, 6, "normal"), (7, 100, "yüksek"), (101, 9999, "çok yüksek")],
                "elderly": [(0, 8, "normal"), (9, 120, "yüksek"), (121, 9999, "çok yüksek")]
            }
        },

        "imaging": {

            "joint_ultrasound": {
                "synovitis": [(0, 0, "yok"), (1, 999, "var")],
                "effusion": [(0, 0, "yok"), (1, 999, "var")],
                "erosions": [(0, 0, "yok"), (1, 999, "var")]
            },

            "mri": {
                "bone_marrow_edema": [(0, 0, "yok"), (1, 999, "var")],
                "cartilage_loss": [(0, 0, "yok"), (1, 999, "var")],
                "tendon_inflammation": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "symptoms": {
                "joint_pain": [(0, 0, "yok"), (1, 999, "var")],
                "morning_stiffness": [(0, 0, "yok"), (1, 999, "var")],
                "fatigue": [(0, 0, "yok"), (1, 999, "var")],
                "rash": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "swollen_joints": [(0, 0, "yok"), (1, 999, "var")],
                "tender_joints": [(0, 0, "yok"), (1, 999, "var")],
                "vasculitic_lesions": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "ra_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "sle_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "vasculitis_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
            }
        }
    },

    "cardiovascular_surgery":{
        "lab": {

            "cardiac_preop": {
                "hgb": {
                    "child":     [(11.5, 15.5, "normal"), (0, 11.4, "düşük")],
                    "adult":     [(13.5, 17.5, "normal"), (0, 13.4, "düşük")],
                    "elderly":   [(12.5, 16.5, "normal"), (0, 12.4, "düşük")]
                },
                "platelets": {
                    "child":     [(150, 450, "normal"), (0, 149, "düşük")],
                    "adult":     [(150, 450, "normal"), (0, 149, "düşük")],
                    "elderly":   [(150, 450, "normal"), (0, 149, "düşük")]
                },
                "inr": {
                    "child":     [(0.8, 1.2, "normal"), (1.3, 999, "yüksek")],
                    "adult":     [(0.8, 1.2, "normal"), (1.3, 999, "yüksek")],
                    "elderly":   [(0.8, 1.3, "normal"), (1.31, 999, "yüksek")]
                }
            },

            "cardiac_postop": {
                "lactate": {
                    "child":     [(0.5, 2.0, "normal"), (2.1, 4.0, "orta"), (4.1, 999, "ciddi")],
                    "adult":     [(0.5, 2.0, "normal"), (2.1, 4.0, "orta"), (4.1, 999, "ciddi")],
                    "elderly":   [(0.5, 2.5, "normal"), (2.6, 4.0, "orta"), (4.1, 999, "ciddi")]
                },
                "troponin": {
                    "child":     [(0, 0.04, "normal"), (0.05, 999, "yüksek")],
                    "adult":     [(0, 0.04, "normal"), (0.05, 999, "yüksek")],
                    "elderly":   [(0, 0.05, "normal"), (0.06, 999, "yüksek")]
                },
                "crp": {
                    "child":     [(0, 5, "normal"), (6, 20, "hafif"), (21, 999, "yüksek")],
                    "adult":     [(0, 5, "normal"), (6, 20, "hafif"), (21, 999, "yüksek")],
                    "elderly":   [(0, 8, "normal"), (9, 25, "hafif"), (26, 999, "yüksek")]
                }
            },

            "vascular_panel": {
                "d_dimer": {
                    "child":     [(0, 0.5, "normal"), (0.51, 1.0, "hafif"), (1.01, 999, "yüksek")],
                    "adult":     [(0, 0.5, "normal"), (0.51, 1.0, "hafif"), (1.01, 999, "yüksek")],
                    "elderly":   [(0, 0.7, "normal"), (0.71, 1.2, "hafif"), (1.21, 999, "yüksek")]
                },
                "fibrinogen": {
                    "child":     [(200, 400, "normal"), (401, 999, "yüksek")],
                    "adult":     [(200, 400, "normal"), (401, 999, "yüksek")],
                    "elderly":   [(250, 450, "normal"), (451, 999, "yüksek")]
                }
            }
        },

        "imaging": {

            "echocardiography": {
                "ef_percent": {
                    "child":     [(55, 75, "normal"), (40, 54, "orta"), (0, 39, "ciddi")],
                    "adult":     [(55, 70, "normal"), (40, 54, "orta"), (0, 39, "ciddi")],
                    "elderly":   [(50, 65, "normal"), (40, 49, "orta"), (0, 39, "ciddi")]
                },
                "lv_hypertrophy": [(0, 0, "yok"), (1, 999, "var")],
                "valve_stenosis": [(0, 0, "yok"), (1, 999, "var")],
                "valve_regurgitation": [(0, 0, "yok"), (1, 999, "var")]
            },

            "ct_angiography": {
                "coronary_stenosis": [(0, 0, "yok"), (1, 999, "var")],
                "aortic_aneurysm": [(0, 0, "yok"), (1, 999, "var")],
                "pulmonary_embolism": [(0, 0, "yok"), (1, 999, "var")]
            },

            "vascular_doppler": {
                "carotid_stenosis": [(0, 0, "yok"), (1, 999, "var")],
                "peripheral_artery_disease": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "symptoms": {
                "chest_pain": [(0, 0, "yok"), (1, 999, "var")],
                "dyspnea": [(0, 0, "yok"), (1, 999, "var")],
                "claudication": [(0, 0, "yok"), (1, 999, "var")],
                "palpitations": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "edema": [(0, 0, "yok"), (1, 999, "var")],
                "cyanosis": [(0, 0, "yok"), (1, 999, "var")],
                "murmur": [(0, 0, "yok"), (1, 999, "var")],
                "weak_pulses": [(0, 0, "yok"), (1, 999, "var")]
            },

            "hemodynamics": {
                "map": [(70, 100, "normal"), (101, 120, "hafif yüksek"), (121, 999, "ciddi yüksek"), (0, 69, "düşük")],
                "cardiac_output": [(4, 8, "normal"), (0, 3.9, "düşük"), (8.1, 999, "yüksek")]
            },

            "risk_scores": {
                "cabg_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "vascular_surgery_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
            }
        },

        "surgery": {

            "procedures": {
                "cabg": [(0, 0, "yapılmadı"), (1, 999, "yapıldı")],
                "valve_replacement": [(0, 0, "yok"), (1, 999, "var")],
                "aortic_repair": [(0, 0, "yok"), (1, 999, "var")],
                "vascular_bypass": [(0, 0, "yok"), (1, 999, "var")]
            },

            "postop_complications": {
                "bleeding": [(0, 0, "yok"), (1, 999, "var")],
                "infection": [(0, 0, "yok"), (1, 999, "var")],
                "arrhythmia": [(0, 0, "yok"), (1, 999, "var")],
                "renal_failure": [(0, 0, "yok"), (1, 999, "var")]
            }
        }

    },

    "orthopedics":{
        "lab": {

            "bone_metabolism": {
                "calcium": {
                    "child":     [(8.8, 10.8, "normal"), (0, 8.7, "düşük"), (10.9, 999, "yüksek")],
                    "adult":     [(8.5, 10.5, "normal"), (0, 8.4, "düşük"), (10.6, 999, "yüksek")],
                    "elderly":   [(8.2, 10.2, "normal"), (0, 8.1, "düşük"), (10.3, 999, "yüksek")]
                },
                "vitamin_d": {
                    "child":     [(20, 50, "normal"), (0, 19, "düşük"), (51, 999, "yüksek")],
                    "adult":     [(20, 50, "normal"), (0, 19, "düşük"), (51, 999, "yüksek")],
                    "elderly":   [(25, 60, "normal"), (0, 24, "düşük"), (61, 999, "yüksek")]
                },
                "alk_phosphatase": {
                    "child":     [(150, 400, "normal"), (401, 999, "yüksek")],  # büyüme dönemi
                    "adult":     [(40, 130, "normal"), (131, 999, "yüksek")],
                    "elderly":   [(40, 150, "normal"), (151, 999, "yüksek")]
                }
            },

            "inflammation": {
                "crp": {
                    "child":     [(0, 5, "normal"), (6, 20, "hafif"), (21, 999, "yüksek")],
                    "adult":     [(0, 5, "normal"), (6, 20, "hafif"), (21, 999, "yüksek")],
                    "elderly":   [(0, 8, "normal"), (9, 25, "hafif"), (26, 999, "yüksek")]
                },
                "esr": {
                    "child":     [(0, 10, "normal"), (11, 20, "hafif"), (21, 999, "yüksek")],
                    "adult":     [(0, 20, "normal"), (21, 40, "hafif"), (41, 999, "yüksek")],
                    "elderly":   [(0, 30, "normal"), (31, 50, "hafif"), (51, 999, "yüksek")]
                }
            },

            "muscle_panel": {
                "ck": {
                    "child":     [(50, 250, "normal"), (251, 9999, "yüksek")],
                    "adult":     [(30, 200, "normal"), (201, 9999, "yüksek")],
                    "elderly":   [(20, 180, "normal"), (181, 9999, "yüksek")]
                }
            }
        },

        "imaging": {

            "xray": {
                "fracture": [(0, 0, "yok"), (1, 999, "var")],
                "dislocation": [(0, 0, "yok"), (1, 999, "var")],
                "osteoporosis_signs": [(0, 0, "yok"), (1, 999, "var")],
                "growth_plate_open": {
                    "child": [(1, 1, "açık")],
                    "adult": [(0, 0, "kapalı")]
                }
            },

            "ct": {
                "complex_fracture": [(0, 0, "yok"), (1, 999, "var")],
                "bone_fragmentation": [(0, 0, "yok"), (1, 999, "var")],
                "joint_surface_damage": [(0, 0, "yok"), (1, 999, "var")]
            },

            "mri": {
                "ligament_tear": [(0, 0, "yok"), (1, 999, "var")],
                "meniscus_tear": [(0, 0, "yok"), (1, 999, "var")],
                "bone_marrow_edema": [(0, 0, "yok"), (1, 999, "var")],
                "muscle_strain": [(0, 0, "yok"), (1, 999, "var")]
            },

            "ultrasound": {
                "tendonitis": [(0, 0, "yok"), (1, 999, "var")],
                "bursitis": [(0, 0, "yok"), (1, 999, "var")],
                "effusion": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "symptoms": {
                "joint_pain": [(0, 0, "yok"), (1, 999, "var")],
                "muscle_pain": [(0, 0, "yok"), (1, 999, "var")],
                "limited_motion": [(0, 0, "yok"), (1, 999, "var")],
                "swelling": [(0, 0, "yok"), (1, 999, "var")],
                "instability": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "tenderness": [(0, 0, "yok"), (1, 999, "var")],
                "crepitus": [(0, 0, "yok"), (1, 999, "var")],
                "muscle_strength": [(5, 5, "normal"), (4, 4, "hafif zayıf"), (3, 3, "orta zayıf"), (0, 2, "ciddi zayıf")],
                "gait_abnormality": [(0, 0, "yok"), (1, 999, "var")]
            },

            "functional_tests": {
                "lachman_test": [(0, 0, "negatif"), (1, 999, "pozitif")],
                "mcmurray_test": [(0, 0, "negatif"), (1, 999, "pozitif")],
                "squeeze_test": [(0, 0, "negatif"), (1, 999, "pozitif")]
            },

            "risk_scores": {
                "fracture_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "osteoporosis_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "sports_injury_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
            }
        }
    },

    "psychiatry":{
        "lab": {

            "neurochemistry": {
                "tsh": {
                    "child":     [(0.6, 4.8, "normal"), (0, 0.59, "düşük"), (4.9, 999, "yüksek")],
                    "adult":     [(0.4, 4.0, "normal"), (0, 0.39, "düşük"), (4.1, 999, "yüksek")],
                    "elderly":   [(0.4, 5.0, "normal"), (0, 0.39, "düşük"), (5.1, 999, "yüksek")]
                },
                "vitamin_b12": {
                    "child":     [(250, 1200, "normal"), (0, 249, "düşük")],
                    "adult":     [(200, 900, "normal"), (0, 199, "düşük")],
                    "elderly":   [(180, 800, "normal"), (0, 179, "düşük")]
                },
                "folate": {
                    "child":     [(5, 20, "normal"), (0, 4.9, "düşük")],
                    "adult":     [(3, 17, "normal"), (0, 2.9, "düşük")]
                },
                "vitamin_d": {
                    "child":     [(20, 50, "normal"), (0, 19, "düşük")],
                    "adult":     [(20, 50, "normal"), (0, 19, "düşük")],
                    "elderly":   [(25, 60, "normal"), (0, 24, "düşük")]
                }
            },

            "inflammation": {
                "crp": {
                    "child":     [(0, 5, "normal"), (6, 20, "hafif"), (21, 999, "yüksek")],
                    "adult":     [(0, 5, "normal"), (6, 20, "hafif"), (21, 999, "yüksek")],
                    "elderly":   [(0, 8, "normal"), (9, 25, "hafif"), (26, 999, "yüksek")]
                },
                "esr": {
                    "child":     [(0, 10, "normal"), (11, 20, "hafif"), (21, 999, "yüksek")],
                    "adult":     [(0, 20, "normal"), (21, 40, "hafif"), (41, 999, "yüksek")],
                    "elderly":   [(0, 30, "normal"), (31, 50, "hafif"), (51, 999, "yüksek")]
                }
            },

            "metabolic": {
                "glucose": {
                    "child":     [(70, 99, "normal"), (100, 125, "prediyabet"), (126, 999, "diyabet")],
                    "adult":     [(70, 99, "normal"), (100, 125, "prediyabet"), (126, 999, "diyabet")],
                    "elderly":   [(70, 110, "normal"), (111, 125, "prediyabet"), (126, 999, "diyabet")]
                }
            }
        },

        "imaging": {

            "brain_mri": {
                "atrophy": [(0, 0, "yok"), (1, 999, "var")],
                "white_matter_changes": [(0, 0, "yok"), (1, 999, "var")],
                "hippocampal_volume_loss": [(0, 0, "yok"), (1, 999, "var")],
                "tumor": [(0, 0, "yok"), (1, 999, "var")]
            },

            "brain_ct": {
                "hemorrhage": [(0, 0, "yok"), (1, 999, "var")],
                "ischemia": [(0, 0, "yok"), (1, 999, "var")],
                "mass_effect": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "symptoms": {

                "mood": {
                    "depressed_mood": [(0, 0, "yok"), (1, 999, "var")],
                    "anhedonia": [(0, 0, "yok"), (1, 999, "var")],
                    "elevated_mood": [(0, 0, "yok"), (1, 999, "var")],
                    "irritability": [(0, 0, "yok"), (1, 999, "var")]
                },

                "anxiety": {
                    "excessive_worry": [(0, 0, "yok"), (1, 999, "var")],
                    "panic_attacks": [(0, 0, "yok"), (1, 999, "var")],
                    "phobias": [(0, 0, "yok"), (1, 999, "var")]
                },

                "psychosis": {
                    "hallucinations": [(0, 0, "yok"), (1, 999, "var")],
                    "delusions": [(0, 0, "yok"), (1, 999, "var")],
                    "disorganized_thought": [(0, 0, "yok"), (1, 999, "var")]
                },

                "adhd": {
                    "inattention": [(0, 0, "yok"), (1, 999, "var")],
                    "hyperactivity": [(0, 0, "yok"), (1, 999, "var")],
                    "impulsivity": [(0, 0, "yok"), (1, 999, "var")]
                },

                "autism": {
                    "social_deficit": [(0, 0, "yok"), (1, 999, "var")],
                    "restricted_interests": [(0, 0, "yok"), (1, 999, "var")],
                    "sensory_issues": [(0, 0, "yok"), (1, 999, "var")]
                }
            },

            "mental_status_exam": {
                "orientation": [(1, 1, "tam"), (0, 0, "bozuk")],
                "memory": [(1, 1, "normal"), (0, 0, "bozuk")],
                "attention": [(1, 1, "normal"), (0, 0, "bozuk")],
                "insight": [(1, 1, "var"), (0, 0, "yok")],
                "judgment": [(1, 1, "normal"), (0, 0, "bozuk")]
            },

            "risk_assessment": {
                "suicide_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "violence_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "substance_abuse_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
            }
        },

        "psych_scales": {

            "depression": {
                "phq9": [(0, 4, "minimal"), (5, 9, "hafif"), (10, 14, "orta"), (15, 19, "orta-şiddetli"), (20, 27, "şiddetli")]
            },

            "anxiety": {
                "gad7": [(0, 4, "minimal"), (5, 9, "hafif"), (10, 14, "orta"), (15, 21, "şiddetli")]
            },

            "bipolar": {
                "mdq": [(0, 6, "negatif"), (7, 13, "pozitif")]
            },

            "psychosis": {
                "bprs": [(18, 31, "hafif"), (32, 53, "orta"), (54, 126, "şiddetli")]
            },

            "dementia": {
                "mmse": [(24, 30, "normal"), (18, 23, "hafif"), (10, 17, "orta"), (0, 9, "ciddi")]
            }
        }
    },

    "endocrine_surgery":{
        "lab": {

            "thyroid_panel": {
                "tsh": {
                    "child":     [(0.6, 4.8, "normal"), (0, 0.59, "düşük"), (4.9, 999, "yüksek")],
                    "adult":     [(0.4, 4.0, "normal"), (0, 0.39, "düşük"), (4.1, 999, "yüksek")],
                    "elderly":   [(0.4, 5.0, "normal"), (0, 0.39, "düşük"), (5.1, 999, "yüksek")]
                },
                "ft4": {
                    "child":     [(0.9, 1.8, "normal"), (0, 0.89, "düşük"), (1.81, 999, "yüksek")],
                    "adult":     [(0.8, 1.8, "normal"), (0, 0.79, "düşük"), (1.81, 999, "yüksek")]
                },
                "thyroglobulin": {
                    "adult": [(0, 30, "normal"), (31, 9999, "yüksek")]  # cerrahi sonrası takip
                }
            },

            "parathyroid_panel": {
                "pth": {
                    "child":     [(10, 65, "normal"), (0, 9.9, "düşük"), (65.1, 999, "yüksek")],
                    "adult":     [(15, 65, "normal"), (0, 14.9, "düşük"), (65.1, 999, "yüksek")],
                    "elderly":   [(20, 70, "normal"), (0, 19.9, "düşük"), (70.1, 999, "yüksek")]
                },
                "calcium": {
                    "child":     [(8.8, 10.8, "normal"), (0, 8.7, "düşük"), (10.9, 999, "yüksek")],
                    "adult":     [(8.5, 10.5, "normal"), (0, 8.4, "düşük"), (10.6, 999, "yüksek")],
                    "elderly":   [(8.2, 10.2, "normal"), (0, 8.1, "düşük"), (10.3, 999, "yüksek")]
                },
                "phosphorus": {
                    "child":     [(3.5, 6.0, "normal"), (0, 3.49, "düşük"), (6.1, 999, "yüksek")],
                    "adult":     [(2.5, 4.5, "normal"), (0, 2.49, "düşük"), (4.6, 999, "yüksek")]
                }
            },

            "adrenal_panel": {
                "cortisol": {
                    "child":     [(6, 23, "normal"), (0, 5.9, "düşük"), (24, 999, "yüksek")],
                    "adult":     [(6, 23, "normal"), (0, 5.9, "düşük"), (24, 999, "yüksek")]
                },
                "acth": {
                    "child":     [(10, 60, "normal"), (0, 9.9, "düşük"), (61, 999, "yüksek")],
                    "adult":     [(10, 60, "normal"), (0, 9.9, "düşük"), (61, 999, "yüksek")]
                },
                "metanephrines": {
                    "adult": [(0, 57, "normal"), (58, 9999, "yüksek")]  # feokromositoma
                }
            },

            "neuroendocrine_panel": {
                "chromogranin_a": {
                    "adult": [(0, 100, "normal"), (101, 9999, "yüksek")]
                },
                "insulin": {
                    "adult": [(2, 25, "normal"), (26, 9999, "yüksek")]
                },
                "glucagon": {
                    "adult": [(50, 150, "normal"), (151, 9999, "yüksek")]
                }
            }
        },

        "imaging": {

            "thyroid_ultrasound": {
                "thyroid_nodule": [(0, 0, "yok"), (1, 999, "var")],
                "microcalcifications": [(0, 0, "yok"), (1, 999, "var")],
                "vascularity": [(0, 0, "normal"), (1, 999, "artmış")]
            },

            "parathyroid_ultrasound": {
                "parathyroid_adenoma": [(0, 0, "yok"), (1, 999, "var")]
            },

            "adrenal_ct_mri": {
                "adrenal_mass": [(0, 0, "yok"), (1, 999, "var")],
                "pheochromocytoma_signs": [(0, 0, "yok"), (1, 999, "var")]
            },

            "pet_ct": {
                "fdg_uptake": [(0, 2.5, "normal"), (2.6, 4.9, "orta"), (5, 999, "yüksek")]
            }
        },

        "clinical": {

            "symptoms": {
                "neck_mass": [(0, 0, "yok"), (1, 999, "var")],
                "hoarseness": [(0, 0, "yok"), (1, 999, "var")],
                "heat_intolerance": [(0, 0, "yok"), (1, 999, "var")],
                "palpitations": [(0, 0, "yok"), (1, 999, "var")],
                "muscle_weakness": [(0, 0, "yok"), (1, 999, "var")]
            },

            "physical_exam": {
                "thyroid_enlargement": [(0, 0, "yok"), (1, 999, "var")],
                "lymphadenopathy": [(0, 0, "yok"), (1, 999, "var")],
                "tracheal_deviation": [(0, 0, "yok"), (1, 999, "var")]
            },

            "risk_scores": {
                "thyroid_cancer_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "hyperparathyroidism_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")],
                "adrenal_tumor_risk": [(0, 5, "düşük"), (6, 10, "orta"), (11, 999, "yüksek")]
            }
        },

        "surgery": {

            "procedures": {
                "thyroidectomy": [(0, 0, "yok"), (1, 999, "var")],
                "parathyroidectomy": [(0, 0, "yok"), (1, 999, "var")],
                "adrenalectomy": [(0, 0, "yok"), (1, 999, "var")],
                "neuroendocrine_tumor_resection": [(0, 0, "yok"), (1, 999, "var")]
            },

            "postop_complications": {
                "hypocalcemia": [(0, 0, "yok"), (1, 999, "var")],
                "recurrent_laryngeal_nerve_injury": [(0, 0, "yok"), (1, 999, "var")],
                "hematoma": [(0, 0, "yok"), (1, 999, "var")],
                "adrenal_crisis": [(0, 0, "yok"), (1, 999, "var")]
            }
        }
    },

    "anesthesia_icu":{
        "lab": {

            "abg": {
                "pH": {
                    "child":     [(7.35, 7.45, "normal"), (0, 7.34, "asidoz"), (7.46, 999, "alkaloz")],
                    "adult":     [(7.35, 7.45, "normal"), (0, 7.34, "asidoz"), (7.46, 999, "alkaloz")],
                    "elderly":   [(7.34, 7.45, "normal"), (0, 7.33, "asidoz"), (7.46, 999, "alkaloz")]
                },
                "pO2": {
                    "child":     [(80, 100, "normal"), (60, 79, "hafif düşük"), (40, 59, "orta"), (0, 39, "ciddi")],
                    "adult":     [(75, 100, "normal"), (60, 74, "hafif düşük"), (40, 59, "orta"), (0, 39, "ciddi")],
                    "elderly":   [(70, 95, "normal"), (50, 69, "hafif düşük"), (30, 49, "orta"), (0, 29, "ciddi")]
                },
                "pCO2": {
                    "child":     [(35, 45, "normal"), (0, 34, "düşük"), (46, 999, "yüksek")],
                    "adult":     [(35, 45, "normal"), (0, 34, "düşük"), (46, 999, "yüksek")],
                    "elderly":   [(35, 48, "normal"), (0, 34, "düşük"), (49, 999, "yüksek")]
                },
                "HCO3": {
                    "child":     [(22, 26, "normal"), (0, 21.9, "düşük"), (26.1, 999, "yüksek")],
                    "adult":     [(22, 26, "normal"), (0, 21.9, "düşük"), (26.1, 999, "yüksek")],
                    "elderly":   [(23, 28, "normal"), (0, 22.9, "düşük"), (28.1, 999, "yüksek")]
                }
            },

            "lactate": {
                "child":     [(0.5, 2.0, "normal"), (2.1, 4.0, "orta"), (4.1, 999, "ciddi")],
                "adult":     [(0.5, 2.0, "normal"), (2.1, 4.0, "orta"), (4.1, 999, "ciddi")],
                "elderly":   [(0.5, 2.5, "normal"), (2.6, 4.0, "orta"), (4.1, 999, "ciddi")]
            },

            "electrolytes": {
                "sodium": {
                    "child":     [(135, 145, "normal"), (0, 134, "düşük"), (146, 999, "yüksek")],
                    "adult":     [(135, 145, "normal"), (0, 134, "düşük"), (146, 999, "yüksek")],
                    "elderly":   [(135, 147, "normal"), (0, 134, "düşük"), (148, 999, "yüksek")]
                },
                "potassium": {
                    "child":     [(3.5, 5.0, "normal"), (0, 3.4, "düşük"), (5.1, 999, "yüksek")],
                    "adult":     [(3.5, 5.0, "normal"), (0, 3.4, "düşük"), (5.1, 999, "yüksek")],
                    "elderly":   [(3.5, 5.2, "normal"), (0, 3.4, "düşük"), (5.21, 999, "yüksek")]
                },
                "magnesium": {
                    "child":     [(1.7, 2.3, "normal"), (0, 1.69, "düşük"), (2.31, 999, "yüksek")],
                    "adult":     [(1.7, 2.2, "normal"), (0, 1.69, "düşük"), (2.21, 999, "yüksek")]
                }
            },

            "coagulation": {
                "inr": {
                    "child":     [(0.8, 1.2, "normal"), (1.3, 999, "yüksek")],
                    "adult":     [(0.8, 1.2, "normal"), (1.3, 999, "yüksek")],
                    "elderly":   [(0.8, 1.3, "normal"), (1.31, 999, "yüksek")]
                },
                "ptt": {
                    "adult": [(25, 35, "normal"), (36, 999, "uzamış")]
                }
            }
        },

        "imaging": {

            "chest_xray": {
                "infiltrates": [(0, 0, "yok"), (1, 999, "var")],
                "effusion": [(0, 0, "yok"), (1, 999, "var")],
                "tube_position": [(0, 0, "doğru"), (1, 999, "yanlış")]
            },

            "ct": {
                "pulmonary_embolism": [(0, 0, "yok"), (1, 999, "var")],
                "pneumonia": [(0, 0, "yok"), (1, 999, "var")],
                "brain_edema": [(0, 0, "yok"), (1, 999, "var")]
            }
        },

        "clinical": {

            "consciousness": {
                "gcs": [(13, 15, "normal"), (9, 12, "orta"), (3, 8, "ciddi")]
            },

            "sedation": {
                "rass": [(0, 0, "uyumlu"), (-1, -2, "hafif sedasyon"), (-3, -5, "derin sedasyon"), (1, 4, "ajite")]
            },

            "pain": {
                "nrs": [(0, 3, "hafif"), (4, 6, "orta"), (7, 10, "şiddetli")]
            },

            "neuromuscular": {
                "train_of_four": [(0.9, 1.0, "normal"), (0.4, 0.89, "kısmi blok"), (0, 0.39, "tam blok")]
            }
        },

        "ventilation": {

            "ventilator_settings": {
                "tidal_volume_mlkg": [(6, 8, "normal"), (0, 5.9, "düşük"), (8.1, 999, "yüksek")],
                "peep": [(5, 10, "normal"), (0, 4.9, "düşük"), (11, 999, "yüksek")],
                "fio2": [(21, 60, "normal"), (61, 100, "yüksek")]
            },

            "oxygenation": {
                "spo2": {
                    "child":     [(95, 100, "normal"), (90, 94, "hafif"), (80, 89, "orta"), (0, 79, "ciddi")],
                    "adult":     [(94, 100, "normal"), (90, 93, "hafif"), (80, 89, "orta"), (0, 79, "ciddi")],
                    "elderly":   [(92, 100, "normal"), (88, 91, "hafif"), (80, 87, "orta"), (0, 79, "ciddi")]
                }
            }
        },

        "hemodynamics": {

            "map": [(70, 100, "normal"), (101, 120, "hafif yüksek"), (121, 999, "ciddi yüksek"), (0, 69, "düşük")],

            "cardiac_output": [(4, 8, "normal"), (0, 3.9, "düşük"), (8.1, 999, "yüksek")],

            "cvp": [(5, 10, "normal"), (0, 4.9, "düşük"), (10.1, 999, "yüksek")],

            "vasopressor_need": [(0, 0, "yok"), (1, 999, "var")]
        },

        "drugs": {

            "sedation": {
                "propofol": [(0, 0, "yok"), (1, 999, "veriliyor")],
                "midazolam": [(0, 0, "yok"), (1, 999, "veriliyor")]
            },

            "analgesia": {
                "fentanyl": [(0, 0, "yok"), (1, 999, "veriliyor")],
                "morphine": [(0, 0, "yok"), (1, 999, "veriliyor")]
            },

            "paralytics": {
                "rocuronium": [(0, 0, "yok"), (1, 999, "veriliyor")],
                "cisatracurium": [(0, 0, "yok"), (1, 999, "veriliyor")]
            },

            "vasopressors": {
                "norepinephrine": [(0, 0, "yok"), (1, 999, "veriliyor")],
                "vasopressin": [(0, 0, "yok"), (1, 999, "veriliyor")],
                "epinephrine": [(0, 0, "yok"), (1, 999, "veriliyor")]
            }
        }
    }

}

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
    "anesthesia_icu"
]


def get_branch_module(branch_name):
    if branch_name in REFERENCE_RANGES:
        return REFERENCE_RANGES[branch_name]
    return None





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
        self.root.geometry("1400x950")
        self.root.state("zoomed")
        self.root.title("Data Analysing Program")
        self.logic = DataAnalyseLogic()
        self.current_module = None

        #---- Sol taraf----
        self.frame_left = tk.Frame(self.root)
        self.frame_left.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)

        # ---Orta taraf----
        self.frame_center = tk.Frame(self.root)
        self.frame_center.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # ---SAĞ TARAF---
        self.frame_right = tk.Frame(self.root)
        self.frame_right.grid(row=0, column=2, sticky="nsew", pady=10, padx=10)

        # --Enties dict---
        self.entries = {}

        # --- Root'u Responsive Yap
        self.root.grid_rowconfigure(0,weight=1)
        self.root.grid_columnconfigure(0,weight=0)
        self.root.grid_columnconfigure(1,weight=1)
        self.root.grid_columnconfigure(2,weight=2)

        #--- frame_center responsive ---
        self.frame_center.grid_rowconfigure(0,weight=1)
        self.frame_center.grid_columnconfigure(0,weight=1)

        # ---frame_right responsive yap
        for i in range(0, 6):
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

        self.list_features = tk.Listbox(self.frame_center, selectmode='multiple', height=10)
        self.list_features.grid(row=6, column=0, pady=5)

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

        # ----Sağ panel: 3 ana bölüm----
        self.branch_frame = tk.LabelFrame(self.frame_right,text="Branş Seçimi")
        self.branch_frame.grid(row=2, column=0, sticky="nsew", pady=10, padx=10)

        # AI sonuçları
        self.ai_frame = tk.LabelFrame(self.frame_right,text="AI Sonuçları")
        self.ai_frame.grid(row=3, column=0, sticky="nsew", pady=10, padx=10)

        #Test alanları frame
        self.test_frame = tk.LabelFrame(self.frame_right,text="Test Alanları")
        self.test_frame.grid(row=4, column=0, sticky="nsew", pady=10, padx=10)

        #--- SAĞ panel: Filtreleme + AI
        self.filter_frame = tk.LabelFrame(self.frame_right,text="Filtreleme + AI")
        self.filter_frame.grid(row=5,column=0,sticky="nsew",pady=10)

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

        self.btn_ai = tk.Button(
            self.filter_frame,
            text="AI Analiz Yap",
            command=self.ai_analysis_button
        )
        self.btn_ai.grid(row=6,column=0,padx=10,pady=10)

        # Türkce AI Yorum
        self.ai_text = tk.Text(
            self.filter_frame,
            height=10,
            width=40,
            font=("Arial",11),
            wrap="word"
        )

        self.ai_text.grid(row=7,column=0,padx=10,pady=10)

        scroll = tk.Scrollbar(self.filter_frame,command=self.ai_text.yview)
        scroll.grid(row=7,column=1,sticky="nsew")
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


    def create_test_fields(self,module):
        #Önce eski test alanlarını temizle
        for widget in self.test_frame.winfo_children():
            widget.destroy()

        #Entries sözlüğünü sıfırla
        self.entries = {}

        #Modülün içindeki tüm testleri dolaş
        for section_name,section_data in module.items():
            # Bölüm başlığı
            section_label = tk.Label(self.test_frame,text=f"[{section_name.upper()}]",font=("Arial",12,"bold"))
            section_label.pack(anchor="w",pady=(10,0))

            for test_name in section_data.keys():
                # Test Label
                label = tk.Label(self.test_frame,text=test_name)
                label.pack(anchor="w")

                #Test Entry
                entry = tk.Entry(self.test_frame)
                entry.pack(anchor="w")

                #Entry'yi dict.'e ekle
                self.entries[test_name] = entry

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

        #GUI verilerini topla
        patient_data = self.collect_patient_data()

        # Python içi analiz(modül bazlı)
        analysis = self.analyze_patient_data(patient_data,self.current_module)

        #Prompt oluştur
        prompt = f"""
           Hasta Özeti:
           {summary}

           Branş Modülü Analizi:
           {analysis}

           Lütfen bu verileri değerlendir."""
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

        #Modul cek
        self.current_module = get_branch_module(selected)

        if self.current_module is None:
            print("Bu branş için modül bulunamadı!")
        else:
            print("Modül başarıyla yüklendi",selected)

        if self.current_module:
            self.create_test_fields((self.current_module))


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
