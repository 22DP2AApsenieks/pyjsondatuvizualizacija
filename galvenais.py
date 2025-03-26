import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

class DataVisualizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Datu Vizualizācijas Rīks")
        
        self.file_paths = [None] * 4
        self.file_dataframes = [None] * 4
        
        self.create_widgets()
    
    def create_widgets(self):
        input_frame = tk.LabelFrame(self.root, text="Ievadiet failus", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")
        
        self.file_entries = []
        for i in range(4):
            row_frame = tk.Frame(input_frame)
            row_frame.pack(fill="x", pady=5)
            
            tk.Label(row_frame, text=f"Fails {i+1}:", width=10).pack(side="left")
            entry = tk.Entry(row_frame, width=50)
            entry.pack(side="left", padx=5)
            self.file_entries.append(entry)
            
            # Mainīsim lambda uz daļēju funkciju drošībai
            tk.Button(row_frame, text="Pārlūkot...", 
                    command=lambda idx=i: self.browse_file(idx)).pack(side="left")
        
        tk.Button(self.root, text="Pārbaudīt failus", command=self.check_files).pack(pady=10)
        
        self.result_frame = tk.LabelFrame(self.root, text="Rezultāti", padx=10, pady=10)
        self.result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.result_label = tk.Label(self.result_frame, text="Ievadiet failus un nospiediet 'Pārbaudīt failus'")
        self.result_label.pack()
    
    def browse_file(self, index):
        # Vienots filtrs visiem atbalstītajiem formātiem
        file_path = filedialog.askopenfilename(
            title="Atlasiet datu failu",
            filetypes=[
                ("Visi atbalstītie formāti", "*.csv;*.xlsx;*.json"),
                ("CSV faili", "*.csv"),
                ("Excel faili", "*.xlsx"),
                ("JSON faili", "*.json"),
                ("Visi faili", "*.*")
            ]
        )
        
        if file_path:
            self.file_entries[index].delete(0, tk.END)
            self.file_entries[index].insert(0, file_path)
            self.file_paths[index] = file_path
    
    def check_files(self):
        results = []
        success = True
        
        def is_valid_line(line):
            """Check if line contains at least one non-whitespace character"""
            return bool(line and not line.isspace())

        for i, path in enumerate(self.file_paths):
            if not path:
                results.append(f"Fails {i+1}: ❌ Nav norādīts")
                success = False
                continue
            
            try:
                valid_lines = 0
                total_lines = 0
                
                # Raw line-by-line validation
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        total_lines += 1
                        if is_valid_line(line.strip()):
                            valid_lines += 1
                
                # Then parse normally for DataFrame
                if path.endswith('.json'):
                    try:
                        df = pd.read_json(path)
                    except ValueError:
                        df = pd.read_json(path, lines=True)
                else:
                    df = pd.read_csv(path) if path.endswith('.csv') else pd.read_excel(path)
                
                self.file_dataframes[i] = df
                results.append(f"Fails {i+1}: ✅ Nolasītas {valid_lines} rindas (no {total_lines} kopā)")
            except Exception as e:
                results.append(f"Fails {i+1}: ❌ Kļūda: {type(e).__name__} - {str(e)}")
                success = False
                self.file_dataframes[i] = None
        
        self.result_label.config(text="\n".join(results))
        if success:
            messagebox.showinfo("Veiksmīgi", "Visi faili nolasīti!")
        else:
            messagebox.showwarning("Brīdinājums", "Daži faili nav nolasīti!")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataVisualizationApp(root)
    root.mainloop()