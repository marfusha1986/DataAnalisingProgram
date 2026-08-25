import tkinter as tk
from tkinter import ttk
import threading


class InternalDiseaseUI:

    def __init__(self, root, logic, module, gui):
        self.root = root
        self.logic = logic
        self.current_module = module
        self.entries = {}
        self.gui = gui

        self.root.title("Internal_Disease Module")
        self.root.geometry("1100x800")
        self.root.lift()
        self.root.focus_force()

        container = tk.Frame(self.root)
        container.grid(row=0, column=0, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(container)
        canvas.configure(height=1)
        canvas.grid(row=0, column=0, sticky="nsew")

        canvas.grid_rowconfigure(0, weight=1)
        canvas.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_frame = tk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.root.configure(bg="#f2f2f2")
        self.scroll_frame.configure(bg="#f2f2f2")

        title = tk.Label(
                self.scroll_frame,
                text="Neurology Data Entry",
                font=("Segoe UI", 18, "bold"),
                fg="#aa0000",
                bg="#f2f2f2"
        )
        title.grid(row=0, column=0, columnspan=2, pady=10)

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window_id, width=event.width)

        self.scroll_frame.bind("<Configure>", _on_frame_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.create_dynamic_fields()

        self.list_frame = tk.LabelFrame(
                self.scroll_frame,
                text="AI Liste",
                font=("Segoe UI", 12, "bold"),
                fg="#0055aa",
                bg="#f2f2f2",
                bd=2,
                relief="groove",
                padx=10,
                pady=10
        )
        self.list_frame.grid(row=self.next_row, column=0, columnspan=2, sticky="nsew", pady=10)

        # Frame grid ayarları
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        # --- MODERN SCROLLBAR STYLE ---
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
                "Vertical.TScrollbar",
                background="#dddddd",
                troughcolor="#f2f2f2",
                bordercolor="#cccccc",
                arrowcolor="#0055aa"
        )

        # Satır seçme listesi (CSV satırlar için)
        self.list_rows = tk.Listbox(
            self.list_frame,
                font=("Segoe UI", 11),
                height=6,
                bg="#ffffff",
                fg="#333333",
                selectbackground="#cce6ff",
                selectforeground="#000000",
                relief="solid",
                bd=1,
                highlightthickness=1,
                highlightbackground="#cccccc",
                highlightcolor="#4da6ff"
        )
        self.list_rows.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.list_rows.bind("<Enter>", lambda e: e.widget.config(bg="#f7fbff"))
        self.list_rows.bind("<Leave>", lambda e: e.widget.config(bg="#ffffff"))

        # Scrollbar
        scroll = ttk.Scrollbar(
                self.list_frame,
                orient="vertical",
                command=self.list_rows.yview,
                style="Vertical.TScrollbar"
        )
        scroll.grid(row=0, column=1, sticky="ns")

        self.list_rows.config(yscrollcommand=scroll.set)

        # Satır seçme event
        self.list_rows.bind("<<ListboxSelect>>", self.on_row_selected)
        self.next_row += 1

        # --- AI ÇIKTI ALANI ---
        ai_label = tk.Label(
                self.scroll_frame,
                text="AI Analysis Output",
                font=("Segoe UI", 14, "bold"),
                fg="#aa0000",
                bg="#f2f2f2"
        )
        ai_label.grid(row=self.next_row, column=0, columnspan=2, pady=(20, 5), sticky="w")

        self.next_row += 1

        # --- STYLE (CSS benzeri) ---
        style = ttk.Style()
        style.theme_use("clam")

        # Scrollbar stili
        style.configure(
                "Vertical.TScrollbar",
                gripcount=0,
                background="#3A3A3A",
                darkcolor="#2E2E2E",
                lightcolor="#4A4A4A",
                troughcolor="#1E1E1E",
                bordercolor="#1E1E1E",
                arrowcolor="#D0D0D0"
        )

        # Textbox stili (arka plan + yazı rengi)
        self.ai_textbox = tk.Text(
            self.scroll_frame,
                wrap="word",
                height=15,
                width=60,
                bg="#1E1E1E",  # koyu arka plan
                fg="#FF5555",  # açık yazı
                insertbackground="#FFFFFF",  # imleç rengi
                relief="flat",
                padx=10,
                pady=10
        )
        self.ai_textbox.grid(row=self.next_row, column=0, sticky="nsew")
        self.ai_textbox.tag_config("error", foreground="#FF4444")
        self.ai_textbox.tag_config("normal", foreground="#000000")

        # Scrollbar
        scroll = ttk.Scrollbar(
                self.scroll_frame,
                orient="vertical",
                command=self.ai_textbox.yview,
                style="Vertical.TScrollbar"
        )
        scroll.grid(row=self.next_row, column=1, sticky="ns")

        # Textbox scroll bağlantısı
        self.ai_textbox.configure(yscrollcommand=scroll.set)

        # Grid genişleme
        self.scroll_frame.rowconfigure(self.next_row, weight=1)
        self.scroll_frame.columnconfigure(0, weight=1)

        self.next_row += 1
        # Hover efekti
        self.ai_textbox.bind("<Enter>", lambda e: e.widget.config(bg="#f7fbff"))
        self.ai_textbox.bind("<Leave>", lambda e: e.widget.config(bg="#ffffff"))

        self.ai_textbox.tag_config("title", font=("Segoe UI", 13, "bold"), foreground="#aa0000")
        self.ai_textbox.tag_config("section", font=("Segoe UI", 12, "bold"), foreground="#003366")
        self.ai_textbox.tag_config("text", font=("Segoe UI", 11), foreground="#333333")

        self.next_row += 1
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton",
                            font=("Segoe UI", 11, "bold"),
                            padding=6,
                            background="#0055aa",
                            foreground="white",
                            borderwidth=0)

        style.map("TButton",
                      background=[("active", "#0077cc")])

        # AI analiz butonu
        btn = ttk.Button(
                self.scroll_frame,
                text="Analiz Et",
                style="AI.TButton",
                command=self.run_analysis
        )
        btn.grid(row=self.next_row, column=0, columnspan=2, pady=15)

        self.next_row += 1

        # --- ALT BOŞLUK ---
        tk.Frame(self.scroll_frame, height=50).grid(row=self.next_row, column=0)

    def create_dynamic_fields(self):
        columns = list(self.logic.df.columns)

        row_index = 1
        self.labels = {}

        for col in columns:
            lbl = tk.Label(
                    self.scroll_frame,
                    text=col,
                    font=("Segoe UI", 11, "bold"),
                    fg="#003366",
                    bg="#f2f2f2",
                    padx=5
            )
            lbl.grid(row=row_index, column=0, sticky="w", padx=10, pady=5)

            lbl_value = tk.Label(
                    self.scroll_frame,
                    text="-",
                    font=("Segoe UI", 11),
                    width=35,
                    bg="#ffffff",
                    fg="#333333",
                    relief="solid",
                    bd=1, padx=5, pady=3
            )

            lbl_value.grid(row=row_index, column=1, sticky="w", padx=10, pady=5)

            # Hover efekti (CSS gibi)
            lbl_value.bind("<Enter>", lambda e: e.widget.config(bg="#e6f2ff"))
            lbl_value.bind("<Leave>", lambda e: e.widget.config(bg="#ffffff"))

            self.labels[col] = lbl_value
            row_index += 1
        self.next_row = row_index

        print("Label sayısı:", len(self.labels))

    def update_rows(self, df):
        print("UPDATE_ROWS ÇAĞRILDI, satır sayısı:", len(df))
        print("UPDATE_ROWS SELF:", self)
        print("LISTBOX:", self.list_rows)
        self.root.lift()
        self.root.focus_force()

        self.list_rows.delete(0, tk.END)
        for i in range(len(df)):
            self.list_rows.insert(tk.END, f"Satır {i + 1}")

    def analyze_values(self, row):
        analysis = {}
        score = 0

        # --- Glikoz ---
        glucose = row.get("glucose")
        if glucose not in (None, "", "unknown"):
            if glucose > 180:
                analysis["glucose"] = "Hiperglisemi"
                score += 15
            elif glucose > 140:
                analysis["glucose"] = "Yüksek glikoz"
                score += 10
            elif glucose < 70:
                analysis["glucose"] = "Hipoglisemi"
                score += 15
            else:
                analysis["glucose"] = "Normal"

        # --- İnsülin ---
        insulin = row.get("insulin")
        if insulin not in (None, "", "unknown"):
            if insulin > 200:
                analysis["insulin"] = "İnsülin direnci olası"
                score += 10
            elif insulin < 20:
                analysis["insulin"] = "Düşük insülin"
                score += 5
            else:
                analysis["insulin"] = "Normal"

        # --- BMI ---
        bmi = row.get("bmi")
        if bmi not in (None, "", "unknown"):
            if bmi >= 30:
                analysis["bmi"] = "Obezite"
                score += 15
            elif bmi >= 25:
                analysis["bmi"] = "Fazla kilolu"
                score += 10
            elif bmi < 18.5:
                analysis["bmi"] = "Zayıf"
                score += 5
            else:
                analysis["bmi"] = "Normal"

        # --- Yaş ---
        age = row.get("age")
        if age not in (None, "", "unknown"):
            if age >= 65:
                analysis["age"] = "İleri yaş"
                score += 10
            elif age >= 45:
                analysis["age"] = "Orta yaş"
                score += 5
            else:
                analysis["age"] = "Genç"

        # --- Kan Basıncı (BP) ---
        bp = row.get("bp")
        if bp not in (None, "", "unknown"):
            if bp >= 140:
                analysis["bp"] = "Hipertansiyon"
                score += 15
            elif bp >= 130:
                analysis["bp"] = "Yüksek tansiyon"
                score += 10
            else:
                analysis["bp"] = "Normal"

        # --- Hemoglobin ---
        hgb = row.get("hemoglobin")
        if hgb not in (None, "", "unknown"):
            if hgb < 12:
                analysis["hemoglobin"] = "Anemi olası"
                score += 10
            elif hgb > 17:
                analysis["hemoglobin"] = "Yüksek hemoglobin"
                score += 5
            else:
                analysis["hemoglobin"] = "Normal"

        # --- Final skor ---
        analysis["risk_score"] = score
        return analysis

    def on_row_selected(self, event):
        selection = self.list_rows.curselection()
        if not selection:
            return

        self.selected_row_index = selection[0]
        row = self.logic.df.iloc[self.selected_row_index]
        # Entry doldurma
        if hasattr(self, "entries"):
            for col, entry in self.entries.items():
                try:
                    value = row[col]
                except KeyError:
                    value = ""
                entry.delete(0, tk.END)
                entry.insert(0, str(value))

        # Label için
        if hasattr(self, "labels"):
            self.fill_labels_from_row(row)

    def fill_labels_from_row(self, row):
        for col, lbl in self.labels.items():
            try:
                value = row[col]
            except KeyError:
                value = "bulunamadı"
            lbl.config(text=f"{col}: {value}")

    def generate_report(self, analysis):
        lines = []
        for test, status in analysis.items():
            lines.append(f"{test}: {status}")
        return "\n".join(lines)

    def run_analysis(self):
        selected = self.list_rows.curselection()
        if not selected:
            self.ai_textbox.delete("1.0", "end")
            self.ai_textbox.insert("end", "Lütfen bir satır seçin.\n")
            return

        idx = selected[0]

        # CSV satırını al ve nan değerleri temizle
        row = self.logic.df.iloc[idx].fillna("bilinmiyor")

        # TEST
        print("RUN ANALYSİS ÇALIŞTI")
        self.labels[list(self.labels.keys())[0]].config(text="TEST")

        self.fill_labels_from_row(row)

        # Python içi analiz
        analysis = self.analyze_values(row)
        score = analysis.get("aggressiveness_score", 0)

        # Prompt oluştur
        prompt = self.build_clinical_prompt(row)

        # Textbox temizle
        self.ai_textbox.delete("1.0", "end")
        self.ai_textbox.insert("end", "AI analiz ediliyor...\n")

        # Asenkron AI çağrısı
        self.ask_ai_async(prompt)

    def ai_analysis_button(self):
        selection = self.list_rows.curselection()
        if not selection:
            print("Satır seçilmedi!")
            return

        index = selection[0]
        row = self.logic.df.iloc[index]

        summary = self.generate_summary_from_row(row)

        if not summary.strip():
            print("AI analiz için yeterli veri yok!")
            return

        self.gui.ask_ai_async(summary)

    def generate_summary_from_row(self, row):
        lines = []
        for col_name, entry in self.entries.items():
            value = row.get(col_name, "veri yok")
            lines.append(f"{col_name}: {value}")
        return "\n".join(lines)

    def on_ai_result(self, ai_output):
        self.ai_textbox.delete("1.0", "end")

        if not ai_output or "AI hatası" in ai_output or ai_output.strip() == "":
            self.ai_textbox.insert("end", "AI cevap vermedi", "error")
            return
        else:
            self.ai_textbox.insert("end", ai_output, "normal")

    def ask_ai_async(self, prompt):
        print("ASK_AI_ASYNC çağrıldı")

        def worker():
            print("WORKER başladı")
            try:
                ai_output = self.logic.ask_ai(prompt)
                print("AI RAW: ", repr(ai_output))

                self.root.after(0, lambda: self.on_ai_result(ai_output))
                print("AFTER çağrıldı")
            except Exception as e:
                print("WORKER HATASI:", e)

        thread = threading.Thread(target=worker, daemon=True).start()
        print("THREAD başlatıldı")

    def build_clinical_prompt(self, row):

        bulgu_text = "\n".join([f"{col} = {row[col]}" for col in row.index])
        prompt = f"""
           Aşağıdaki veriler bir hastanın Parkinson ses analizi bulgularıdır.
            Bu bulgulara göre olası nörolojik tanıları üret.
            Sadece tıbbi bilgi kullan.
            Klinik Bulgular:
        {bulgu_text}
            """
        return prompt

    def update_ai_output(self, row):
        bulgular = "\n".join([f"- {col}: {row[col]}" for col in row.index])

        text = []
        text.append("🧠 Nörolojik Klinik Değerlendirme")
        text.append("")
        text.append("📌 Hastaya ait nörolojik klinik bulgular:")
        text.append(bulgular)
        text.append("")
        text.append("🔍 Bu bulgular AI tarafından analiz edilerek olası nörolojik tanılar üretilecektir.")
        text.append("")

        self.ai_textbox.delete("1.0", "end")
        self.ai_textbox.insert("end", "\n".join(text))

    def on_predict_clicked(self):
        row = self.logic.df.iloc[self.selected_row_index]
        pred = self.logic.predict(row)
        self.ai_textbox.insert("end", f"\n\n🎯 Tahmin Edilen Sınıf: {pred}")


def on_ai_clicked(self):
    row = self.logic.df.iloc[self.selected_row_index]

    bulgu_text = "\n".join([
        f"{col} = {row[col]}"
        for col in row.index
    ])

    prompt = f"""
        Aşağıdaki dahiliye verilerini analiz et.
        Klinik açıdan anlamlı noktaları açıkla.
        Risk faktörlerini değerlendir.
        Uç değerleri, normalden sapmaları belirt.
        Tıbbi tanı koyma.
        Sadece klinik yorum yap.

        Bulgular:
        {bulgu_text}
        """

    result = self.logic.ask_ai(prompt)
    self.ai_textbox.insert("end", f"\n\n🧠 Dahiliye Klinik Analiz:\n{result}")




