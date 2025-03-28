import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json

class JSONTimeStampCopier:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON TimeStamp Saglabatajs")
        self.directories = {1: None, 2: None, 3: None, 4: None}
        self.create_widgets()

    def create_widgets(self):
        # Ievades lauki
        for i in range(1, 5):
            frame = tk.LabelFrame(self.root, text=f"Ievadiet mapi ar JSON failiem ({i})", padx=10, pady=5)
            frame.pack(padx=10, pady=2, fill="x")

            entry = tk.Entry(frame, width=50)
            entry.pack(side="left", padx=5)
            
            btn = tk.Button(frame, text="Pārlūkot...", command=lambda num=i: self.browse_directory(num))
            btn.pack(side="left")
            setattr(self, f"entry{i}", entry)

        #Pogas lietotaja darbibam
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(side="left", padx=5)
        tk.Button(btn_frame, text="Apstrādāt failus", command=self.process_files).pack(pady=2)
        tk.Button(btn_frame, text="Notīrīt visu", command=self.clear_all).pack(pady=2)
        
        tk.Button(control_frame, text="Dzēst timestamp failus", command=self.delete_timestamp_files, 
                 bg="#ff9999", fg="black").pack(side="left", padx=5)

        # Rezulti (logs apaksa)
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

    def clear_all(self):
        for i in range(1, 5):
            getattr(self, f"entry{i}").delete(0, tk.END)
            self.directories[i] = None
        self.result_text.delete(1.0, tk.END)

    def process_files(self):
        if not any(self.directories.values()):
            messagebox.showerror("Kļūda", "Lūdzu, atlasiet vismaz vienu mapi!")
            return

        self.result_text.delete(1.0, tk.END) #šie visi bus talak, bet šeit tieši zveido vertibas un saliek 0
        total_files = 0
        success_count = 0
        
        for dir_num, directory in self.directories.items():
            if not directory:
                continue

            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.json'):
                        total_files += 1
                        file_path = os.path.join(root, file)
                        copy_name = f"timestamp_{file}"
                        copy_path = os.path.join(root, copy_name)

                        try:
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                            
                            if 'time_stamp' not in data:
                                raise KeyError("Trūkst time_stamp lauka")
                            
                            with open(copy_path, 'w') as f:
                                json.dump({"time_stamp": data["time_stamp"]}, f, indent=4)
                            
                            self.result_text.insert(tk.END, f"[Mape {dir_num}] {file} -> {copy_name} ✅\n")
                            success_count += 1
                        
                        except Exception as e:
                            self.result_text.insert(tk.END, f"[Mape {dir_num}] {file} ❌ Kļūda: {str(e)}\n")

        # Kopsavilkums
        self.result_text.insert(tk.END, "\n=== REZULTĀTU KOPSUMMA ===\n")
        self.result_text.insert(tk.END, f"Kopējais failu skaits: {total_files}\n")
        self.result_text.insert(tk.END, f"Izdevās: {success_count}\n")
        self.result_text.insert(tk.END, f"Neizdevās: {total_files - success_count}")

        messagebox.showinfo("Pabeigts", f"Apstrādāti {total_files} faili")

    def delete_timestamp_files(self):
        if not any(self.directories.values()):
            messagebox.showerror("Kļūda", "Lūdzu, atlasiet vismaz vienu mapi!")
            return

        self.result_text.delete(1.0, tk.END)
        total_deleted = 0
        error_count = 0

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
                            error_count += 1

        # Kopsavilkums
        self.result_text.insert(tk.END, "\n=== DZĒŠŠANAS REZULTĀTI ===\n")
        self.result_text.insert(tk.END, f"Kopā izdzēsti faili: {total_deleted}\n")
        self.result_text.insert(tk.END, f"Neizdevās izdzēst: {error_count}\n")

        messagebox.showinfo("Pabeigts", f"Izdzēsti {total_deleted} timestamp faili")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONTimeStampCopier(root)
    root.mainloop()