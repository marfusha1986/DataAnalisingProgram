import tkinter as tk
from tkinter import ttk
import threading
from tkinter import messagebox

class CardiologyUI:
    def __init__(self, root, logic, module, gui):
        self.root = root
        self.logic = logic
        self.current_module = module
        self.entries = {}
        self.gui = gui
        self.next_row = 0

        self.root.title("Cardiology Module")
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
        canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_frame = tk.Frame(canvas, bg="#f2f2f2")
        window_id = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.root.configure(bg="#f2f2f2")

        # --- DİNAMİK FARE TEKERLEĞİ (SCROLL) MANTIĞI ---
        def _on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(e=None):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)

        def _unbind_mousewheel(e=None):
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")

        canvas.bind("<Enter>", lambda e: (canvas.focus_set(), _bind_mousewheel()))
        canvas.bind("<Leave>", _unbind_mousewheel)

        # Başlık alanı
        title = tk.Label(
            self.scroll_frame,
            text="Cardiology Data Entry",
            font=("Segoe UI", 18, "bold"),
            fg="#aa0000",
            bg="#f2f2f2"
        )
        title.grid(row=self.next_row, column=0, columnspan=2, pady=10)
        self.next_row += 1

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window_id, width=event.width)

        self.scroll_frame.bind("<Configure>", _on_frame_configure)

        # Dinamik giriş alanları
        self.create_dynamic_fields()

        # AI Liste alanı
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

        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Vertical.TScrollbar",
            background="#dddddd",
            troughcolor="#f2f2f2",
            bordercolor="#cccccc",
            arrowcolor="#0055aa"
        )

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

        scroll = ttk.Scrollbar(
            self.list_frame,
            orient="vertical",
            command=self.list_rows.yview,
            style="Vertical.TScrollbar"
        )
        scroll.grid(row=0, column=1, sticky="ns")
        self.list_rows.config(yscrollcommand=scroll.set)

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

        style.configure(
            "Dark.Vertical.TScrollbar",
            gripcount=0,
            background="#3A3A3A",
            darkcolor="#2E2E2E",
            lightcolor="#4A4A4A",
            troughcolor="#1E1E1E",
            bordercolor="#1E1E1E",
            arrowcolor="#D0D0D0"
        )

        self.ai_textbox = tk.Text(
            self.scroll_frame,
            wrap="word",
            height=15,
            width=60,
            bg="#1E1E1E",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            relief="flat",
            padx=10,
            pady=10
        )
        self.ai_textbox.grid(row=self.next_row, column=0, sticky="nsew")

        scroll_ai = ttk.Scrollbar(
            self.scroll_frame,
            orient="vertical",
            command=self.ai_textbox.yview,
            style="Dark.Vertical.TScrollbar"
        )
        scroll_ai.grid(row=self.next_row, column=1, sticky="ns")
        self.ai_textbox.configure(yscrollcommand=scroll_ai.set)

        # AI Textbox Fare Bağlantıları
        self.ai_textbox.bind("<Enter>", lambda e: (_unbind_mousewheel(), e.widget.config(bg="#2A2A2A")))
        self.ai_textbox.bind("<Leave>", lambda e: (_bind_mousewheel(), e.widget.config(bg="#1E1E1E")))

        self.ai_textbox.tag_config("title", font=("Segoe UI", 13, "bold"), foreground="#FF6666")
        self.ai_textbox.tag_config("section", font=("Segoe UI", 12, "bold"), foreground="#66B2FF")
        self.ai_textbox.tag_config("text", font=("Segoe UI", 11), foreground="#DDDDDD")
        self.ai_textbox.tag_config("error", foreground="#FF4444")

        self.scroll_frame.rowconfigure(self.next_row, weight=1)
        self.scroll_frame.columnconfigure(0, weight=1)
        self.next_row += 1

        style.configure("AI.TButton",
                        font=("Segoe UI", 11, "bold"),
                        padding=6,
                        background="#0055aa",
                        foreground="white",
                        borderwidth=0)

        style.map("AI.TButton", background=[("active", "#0077cc")])


        # Risk Paneli
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

        # AI Analiz Butonu
        btn = ttk.Button(
            self.scroll_frame,
            text="Analiz Et",
            style="AI.TButton",
            command=self.run_analysis
        )
        btn.grid(row=self.next_row, column=0, columnspan=2, pady=15)


        # --- DİNAMİK YANIT BUTONU ---
        self.origin_module = None  # Konsültasyonu gönderen modülü tutar (Örn: 'rheumatology')

        self.btn_reply_consult = ttk.Button(
            self.scroll_frame,
            text="↩️ Konsültasyon Yanıtını Gönder",
            command=self.send_dynamic_reply,
            state="disabled"  # Konsültasyon gelene kadar pasif durur
        )
        self.btn_reply_consult.grid(row=self.next_row, column=1, columnspan=2, pady=10)
        self.next_row += 1

        # Alt Boşluk
        tk.Frame(self.scroll_frame, height=50, bg="#f2f2f2").grid(row=self.next_row, column=0)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        try:
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")
        except Exception:
            pass
        self.root.destroy()


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

        self.list_rows.delete(0,"end")

        #Satır sayısı yoksa çık
        if df is None or len(df) == 0:
            self.list_rows.insert("end","Veri bulunamadı!")
            return

        for i in range(len(df)):
            self.list_rows.insert("end",f"Satır {i+1}")

    def analyze_values(self, row):
        score = 0
        analysis = {}

        # --- Yaş ---
        age = row.get("age")
        if age not in (None, "bilinmiyor"):
            if age > 60:
                score += 10
                analysis["age"] = "İleri Yaş"
            elif age > 45:
                score += 5
                analysis["age"] = "Orta Yaş"
            else:
                analysis["age"] = "Genç"

        # --- chest pain ---
        cp = row.get("cp")
        if cp not in (None, "bilinmiyor"):
            if cp == 3:
                score += 20
                analysis["cp"] = "Tipik angina"
            elif cp == 2:
                score += 10
                analysis["cp"] = "Atipik angina"
            elif cp ==1:
                score += 5
                analysis["cp"] = "Non-anginal"
            else:
                analysis["cp"] = "Göğüs ağrısı yok"

        # --- trestbps ---
        bp = row.get("trestbps")
        if bp not in (None, "bilinmiyor"):
            if bp > 150:
                score += 15
                analysis["trestbps"] = "Hipertansiyon"
            elif bp > 130:
                score += 10
                analysis["trestbps"] = "Yüksek Tansiyon"
            else:
                analysis["trestbps"] = "Normal"

        # --- chol ---
        chol = row.get("chol")
        if chol not in (None, "bilinmiyor"):
            if chol > 250:
                score += 20
                analysis["chol"] = "Kolestrol çok yüksek"
            elif chol > 200:
                score += 10
                analysis["chol"] = "Kolestrol Yüksek"
            else:
                analysis["chol"] = "Kolestrol normal"

        # --- thalac ---
        th = row.get("thalac")
        if th not in (None, "bilinmiyor"):
            if th < 120:
                score += 15
                analysis["thalac"] = "Düşük maximum nabız"
            else:
                analysis["thalac"] = "Normal maximum nabız"

        # --- oldpeak ---
        op = row.get("oldpeak")
        if op not in (None, "bilinmiyor"):
            if op > 2.0:
                score += 20
                analysis["oldpeak"] = "ST depresyonu belirgin"
            elif op > 1.0:
                score += 10
                analysis["oldpeak"] = "ST depresyonu hafif"
            else:
                analysis["oldpeak"] = "ST depresyonu yok"

        # --- slope ---
        slope = row.get("slope")
        if slope not in (None, "bilinmiyor"):
            if slope == 2:
                score += 10
                analysis["slope"] = "Egzersiz sonrası eğim anormal"
        # --- Final skor ---
        analysis["aggressiveness_score"] = score


        # --- ca ---
        ca = row.get("ca")
        if ca not in (None, "bilinmiyor"):
            if ca >= 2:
                score += 20
                analysis["ca"] = "Koroner damar sayısı yüksek"

        # --- thal ---
        thal = row.get("thal")
        if thal not in (None, "bilinmiyor"):
            if thal == 3:
                score += 20
                analysis["thal"] = "Reversibl defekt"
            elif thal == 6:
                score += 10
                analysis["thal"] = "Fiks defekt"

        analysis["aggressiveness_score"] = score
        return analysis

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
        for col,entry in self.entries.items():
            value = row.get(col,"bilinmiyor")
            entry.delete(0,"end")
            entry.insert(0,value)


    def generate_report(self,analysis):
        lines = []
        for test,status in analysis.items():
            lines.append(f"{test}: {status}")
        return "\n".join(lines)

    def run_analysis(self):
        selected = self.list_rows.curselection()
        if not selected:
            self.ai_textbox.delete("1.0", "end")
            self.ai_textbox.insert("end", "Lütfen bir satır seçin.\n")
            return

        idx = selected[0]

        # 1) Klinik analiz için: ham numeric veri
        row_numeric = self.logic.df.iloc[idx]

        # 2) AI prompt için: eksikler "bilinmiyor"
        row_for_prompt = row_numeric.copy()
        row_for_prompt = row_for_prompt.where(row_for_prompt.notna(), "bilinmiyor")

        # Python içi analiz (risk skoru vs.)
        analysis = self.analyze_values(row_numeric)
        score = analysis.get("aggressiveness_score", 0)
        self.update_risk_label(score)
        self.update_risk_bar(score)
        # Prompt oluştur
        prompt = self.build_clinical_prompt(row_for_prompt)

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

        import json
        final_text = ""  # Değişkeni başta tanımlıyoruz ki NameError vermesin

        # 1) Eğer string "AI hatası: Beklenmeyen yanıt yapısı:" ile başlıyorsa, JSON kısmını ayıkla
        if isinstance(ai_output, str) and "Beklenmeyen yanıt yapısı:" in ai_output:
            start = ai_output.find("{")
            if start != -1:
                ai_output = ai_output[start:]

        try:
            # 2) LM Studio chat.completion JSON'unu parse et
            data = json.loads(ai_output)

            # 3) Asıl içerik: message.content
            content = data["choices"][0]["message"]["content"]

            # 4) İçerik JSON string → tekrar parse et
            try:
                inner = json.loads(content)
                klinik = inner.get("klinik_degerlendirme")
                final_text = klinik if klinik else content
            except Exception:
                final_text = content

        except Exception:
            # Fallback: ham metni al
            final_text = str(ai_output)

        # 5) Metni Textbox'a yazdır
        self.ai_textbox.insert("end", final_text)

        # 6) --- DİNAMİK YANIT BUTONUNU AKTİFLEŞTİR ---
        if hasattr(self, "btn_reply_consult"):
            self.btn_reply_consult.config(state="normal")

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


    def build_clinical_prompt(self,row):

        bulgu_text = "\n".join([f"{col} = {row[col]}" for col in row.index])
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

    def set_incoming_consultation(self, consult_info):
        """Gelen konsültasyona göre kaynak modülün anahtarını kaydeder."""
        # Veri gelmese dahi varsayılan olarak 'rheumatology' atayarak çökmesini/boş kalmasını önlüyoruz
        self.origin_module_key = consult_info.get("from_module_key") or consult_info.get("from_module",
                                                                                         "rheumatology").lower()
        origin_title = consult_info.get("from_module", "Rheumatology")

        if hasattr(self, "btn_reply_consult"):
            self.btn_reply_consult.config(
                text=f"↩️ {origin_title}'ye Konsültasyon Yanıtını Gönder"
            )

    def send_dynamic_reply(self):
        """Butona tıklandığında kaynak branşa yanıt gönderir."""
        # origin_module_key yoksa fallback olarak 'rheumatology' kullan
        target_key = getattr(self, "origin_module_key", "rheumatology")

        ai_reply = self.ai_textbox.get("1.0", "end").strip()
        if not ai_reply:
            from tkinter import messagebox
            messagebox.showwarning("Uyarı", "Gönderilecek bir değerlendirme metni bulunamadı.")
            return

        current_branch_name = self.__class__.__name__.replace("UI", "")

        reply_data = {
            "from_module": current_branch_name,
            "from_module_key": current_branch_name.lower(),
            "to_module": target_key,
            "ai_summary": ai_reply
        }

        self.gui.active_consultation = reply_data

        # İstek atan ana modülü (Romatoloji) tekrar aç ve ön plana getir
        if hasattr(self.gui, "branch_var"):
            self.gui.branch_var.set(target_key)
            self.gui.on_branch_selected(None)

        from tkinter import messagebox
        messagebox.showinfo("Başarılı", "Değerlendirme notu ilgili branşa iletildi.")