import tkinter as tk
from tkinter import ttk

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

        self.list_frame = tk.LabelFrame(self.scroll_frame, text="AI liste",height=20,width=80)
        self.list_frame.grid(row=self.next_row, column=0, sticky="nsew")

        # Satır seçme listesi (CSV satırlar için)
        self.list_rows = tk.Listbox(self.list_frame, font=("Arial", 11), height=5)
        self.list_rows.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        # Satır seçildiğinde formu dolduracak event
        self.list_rows.bind("<<ListboxSelect>>", self.on_row_selected)

        # Scrollbar
        list_rows_scroll = tk.Scrollbar(self.list_frame, orient="vertical", command=self.list_rows.yview)
        list_rows_scroll.grid(row=0, column=1, sticky="ns")
        self.list_rows.config(yscrollcommand=list_rows_scroll.set)
        tk.Frame(self.list_frame, height=40).grid(row=1, column=0)


        #---AI Çıktı Alanı----
        self.ai_textbox = tk.Text(self.scroll_frame,height=10,width=40)
        self.ai_textbox.grid(row=self.next_row+1,column=0,columnspan=5,sticky="nsew",pady=20)

        #AI analiz butonu
        btn = tk.Button(self.scroll_frame, text="Analiz et", command=self.run_analysis)
        btn.grid(row=self.next_row+2, column=0, columnspan=5, pady=10)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TButton",
                        font=("Segoe UI", 11, "bold"),
                        padding=6,
                        background="#0055aa",
                        foreground="white")

        style.map("TButton",
                  background=[("active", "#0077cc")])

        # --- ALT BOŞLUK ---
        tk.Frame(self.scroll_frame, height=50).grid(row=self.next_row+3,column=0)

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
        index = selection[0]
        row = self.logic.df.iloc[index]

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
        for test_name,entry in self.entries.items():
            value = entry.get().strip()
            if value == "":
                continue
            try:
                value = float(value)
            except:
                pass
            results[test_name] = value
        return results

    def analyze_values(self,values):
        analysis = {}

        for category,subcats in self.current_module.items():
            if category == "lab":
                for subcat,tests in subcats.items():
                    for test_name,ranges in tests.items():
                        if test_name not in values:
                            continue

                        val = values[test_name]
                        results = None

                        #Yaş grubu varsa adult/child/elderly seçimi
                        if isinstance(ranges,dict):
                            #şimdilik adult
                            ranges = ranges.get("adult",ranges.get("child",ranges.get("elderly")))

                        for low,high,label in ranges:
                            if low <= val <= high:
                                result = label
                                break

                        analysis[test_name] = result

            elif category in ["imaging","clinical"]:
                for subcat,tests in subcats.items():
                    for test_name,ranges in tests.items():
                        if test_name not in values:
                            continue

                        val = values[test_name]
                        result=None

                        for low,high,label in ranges:
                            if low <= val <= high:
                                result = label
                                break

                        analysis[test_name] = result

        return analysis

    def generate_report(self,analysis):
        lines = []
        for test,status in analysis.items():
            lines.append(f"{test}: {status}")
        return "\n".join(lines)

    def run_analysis(self):
        values = self.collect_values()
        analysis = self.analyze_values(values)
        prompt = f"""
            Sen bir klinik karar destek sistemisin.

            Hasta verileri:
            {values}

            Python analiz sonuçları:
            {analysis}

            Görev:
            - Laboratuvar, görüntüleme ve klinik bulguları birlikte değerlendir
            - Olası tanıları belirt
            - Risk skorlarını yorumla
            - Ek test öner
            - Klinik olarak anlamlı bir özet oluştur
            """
        ai_output = self.logic.ask_ai(prompt)

        self.ai_textbox.delete("1.0",tk.END)
        self.ai_textbox.insert(tk.END,ai_output)

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