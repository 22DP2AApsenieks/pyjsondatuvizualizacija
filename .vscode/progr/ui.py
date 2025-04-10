import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class JSONTimeStampUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("JSON Datu Saglabātājs un vizualizācijas veidotājs")
        self.directories = {1: None, 2: None, 3: None, 4: None}
        self.create_widgets()
        self.mode_var = tk.StringVar(value="2+0 Aggregation")
        self.process_command = None
        self.clear_command = None
        self.vizualize_command = None

    def create_widgets(self):
        # Mode selection
        mode_frame = tk.LabelFrame(self, text="Parsing Mode", padx=10, pady=5)
        mode_frame.pack(padx=10, pady=2, fill="x")
        ttk.Radiobutton(mode_frame, text="2+0 Aggregation", variable=self.mode_var,
                        value="2+0 Aggregation").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="1+1HSB Protection", variable=self.mode_var,
                        value="1+1HSB Protection").pack(side=tk.LEFT, padx=5)

        # Directory inputs
        self.dir_entries = {}
        self.id_entries = {}
        for i in range(1, 5):
            frame = tk.LabelFrame(self, text=f"Ievadiet mapi un identifikatoru ({i})", padx=10, pady=5)
            frame.pack(padx=10, pady=2, fill="x")
            
            dir_entry = tk.Entry(frame, width=40)
            dir_entry.pack(side=tk.LEFT, padx=5)
            tk.Button(frame, text="Pārlūkot...", command=lambda num=i: self.browse_directory(num)
                      ).pack(side=tk.LEFT, padx=5)
            
            tk.Label(frame, text="ID:").pack(side=tk.LEFT, padx=5)
            id_entry = tk.Entry(frame, width=15)
            id_entry.pack(side=tk.LEFT)
            
            self.dir_entries[i] = dir_entry
            self.id_entries[i] = id_entry

        # Control buttons
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10)
        self.process_btn = tk.Button(control_frame, text="Apstrādāt failus", command=self.process)
        self.process_btn.pack(pady=2, side=tk.LEFT, padx=5)
        self.clear_btn = tk.Button(control_frame, text="Notīrīt visu", command=self.clear)
        self.clear_btn.pack(pady=2, side=tk.LEFT, padx=5)
        self.vizualize_btn = tk.Button(control_frame, text="Parādīt vizualizāciju", command=self.vizualize)
        self.vizualize_btn.pack(pady=2, side=tk.LEFT, padx=5)

        # Results
        self.result_frame = tk.LabelFrame(self, text="Rezultāti", padx=10, pady=10)
        self.result_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.result_text = tk.Text(self.result_frame, height=15, width=100)
        self.result_text.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.result_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.result_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.result_text.yview)

    def browse_directory(self, dir_num):
        directory = filedialog.askdirectory(title=f"Atlasiet mapi {dir_num}")
        if directory:
            self.dir_entries[dir_num].delete(0, tk.END)
            self.dir_entries[dir_num].insert(0, directory)

    def clear_directory(self, dir_num):
        self.dir_entries[dir_num].delete(0, tk.END)

    def clear_identifier(self, dir_num):
        self.id_entries[dir_num].delete(0, tk.END)

    def clear_results(self):
        self.result_text.delete(1.0, tk.END)

    def get_directories(self):
        return {i: self.dir_entries[i].get().strip() for i in range(1, 5)}

    def get_identifiers(self):
        return {i: self.id_entries[i].get().strip() for i in range(1, 5)}

    def get_mode(self):
        return self.mode_var.get()

    def append_results(self, text):
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def set_process_command(self, command):
        self.process = command

    def set_clear_command(self, command):
        self.clear = command

    def set_vizualize_command(self, command):
        self.vizualize = command