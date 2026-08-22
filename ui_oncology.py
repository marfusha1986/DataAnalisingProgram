import tkinter as tk
from tkinter import ttk
import threading

class OncologyUI:
    def __init__(self, root, logic, module,gui):
        self.root = root
        self.logic = logic
        self.current_module = module
        self.entries = {}
        self.gui = gui

        self.root.title("Oncology Module")
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
            text="Oncology Data Entry",
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

        self.risk_label = tk.Label(
            self.scroll_frame,
            text="Risk Skoru: -",
            font=("Segoe UI", 12, "bold"),
            bg="#f2f2f2"
        )
        self.risk_label.grid(row=self.next_row, column=0, columnspan=2, pady=10, sticky="w")
        self.next_row += 1

        self.risk_bar = ttk.Progressbar(
            self.scroll_frame,
            orient="horizontal",
            length=300,
            mode="determinate"
        )
        self.risk_bar.grid(row=self.next_row, column=0, columnspan=2, pady=5)
        self.next_row += 1


        # --- ALT BOŞLUK ---
        tk.Frame(self.scroll_frame, height=50).grid(row=self.next_row,column=0)

    def create_dynamic_fields(self):
        columns = list(self.logic.df.columns)

        row_index = 1
        for col in columns:
            lbl = tk.Label(
                self.scroll_frame,
                text=col,
                font=("Segoe UI", 11, "bold"),
                fg="#003366",
                bg="#f2f2f2",
                padx=5
            )
            lbl.grid(row=row_index,column=0,sticky="w",padx=10,pady=5)

            entry = tk.Entry(
                self.scroll_frame,
                font=("Segoe UI", 11),
                width=35,
                bg="#ffffff",
                fg="#333333",
                relief="flat",
                highlightthickness=1,
                highlightbackground="#cccccc",
                highlightcolor="#4da6ff"
            )

            entry.grid(row=row_index,column=1,sticky="w",padx=10,pady=5)

            # Hover efekti (CSS gibi)
            entry.bind("<Enter>", lambda e: e.widget.config(bg="#e6f2ff"))
            entry.bind("<Leave>", lambda e: e.widget.config(bg="#ffffff"))

            self.entries[col] = entry
            row_index += 1
        self.next_row = row_index


    def update_rows(self,df):
        print("UPDATE_ROWS ÇAĞRILDI, satır sayısı:", len(df))
        print("UPDATE_ROWS SELF:", self)
        print("LISTBOX:", self.list_rows)
        self.root.lift()
        self.root.focus_force()

        self.list_rows.delete(0,tk.END)
        for i in range(len(df)):
            self.list_rows.insert(tk.END,f"Satır {i+1}")


    def on_row_selected(self,event):
        selection = self.list_rows.curselection()
        if not selection:
            return
        self.selected_row_index = selection[0]
        row = self.logic.df.iloc[self.selected_row_index]

        for col ,entry in self.entries.items():
            value = row.get(col,"")
            entry.delete(0,tk.END)
            entry.insert(0,str(value))



    def fill_entries_from_row(self,row):
        for col_name,value in row.items():
            entry = self.entries[col_name]
            entry.delete(0,tk.END)
            entry.insert(0,value)


    def collect_values(self):
        results = {}
        for col,entry in self.entries.items():
            value = entry.get().strip()
            if value == "":
                continue
            try:
                value = float(value)
            except:
                pass
            results[col] = value
        return results

    def analyze_values(self,values):
        analysis = {}

        worst_vals = []
        mean_vals = []
        se_vals = []

        for key, val in values.items():
            if isinstance(val, (int, float)):
                if "worst" in key:
                    worst_vals.append(val)
                elif "mean" in key:
                    mean_vals.append(val)
                elif "se" in key:
                    se_vals.append(val)

            # Agresiflik skoru (worst değerlerinin ortalaması)
        if worst_vals:
            analysis["aggressiveness_score"] = round(sum(worst_vals) / len(worst_vals), 4)

            # Genel risk skoru (mean değerlerinin ortalaması)
        if mean_vals:
            analysis["general_risk_score"] = round(sum(mean_vals) / len(mean_vals), 4)

            # Varyasyon skoru (se değerlerinin ortalaması)
        if se_vals:
            analysis["variation_score"] = round(sum(se_vals) / len(se_vals), 4)

        return analysis

    def generate_report(self,analysis):
        lines = []
        for test,status in analysis.items():
            lines.append(f"{test}: {status}")
        return "\n".join(lines)

    def run_analysis(self):
        # 1) Entry’lerden veri topla
        values = self.collect_values()

        # 2) Python içi analiz (yüksek/düşük vb.)
        analysis = self.analyze_values(values)
        score = (analysis.get("aggressiveness_score"))
        self.update_risk_label(score)
        self.update_risk_bar(score)
        print("RUN_ANALYSIS ÇAĞRILDI")

        #3)CSV satırından klinik bulgu oluştur
        prompt = self.build_clinical_prompt()

        #4)Textbox'ı temizle

        self.ai_textbox.delete("1.0", "end")
        self.ai_textbox.insert("end", "AI analiz ediliyor...\n")

        # ASENKRON AI çağrısı
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

    def generate_summary_from_row(self,row):
        lines = []
        for col_name,entry in self.entries.items():
            value = row.get(col_name,"veri yok")
            lines.append(f"{col_name}: {value}")
        return "\n".join(lines)

    def update_risk_label(self, score):
        if score is None:
            self.risk_label.config(text="Risk Skoru: -", fg="#333333")
            return

        if score < 0.2:
            color = "#009900"  # yeşil
            level = "Düşük"
        elif score < 0.5:
            color = "#e6b800"  # sarı
            level = "Orta"
        else:
            color = "#cc0000"  # kırmızı
            level = "Yüksek"

        self.risk_label.config(
            text=f"Risk Skoru: {score:.3f} ({level})",
            fg=color
        )

    def update_risk_bar(self, score):
        if score is None:
            self.risk_bar["value"] = 0
            return

        self.risk_bar["maximum"] = 200

        # score 0–1 arası normalize ediliyor
        value = min(max(score, 0), 200)
        self.risk_bar["value"] = value

    def on_ai_result(self, ai_output):
        self.ai_textbox.delete("1.0", "end")

        if not ai_output or "AI hatası" in ai_output or ai_output.strip() == "":
            self.ai_textbox.insert("end","AI cevap vermedi","error")
            return
        else:
            self.ai_textbox.insert("end", ai_output,"normal")

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
                print("WORKER HATASI:",e)

        thread = threading.Thread(target=worker, daemon=True).start()
        print("THREAD başlatıldı")


    def build_clinical_prompt(self):
        row_data =self.logic.df.iloc[self.selected_row_index]

        bulgu_text = "\n".join([f"{col} = {row_data[col]}" for col in row_data.index])
        prompt = f"""
        Aşağıdaki veriler bir hastanın klinik bulgularıdır.
        Bu bulgulara göre olası klinik tanıları üret.
        Tanı üretirken sadece tıbbi bilgi kullan.
        Python analizinden bahsetme.
        Metni çevirme.
        Risk skoru hesapla.
        Sadece klinik tanı ver.

        Klinik Bulgular:
        {bulgu_text}
        """
        return prompt
