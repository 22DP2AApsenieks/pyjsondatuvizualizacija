import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import shutil

class JSONCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Kopētājs")
        
        self.directories = {1: None, 2: None, 3: None, 4: None}
        self.create_widgets()
    
    def create_widgets(self):
        # Izveidojam 4 ievades rāmjus
        for i in range(1, 5):
            frame = tk.LabelFrame(self.root, text=f"Ievadiet mapi ar JSON failiem ({i})", padx=10, pady=5)
            frame.pack(padx=10, pady=2, fill="x", expand=True)
            
            entry = tk.Entry(frame, width=50)
            entry.pack(side="left", padx=5)
            
            btn = tk.Button(frame, text="Pārlūkot...", command=lambda num=i: self.browse_directory(num))
            btn.pack(side="left")
            
            # Saglabājam atsauces uz entry widgetiem
            setattr(self, f"entry{i}", entry)

        # Kontrolelementi
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        tk.Button(control_frame, text="Apstrādāt failus", command=self.process_files).pack(side="left", padx=5)
        tk.Button(control_frame, text="Notīrīt laukus", command=self.clear_fields).pack(side="left")

        # Rezultātu logs
        self.result_frame = tk.LabelFrame(self.root, text="Rezultāti", padx=10, pady=10)
        self.result_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.result_text = tk.Text(self.result_frame, height=15, width=85)
        self.result_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.result_frame)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

    def browse_directory(self, dir_num):
        directory = filedialog.askdirectory(title=f"Atlasiet mapi {dir_num}")
        if directory:
            getattr(self, f"entry{dir_num}").delete(0, tk.END)
            getattr(self, f"entry{dir_num}").insert(0, directory)
            self.directories[dir_num] = directory

    def clear_fields(self):
        for i in range(1, 5):
            getattr(self, f"entry{i}").delete(0, tk.END)
            self.directories[i] = None
        self.result_text.delete(1.0, tk.END)

    def process_files(self):
        # Pārbauda vai ir vismaz viena mape
        if not any(self.directories.values()):
            messagebox.showerror("Kļūda", "Lūdzu, atlasiet vismaz vienu mapi!")
            return

        self.result_text.delete(1.0, tk.END)
        total_files = 0
        success_count = 0
        
        # Apstrādājam atlasītās mapes
        for dir_num, directory in self.directories.items():
            if not directory:
                continue  # Izlaižam neizvēlētās mapes
            
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.json'):
                        total_files += 1
                        file_path = os.path.join(root, file)
                        
                        try:
                            pd.read_json(file_path)  # JSON validācija
                            copy_name = f"kopija_{file}"
                            copy_path = os.path.join(root, copy_name)
                            
                            shutil.copy(file_path, copy_path)
                            self.result_text.insert(tk.END, f"Mape {dir_num}: {file} -> {copy_name} ✅\n")
                            success_count += 1
                        except Exception as e:
                            self.result_text.insert(tk.END, f"Mape {dir_num}: {file} ❌ Kļūda: {str(e)}\n")

        # Kopsavilkums
        self.result_text.insert(tk.END, "\n=== Kopsavilkums ===\n")
        self.result_text.insert(tk.END, f"Kopējais failu skaits: {total_files}\n")
        self.result_text.insert(tk.END, f"Veiksmīgi nokopēti: {success_count}\n")
        self.result_text.insert(tk.END, f"Neveiksmīgi mēģinājumi: {total_files - success_count}")

        if total_files == success_count:
            messagebox.showinfo("Pabeigts", "Visas kopēšanas operācijas veiksmīgas!")
        else:
            messagebox.showwarning("Pabeigts", f"Neizdevās nokopēt {total_files - success_count} failus!")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONCopierApp(root)
    root.mainloop()