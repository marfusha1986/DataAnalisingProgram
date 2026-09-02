import tkinter as tk
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
import seaborn as sns
import re


class RheumatologyUI:

    def __init__(self, root, logic, module, gui):
        self.root = root
        self.logic = logic
        self.current_module = module
        self.entries = {}
        self.gui = gui
        self.next_row = 0

        self.root.title("Rheumatology Module")
        self.root.geometry("1100x800")
        self.root.lift()
        self.root.focus_force()

        container = tk.Frame(self.root)
        container.grid(row=0, column=0, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        main_canvas = tk.Canvas(container)
        main_canvas.configure(height=1)
        main_canvas.grid(row=0, column=0, sticky="nsew")

        main_canvas = tk.Canvas(container)
        main_canvas.grid(row=0, column=0, sticky="nsew")

        main_canvas.bind("<Enter>", lambda e: (main_canvas.focus_set(),_bind_mousewheel()))


        main_canvas.grid_rowconfigure(0, weight=1)
        main_canvas.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=main_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        main_canvas.configure(yscrollcommand=scrollbar.set)

        self.scroll_frame = tk.Frame(main_canvas)
        window_id = main_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.root.configure(bg="#f2f2f2")

        title = tk.Label(
                self.scroll_frame,
                text="Rheumatology Data Entry",
                font=("Segoe UI", 18, "bold"),
                fg="#aa0000",
                bg="#f2f2f2"
        )
        title.grid(row=self.next_row, column=0, columnspan=2, pady=10)
        self.next_row +=1

        def _on_frame_configure(event):
            main_canvas.configure(scrollregion=main_canvas.bbox("all"))
            main_canvas.itemconfig(window_id, width=event.width)

        self.scroll_frame.bind("<Configure>", _on_frame_configure)

        self.create_dynamic_fields()
        self.build_row_list()
        self.update_rows(self.logic.df)

        self.next_row = self.scroll_frame.grid_size()[1]

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

        def _on_mousewheel(event):
            if event.num == 4:
                main_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                main_canvas.yview_scroll(1, "units")
            else:
                main_canvas.yview_scroll(int(-1*(event.delta / 120)), "units")

        def _bind_mousewheel(e=None):
            main_canvas.bind_all("<MouseWheel>", _on_mousewheel) #Windows/macOS
            main_canvas.bind_all("<Button-4>",_on_mousewheel) #Linux Yukarı
            main_canvas.bind_all("<Button-5>",_on_mousewheel) #Linux Aşağı

        def _unbind_mousewheel(e=None):
            main_canvas.unbind_all("<MouseWheel>")
            main_canvas.unbind_all("<Button-4>")
            main_canvas.unbind_all("<Button-5>")

        _bind_mousewheel()

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
                fg="#FFFFFF",  # açık yazı
                insertbackground="#FFFFFF",  # imleç rengi
                relief="flat",
                padx=10,
                pady=10
        )
        self.ai_textbox.grid(row=self.next_row, column=0, sticky="nsew")

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
        self.scroll_frame.rowconfigure(0, weight=1)

        self.ai_textbox.tag_config("error", foreground="#FF4444")
        self.ai_textbox.tag_config("normal", foreground="#E0E0E0")
        self.ai_textbox.tag_config("title", font=("Segoe UI", 13, "bold"), foreground="#FF6666")
        self.ai_textbox.tag_config("section", font=("Segoe UI", 12, "bold"), foreground="#66B2FF")
        self.ai_textbox.tag_config("text", font=("Segoe UI", 11), foreground="#DDDDDD")

        def _on_textbox_scroll(event):
            if event.delta:
                self.ai_textbox.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                if event.num == 4:
                    self.ai_textbox.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.ai_textbox.yview_scroll(1, "units")
            return "break"



        self.ai_textbox.bind("<MouseWheel>", _on_textbox_scroll)
        self.ai_textbox.bind("<Button-4>", _on_textbox_scroll)
        self.ai_textbox.bind("<Button-5>", _on_textbox_scroll)

        self.ai_textbox.bind("<Enter>", lambda e:(_unbind_mousewheel(), e.widget.config(bg="#2A2A2A")))
        self.ai_textbox.bind("<Leave>", lambda e:(_bind_mousewheel(), e.widget.config(bg="#1E1E1E")))

        self.scroll_frame.bind("<MouseWheel>", lambda e: "break")
        self.scroll_frame.bind("<Button-4>", lambda e: "break")
        self.scroll_frame.bind("<Button-5>", lambda e: "break")

        self.scroll_frame.bind("<Leave>", lambda e: _bind_mousewheel())

        self.next_row += 1

        style.configure("AI.TButton",
                            font=("Segoe UI", 11, "bold"),
                            padding=6,
                            background="#0055aa",
                            foreground="white",
                            borderwidth=0)

        style.map("AI.TButton",
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

        # --- KONSÜLTASYON VE SEVK PANELSİ ---
        self.consult_frame = tk.LabelFrame(
            self.scroll_frame,
            text=" 🏥 Konsültasyon & Branş Sevk Paneli ",
            font=("Segoe UI", 12, "bold"),
            fg="#0055aa",
            bg="#f2f2f2",
            bd=2,
            relief="groove",
            padx=10,
            pady=10
        )
        self.consult_frame.grid(row=self.next_row, column=0, columnspan=2, sticky="nsew", pady=15)
        self.next_row += 1

        # Konsültasyon Durum Etiketi
        self.lbl_consult_status = tk.Label(
            self.consult_frame,
            text="Konsültasyon İhtiyacı: Analiz bekleniyor...",
            font=("Segoe UI", 10, "italic"),
            bg="#f2f2f2",
            fg="#555555"
        )
        self.lbl_consult_status.pack(anchor="w", pady=(0, 5))

        # Önerilen Branşlar için Checkbox / Listbox alanı
        self.consult_checks = {}
        consult_branches = [
            ("Cardiology", "Kardiyoloji (Tutulum / EKG / EKO)"),
            ("Nephrology", "Nefroloji (Böbrek Tutulumu / Proteinüri)"),
            ("Endocrinology", "Endokrinoloji (Glikokortikoid / Metabolizma)"),
            ("Dermatology", "Dermatoloji (Cilt Lezyonları / Biyopsi)")
        ]

        for code, name in consult_branches:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(
                self.consult_frame,
                text=name,
                variable=var,
                font=("Segoe UI", 10),
                bg="#f2f2f2",
                activebackground="#f2f2f2"
            )
            chk.pack(anchor="w")
            self.consult_checks[code] = var

        # Konsültasyon Notu Gönderme Butonu
        btn_send_consult = ttk.Button(
            self.consult_frame,
            text="Seçili Branşlara Konsültasyon Talebi Oluştur",
            command=self.send_consultation
        )
        btn_send_consult.pack(anchor="e", pady=(10, 0))

        # --- ALT BOŞLUK ---
        tk.Frame(self.scroll_frame, height=50,bg="#f2f2f2").grid(row=self.next_row, column=0)

        self.root.protocol("WM_DELETE_WINDOW",self.on_close)

    def on_close(self):
        try:
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")
        except Exception:
            pass
        self.root.destroy()

    def build_row_list(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#1e1e1e",
                        foreground="#d4d4d4",
                        fieldbackground="#1e1e1e",
                        rowheight=24)
        style.map("Treeview",
                  background=[("selected", "#3a3a3a")],
                  foreground=[("selected", "#ffffff")])

        self.list_frame = tk.LabelFrame(
            self.scroll_frame,
            text="AI Liste",
            font=("Segoe UI", 12, "bold"),
            fg="#d4d4d4",
            bg="#1e1e1e",
            bd=2,
            relief="groove",
            padx=10,
            pady=10
        )
        self.list_frame.grid(row=self.next_row, column=0, columnspan=2, sticky="nsew", pady=10)

        self.tree_scroll = tk.Scrollbar(self.list_frame)
        self.tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            self.list_frame,
            yscrollcommand=self.tree_scroll.set,
            columns=("index",),
            show="headings",
            height=10
        )

        self.tree.heading("index", text="Satır")
        self.tree.column("index", width=120, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        self.tree_scroll.config(command=self.tree.yview)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

        def _on_tree_mousewheel(event):
            self.tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return 'break'

        self.tree.bind("<MouseWheel>", _on_tree_mousewheel)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

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
        # Treeview'i temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        if df is None or df.empty:
            return

        # Satırları ekle (Resim sütunu varsa ismini de parantez içinde gösterir)
        for i in range(len(df)):
            if "Görsel_Yolu" in df.columns:
                import os
                file_name = os.path.basename(str(df.iloc[i]["Görsel_Yolu"]))
                self.tree.insert("", "end", values=(f"Satır {i + 1} ({file_name})",))
            else:
                self.tree.insert("", "end", values=(f"Satır {i + 1}",))


    def on_row_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        satir_text = item["values"][0]

        index = int(satir_text.split()[1]) - 1
        self.selected_row_index = index

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
        import os
        from pathlib import Path

        def _find_image_file(file_name):
            """Resim dosyasını seçilen klasörde ve tüm alt klasörlerde arar."""
            if not file_name or not isinstance(file_name, str):
                return None

            file_name = file_name.strip().strip("'\"")
            if file_name.startswith("b'") or file_name.startswith('b"'):
                file_name = file_name[2:].strip("'\"")

            # 1. Zaten tam yol verildiyse ve varsa doğrudan döndür
            if os.path.exists(file_name) and os.path.isfile(file_name):
                return file_name

            # 2. Seçilen klasörün yolunu al
            search_dir = getattr(self.logic, "csv_folder", None) or os.getcwd()

            # 3. Klasör ve ALT KLASÖRLERİ (os.walk) tarayarak dosyayı bul
            base_name = os.path.basename(file_name).lower()
            for root, _, files in os.walk(search_dir):
                for f in files:
                    if f.lower() == base_name:
                        return os.path.join(root, f)

            return None

        image_exts = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')

        for col, lbl in self.labels.items():
            try:
                value = row[col]
            except KeyError:
                value = "bulunamadı"

            text_value = "" if value is None else str(value)
            v_lower = text_value.lower().strip() if isinstance(text_value, str) else ""
            shown_image = False

            # --- 1. GÖRSEL DOSYASI KONTROLÜ ---
            if isinstance(text_value, str) and any(v_lower.endswith(ext) for ext in image_exts):
                found_path = _find_image_file(text_value)

                if found_path:
                    try:
                        from PIL import Image, ImageTk

                        img = Image.open(found_path)
                        # Resim kalitesini koruyarak 180x150 boyutuna getirir
                        img.thumbnail((180, 150), Image.Resampling.LANCZOS)
                        tkimg = ImageTk.PhotoImage(img)
                        fname = Path(found_path).name

                        # Resim yüklenirken width="" verilerek kırpılma engellenir
                        lbl.config(
                            image=tkimg,
                            text=f"{col}: {fname}",
                            compound='left',
                            anchor='w',
                            width=250,
                            height=150  # Esnek genişlik ve boyutlandırma için height eklenebilir
                        )
                        lbl.image = tkimg

                        # Tıklayınca varsayılan görüntüleyicide açma
                        def _open(event, p=found_path):
                            try:
                                os.startfile(p)
                            except Exception:
                                try:
                                    import webbrowser
                                    webbrowser.open(p)
                                except Exception:
                                    pass

                        lbl.bind("<Button-1>", _open)
                        shown_image = True

                    except Exception as e:
                        print("Görsel yükleme hatası:", e)
                        lbl.config(text=f"{col}: [Görsel Yüklenemedi]", width="")
                        lbl.image = None
                        shown_image = True
                else:
                    fname = Path(text_value).name
                    lbl.config(text=f"{col}: [Görsel Bulunamadı: {fname}]", width="")
                    lbl.image = None
                    shown_image = True

            # --- 2. NORMAL METİN/SAYI KONTROLÜ (Görsel Değilse) ---
            if not shown_image:
                try:
                    # Normal metinler için genişlik 35 karakter olarak korunur
                    lbl.config(image="", text=f"{col}: {text_value}", compound=None, width=35)
                except Exception:
                    lbl.config(text=f"{col}: {text_value}",width=35,height=1)

                lbl.image = None
                try:
                    lbl.unbind('<Button-1>')
                except Exception:
                    pass
    def generate_report(self, analysis):
        lines = []
        for test, status in analysis.items():
            lines.append(f"{test}: {status}")
        return "\n".join(lines)

    def run_analysis(self):
        selected = self.tree.selection()
        if not selected:
            self.ai_textbox.delete("1.0", "end")
            self.ai_textbox.insert("end", "Lütfen bir satır seçin.\n")
            return

        item = self.tree.item(selected[0])
        satir_text = item["values"][0]

        idx = int(satir_text.split()[1])-1

        # CSV satırını al ve nan değerleri temizle
        row = self.logic.df.iloc[idx].fillna("bilinmiyor")

        # TEST
        print("RUN ANALYSİS ÇALIŞTI")
        self.labels[list(self.labels.keys())[0]].config(text="TEST")

        self.fill_labels_from_row(row)

        # Prompt oluştur
        prompt = self.build_clinical_prompt(row)

        # Textbox temizle
        self.ai_textbox.delete("1.0", "end")
        self.ai_textbox.insert("end", "AI analiz ediliyor...\n")

        # Asenkron AI çağrısı
        self.ask_ai_async(prompt)

    def ai_analysis_button(self):
        selection = self.tree.selection()
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

        import json
        final_text = ""
        # 1) Eğer string "AI hatası: Beklenmeyen yanıt yapısı:" ile başlıyorsa, JSON kısmını ayıkla
        if isinstance(ai_output, str) and "Beklenmeyen yanıt yapısı:" in ai_output:
            # İlk '{' karakterinden sonrasını al
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

        # 5) Metni temizle ve Textbox'a yazdır
        # (Metin sonundaki ANSI escape karakterlerini ve yabancı kelimeleri temizleyelim)
        if hasattr(self, "clean_ai_text"):
            final_text = self.clean_ai_text(final_text)

        self.ai_textbox.insert("end", final_text)
        # 6) --- OTOMATİK KONSÜLTASYON TESPİTİ ---
        # AI metni basıldıktan hemen sonra metni tarayıp konsültasyonları seçtiriyoruz
        if hasattr(self, "auto_detect_consultations"):
            self.auto_detect_consultations(final_text)

    def auto_detect_consultations(self, ai_text):
        text_lower = ai_text.lower()

        # 1. Önceki seçimleri temizle (Sıfırla)
        for code, var in self.consult_checks.items():
            var.set(False)

        detected_any = False

        # 2. Anahtar kelimelere göre konsültasyon kutucuklarını işaretle
        if any(k in text_lower for k in ["nefroloji", "böbrek", "kreatinin", "proteinüri"]):
            self.consult_checks["Nephrology"].set(True)
            detected_any = True

        if any(k in text_lower for k in ["kardiyoloji", "kalp", "perikardit", "ekg", "hipertansiyon"]):
            self.consult_checks["Cardiology"].set(True)
            detected_any = True

        if any(k in text_lower for k in ["endokrin", "steroid", "şeker", "diyabet", "tiroid"]):
            self.consult_checks["Endocrinology"].set(True)
            detected_any = True

        if any(k in text_lower for k in ["dermatoloji", "döküntü", "rash", "kelebek", "cilt"]):
            self.consult_checks["Dermatology"].set(True)
            detected_any = True

        # 3. Durum etiketini güncelle
        if detected_any:
            self.lbl_consult_status.config(
                text="⚠️ AI Analizine Göre Olası Konsültasyon İhtiyaçları İşaretlendi!",
                fg="#cc0000"
            )
        else:
            self.lbl_consult_status.config(
                    text="İnceleme Tamamlandı: Ek konsültasyon ihtiyacı tespit edilmedi.",
                    fg="#008800"
            )

    def clean_ai_text(self, text):
        import re
        # ANSI terminal renk/silme kodlarını temizle (\x1b...)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansi_escape.sub('', text)
        # Portekizce 'Não' kelimesini 'Yok' ile değiştir
        cleaned = re.sub(r'\bNão\b', 'Yok', cleaned, flags=re.IGNORECASE)
        return cleaned


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


    def update_ai_output(self, row):
        bulgular = "\n".join([f"- {col}: {row[col]}" for col in row.index])

        text = []
        text.append(" Klinik Değerlendirme")
        text.append("")
        text.append("📌 Hastaya ait klinik bulgular:")
        text.append(bulgular)
        text.append("")
        text.append("🔍 Bu bulgular AI tarafından analiz edilerek olası terapevtik tanılar üretilecektir.")
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
        Aşağıdaki Dermatology verilerini analiz et.
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

    def clean_ai_text(self,text):
        # ANSI escape dizilerini temizle
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansi_escape.sub('', text)
        # Portekizce 'Não' kelimelerini Türkçe 'Yok' ile değiştir
        cleaned = re.sub(r'\bNão\b', 'Yok', cleaned, flags=re.IGNORECASE)
        return cleaned

    def send_consultation(self):
        branch_mapping = {
            "Nephrology": "internal_disease",
            "Cardiology": "cardiology",
            "Endocrinology": "internal_disease",
            "Dermatology": "dermatology"
        }

        selected_targets = []
        for code, var in self.consult_checks.items():
            if var.get():
                target_branch = branch_mapping.get(code, code.lower())
                selected_targets.append((code, target_branch))

        if not selected_targets:
            from tkinter import messagebox
            messagebox.showwarning("Uyarı", "Lütfen en az bir konsültasyon branşı seçin!")
            return

        # KONSÜLTASYON PAKETİ (Kaynak bilgileri eksiksiz eklendi)
        consult_data = {
            "patient_row": getattr(self, "selected_row_index", None),
            "ai_summary": self.ai_textbox.get("1.0", "end").strip(),
            "from_module": "Rheumatology",
            "from_module_key": "rheumatology"
        }

        # Ana GUI'ye paketi kaydet
        self.gui.active_consultation = consult_data

        opened_branches = []
        for display_name, branch_key in selected_targets:
            if hasattr(self.gui, "branch_var"):
                self.gui.branch_var.set(branch_key)
                self.gui.on_branch_selected(None)
                opened_branches.append(display_name)

        from tkinter import messagebox
        messagebox.showinfo(
            "Konsültasyon Gönderildi",
            f"Seçilen branşlara ({', '.join(opened_branches)}) konsültasyon notu başarıyla iletildi."
        )

    def receive_consultation_reply(self, reply_info):
        from_mod = reply_info.get("from_module", "Kardiyoloji")
        summary = reply_info.get("ai_summary", "")

        # 1. Gelen konsültasyon notunu hafızaya al
        self.cardiology_consult_note = summary

        # 2. Arayüzde durumu güncelle (Kullanıcıya bilgi ver)
        if hasattr(self, "lbl_consult_status"):
            self.lbl_consult_status.config(
                text=f"✅ {from_mod} Konsültasyon Notu Alındı! Bütüncül analiz için 'Analiz Et' butonuna basabilirsiniz.",
                fg="#008800"
            )

        if "Cardiology" in self.consult_checks:
            self.consult_checks["Cardiology"].set(True)

    def build_clinical_prompt(self, row):
        text = (
            "Aşağıda bir Romatoloji hastasının klinik verileri ve alınan branş konsültasyonu yer almaktadır.\n"
            "Lütfen tüm verileri birlikte değerlendirerek bütüncül bir Romatoloji Raporu oluştur.\n"
            "Tüm yanıtı Türkçe olarak ver.\n\n"
            "--- HASTA MEVCUT BULGULARI ---\n"
        )

        for col in row.index:
            val = str(row[col])
            if any(val.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                text += f"- {col}: {val} (Görsel Kaydı Var)\n"
            else:
                text += f"- {col}: {val}\n"

        # Konsültasyon notu varsa prompta ekle
        if hasattr(self, "cardiology_consult_note") and self.cardiology_consult_note:
            text += (
                "\n--- ALINAN KARDİYOLOJİ KONSÜLTASYON NOTU ---\n"
                f"{self.cardiology_consult_note}\n"
                "--------------------------------------------------\n"
            )

        text += (
            "\nLütfen Kardiyoloji görüşünü ve hastanın verilerini birlikte ele alarak:\n"
            "1. Bütüncül Romatolojik Ön Tanı ve Otoimmün Tutulum Analizi\n"
            "2. Kardiyovasküler Bulguların Tedaviye ve İlaç Seçimine Etkisi\n"
            "3. Nihai Tedavi, İlaç Ayarlamaları ve Takip Planı\n"
            "başlıkları altında SON ÇIKTI raporunu üret.\n"
        )

        return text