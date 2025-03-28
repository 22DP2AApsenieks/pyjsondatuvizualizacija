import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import sys


class JSONTimeStampSaglabatajs:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON TimeStamp Saglabātājs")
        self.directories = {1: None, 2: None, 3: None, 4: None}  # Mapei izvēlētas direktorijas//t.i. 4 logu ievade apstradei
        self.create_widgets()

    def create_widgets(self):
        """Izveido grafiskos elementus (logrīkus) lietotāja saskarnei."""
        for i in range(1, 5):
            frame = tk.LabelFrame(self.root, text=f"Ievadiet mapi ar JSON failiem ({i})", padx=10, pady=5)
            frame.pack(padx=10, pady=2, fill="x")

            entry = tk.Entry(frame, width=50)
            entry.pack(side="left", padx=5)
            
            btn = tk.Button(frame, text="Pārlūkot...", command=lambda num=i: self.browse_directory(num))
            btn.pack(side="left")
            setattr(self, f"entry{i}", entry)  # atsauce uz ievades lauku

        # Pogas lodgu izveide
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(side="left", padx=5)
        tk.Button(btn_frame, text="Apstrādāt failus", command=self.process_files).pack(pady=2)
        tk.Button(btn_frame, text="Notīrīt visu", command=self.clear_all).pack(pady=2)
        
        tk.Button(control_frame, text="Dzēst timestamp failus", command=self.delete_timestamp_files, 
                 bg="#ff9999", fg="black").pack(side="left", padx=5)

        # Rezultātu attēlošanas logs
        self.result_frame = tk.LabelFrame(self.root, text="Rezultāti", padx=10, pady=10)
        self.result_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        self.result_text = tk.Text(self.result_frame, height=15, width=85)
        self.result_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.result_frame)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

    def browse_directory(self, dir_num):
        """Atver dialoglogu, lai lietotājs varētu izvēlēties direktoriju."""
        directory = filedialog.askdirectory(title=f"Atlasiet mapi {dir_num}")
        if directory:
            getattr(self, f"entry{dir_num}").delete(0, tk.END)
            getattr(self, f"entry{dir_num}").insert(0, directory)
            self.directories[dir_num] = directory

    def clear_all(self):
        """Notīra visus ievades laukus un rezultātu logu."""
        for i in range(1, 5):
            getattr(self, f"entry{i}").delete(0, tk.END)
            self.directories[i] = None
        self.result_text.delete(1.0, tk.END)

    def process_files(self):
        """Apstrādā JSON failus, saglabājot timestamp datus atsevišķā failā."""
        if not any(self.directories.values()):
            messagebox.showerror("Kļūda", "Lūdzu, atlasiet vismaz vienu mapi!")
            return

        self.result_text.delete(1.0, tk.END)
        total_files, success_count = 0, 0
        
        for dir_num, directory in self.directories.items():
            if not directory:
                continue

            try:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.lower().endswith('.json'):
                            total_files += 1
                            file_path = os.path.join(root, file)
                            copy_path = os.path.join(root, f"timestamp_{file}")

                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                
                                if 'time_stamp' not in data:
                                    raise KeyError("Trūkst 'time_stamp' lauka")
                                
                                copy_data = {
                                    "time_stamp": data["time_stamp"],
                                    "local_info_index": data.get('local', {}).get('info', {}).get('index', 'N/A'),
                                    "alternate_info_index": data.get('alternate', {}).get('info', {}).get('index', 'N/A')
                                }
                                
                                with open(copy_path, 'w', encoding='utf-8') as f:
                                    json.dump(copy_data, f, indent=4, ensure_ascii=False)
                                
                                self.result_text.insert(tk.END, f"[Mape {dir_num}] {file} -> timestamp_{file} ✅\n")
                                success_count += 1
                            except Exception as e:
                                self.result_text.insert(tk.END, f"[Mape {dir_num}] {file} ❌ Kļūda: {str(e)}\n")
            except Exception as e:
                self.result_text.insert(tk.END, f"Kļūda mapei {dir_num}: {str(e)}\n")

        self.result_text.insert(tk.END, f"\n=== REZULTĀTU KOPSUMMA ===\nKopējais failu skaits: {total_files}\nIzdevās: {success_count}\nNeizdevās: {total_files - success_count}\n")
        messagebox.showinfo("Pabeigts", f"Apstrādāti {total_files} faili")

    def delete_timestamp_files(self):
        """Dzēš visus timestamp failus atlasītajās mapēs."""
        if not any(self.directories.values()):
            messagebox.showerror("Kļūda", "Lūdzu, atlasiet vismaz vienu mapi!")
            return

        self.result_text.delete(1.0, tk.END)
        total_deleted = 0

        for dir_num, directory in self.directories.items():
            if not directory:
                continue
            
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.startswith("timestamp_"):
                        full_path = os.path.join(root, file)
                        try:
                            os.remove(full_path)
                            self.result_text.insert(tk.END, f"Izdzēsts: {full_path} ✅\n")
                            total_deleted += 1
                        except Exception as e:
                            self.result_text.insert(tk.END, f"Neizdevās izdzēst {full_path} ❌: {str(e)}\n")
        
        messagebox.showinfo("Pabeigts", f"Izdzēsti {total_deleted} timestamp faili")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONTimeStampSaglabatajs(root)
    root.mainloop()
