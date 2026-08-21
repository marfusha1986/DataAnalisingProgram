import tkinter as tk
from tkinter import ttk

class CardiologyUI:
    def __init__(self, root, logic, module):
        self.root = root
        self.logic = logic
        self.current_module = module

        self.root.title("Oncology Module")
        self.root.geometry("1100x800")

        # --- Toplevel responsive ---
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- Main frame ---
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # --- Header ---
        header = tk.Label(self.main_frame, text="Cardiology Clinical Panel",
                          font=("Arial", 18, "bold"))
        header.grid(row=0, column=0, pady=10, sticky="w")

        # --- Scrollable area (canvas yok!) ---
        container = tk.Frame(self.main_frame)
        container.grid(row=1, column=0, sticky="nsew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # İçerik frame'i
        self.scroll_frame = tk.Frame(container)
        self.scroll_frame.grid(row=0, column=0, sticky="nsew")

        # Scrollbar'ı frame'e bağlamak için canvas kullanmadan çözüm:
        def _on_mousewheel(event):
            scrollbar.set(scrollbar.get()[0] - event.delta/1200,
                          scrollbar.get()[1] - event.delta/1200)

        self.scroll_frame.bind_all("<MouseWheel>", _on_mousewheel)

        # --- AI output ---
        self.ai_output = tk.Text(self.main_frame, height=10)
        self.ai_output.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # --- AI button ---
        btn_ai = tk.Button(self.main_frame, text="AI Analiz Yap",
                           command=self.run_ai)
        btn_ai.grid(row=3, column=0, pady=10, sticky="e")

    def run_ai(self):
        self.ai_output.insert("end", "Cardiology AI çalıştı...\n")
