import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import glob #meklē failus pēc nosaukuma parauga

class JSONTimeStampSaglabatajs:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON TimeStamp Saglabātājs")
        self.directories = {1: None, 2: None, 3: None, 4: None} #izveido 4 tuksus mainigos
        self.create_widgets()

    def create_widgets(self):
        for i in range(1, 5):
            frame = tk.LabelFrame(self.root, text=f"Ievadiet mapi ar JSON failiem ({i})", padx=10, pady=5)
            frame.pack(padx=10, pady=2, fill="x")
            entry = tk.Entry(frame, width=50)
            entry.pack(side="left", padx=5)
            btn = tk.Button(frame, text="Pārlūkot...", command=lambda num=i: self.browse_directory(num))
            btn.pack(side="left")
            setattr(self, f"entry{i}", entry)
        
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Apstrādāt failus", command=self.process_files).pack(pady=2)
        tk.Button(control_frame, text="Notīrīt visu", command=self.clear_all).pack(pady=2)
        tk.Button(control_frame, text="Dzēst timestamp failus", command=self.delete_timestamp_files, bg="#ff9999").pack(pady=2)
        
        self.result_frame = tk.LabelFrame(self.root, text="Rezultāti", padx=10, pady=10)
        self.result_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.result_text = tk.Text(self.result_frame, height=15, width=85)
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(self.result_frame)
        scrollbar.pack(side="right", fill="y")
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)

    def browse_directory(self, dir_num):
        directory = filedialog.askdirectory(title=f"Atlasiet mapi {dir_num}") #lietotajs var izveleties mapi
        if directory: #parbauda vai lietotajs tiešām ir izvelējis mapi
            getattr(self, f"entry{dir_num}").delete(0, tk.END) #iztīra iepriekšejo saturu
            getattr(self, f"entry{dir_num}").insert(0, directory) #Ievieto lietotāja izvēlēto direktoriju atbilstošajā Entry laukā.
            self.directories[dir_num] = directory #saglabā izvēlēto direktoriju
    def clear_all(self):
        for i in range(1, 5):
            getattr(self, f"entry{i}").delete(0, tk.END)
            self.directories[i] = None
        self.result_text.delete(1.0, tk.END)

    def load_error_mapping(self, directory):
        error_mapping = {}
        error_files = glob.glob(os.path.join(directory, '*.txt'))
        for error_file in error_files:
            try:
                with open(error_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for line in lines:
                    if not line.strip():
                        continue
                    parts = line.split(';')
                    if len(parts) < 4:
                        continue
                    date_field, time_field, error_desc = parts[1].strip(), parts[2].strip(), parts[-1].strip()
                    if error_desc.startswith("Aggregation FSM state changed"):
                        error_mapping[(date_field, time_field)] = error_desc
            except Exception as e: #saglaba erorus, ja fails nav izveidots vai ir tukšs(vai nepareizs formats)
                messagebox.showerror("Kļūda", f"Kļūda, lasot failu {error_file}: {str(e)}")
        return error_mapping

    def process_files(self):
        if not any(self.directories.values()):
            messagebox.showerror("Kļūda", "Lūdzu, atlasiet vismaz vienu mapi!")
            return

        self.result_text.delete(1.0, tk.END)
        total_files, success_count, skipped_count = 0, 0, 0

        for dir_num, directory in self.directories.items():
            if not directory:
                continue
            
            error_mapping = self.load_error_mapping(directory)
            
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
                            date_part, time_part = data["time_stamp"].split(' ')
                            error_desc = error_mapping.get((date_part, time_part), "N/A")
                            if error_desc == "N/A":
                                skipped_count += 1
                                continue
                            with open(copy_path, 'w', encoding='utf-8') as f:
                                json.dump({"time_stamp": data["time_stamp"], "error_description": error_desc}, f, indent=4)
                            success_count += 1
                        except Exception as e:
                            self.result_text.insert(tk.END, f"[Mape {dir_num}] {file} Kļūda: {str(e)}\n")
            
        summary = f"\n=== REZULTĀTU KOPSUMMA ===\nKopējais JSON failu skaits: {total_files}\nIzdevās saglabāt: {success_count}\nIzlaisti: {skipped_count}\n"
        self.result_text.insert(tk.END, summary)
        messagebox.showinfo("Pabeigts", f"Apstrādāti {total_files} faili")

    def delete_timestamp_files(self):
        if not any(self.directories.values()):
            messagebox.showerror("Kļūda", "Lūdzu, atlasiet vismaz vienu mapi!")
            return
        self.result_text.delete(1.0, tk.END)
        total_deleted = 0
        for directory in self.directories.values():
            if not directory:
                continue
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.startswith("timestamp_"):
                        try:
                            os.remove(os.path.join(root, file))
                            total_deleted += 1
                        except Exception as e:
                            self.result_text.insert(tk.END, f"Neizdevās izdzēst {file}: {str(e)}\n")
        messagebox.showinfo("Pabeigts", f"Izdzēsti {total_deleted} timestamp faili")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONTimeStampSaglabatajs(root)
    root.mainloop()