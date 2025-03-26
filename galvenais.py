import tkinter as tk  # Importē Tkinter bibliotēku darbam ar GUI
from tkinter import ttk  # Importē uzlabotās Tkinter logrīku klases
from tkinter import filedialog  # Importē failu dialoga funkcionalitāti

class App:
    def __init__(self):  
        # Izveido logu
        self.root = tk.Tk()
        self.root.geometry('400x250+4000+500')  # Nosaka loga izmērus un atrašanās vietu ekrānā
        self.root.title("JSON datu vizualizācija")  # Nosaka loga nosaukumu
        
        # Izveido galveno ietvaru (frame) logā
        self.mainframe = tk.Frame(self.root)
        self.mainframe.pack(fill='both', expand=True, padx=10, pady=10)  # Izkārto ietvaru ar atstarpēm

        # Pievieno tekstu virs faila izvēles lauka
        ttk.Label(self.mainframe, text="Izvēlieties JSON failu:").pack(pady=5)

        # Izveido ievades lauku, lai parādītu izvēlētā faila ceļu
        self.file_path_var = tk.StringVar()  # Mainīgais, kurā glabāsies faila ceļš
        self.file_entry = ttk.Entry(self.mainframe, textvariable=self.file_path_var, width=40)
        self.file_entry.pack(pady=5, padx=5)

        # Pievieno pogu, lai atvērtu failu pārlūkošanas dialogu
        self.browse_button = ttk.Button(self.mainframe, text="Pārlūkot...", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Pievieno tekstu  virs vizualizācijas izvēles
        ttk.Label(self.mainframe, text="Izvēlieties vizualizācijas veidu:").pack(pady=5)

        # Izveido saraksta (Listbox) logrīku ar iespējamiem vizualizācijas veidiem
        self.visualization_options = ["Tabula", "Diagramma", "Kods"]  # Pieejamās opcijas
        self.listbox = tk.Listbox(self.mainframe, heigt=len(self.visualization_options))  # Izveido sarakstu ar tik daudz rindām, cik opciju
        for option in self.visualization_options:
            self.listbox.insert(tk.END, option)  # Pievieno opcijas sarakstam
        self.listbox.pack(pady=5)

        # Pievieno pogu, lai apstiprinātu izvēli
        self.confirm_button = ttk.Button(self.mainframe, text="Apstiprināt", command=self.confirm_selection)
        self.confirm_button.pack(pady=10)

        # Palaiž Tkinter galveno notikumu cilpu (lai logs paliktu atvērts)
        self.root.mainloop()

    def browse_file(self):
        """Atver failu pārlūkošanas dialogu un saglabā izvēlētā faila ceļu"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])  # Tikai JSON faili
        if file_path:
            self.file_path_var.set(file_path)  # Ievieto izvēlēto faila ceļu ievades laukā

    def confirm_selection(self):
        """Apstrādā izvēlēto vizualizācijas veidu un failu"""
        selected_index = self.listbox.curselection()  # Iegūst izvēlēto indeksu no saraksta
        if selected_index:
            selected_visualization = self.visualization_options[selected_index[0]]  # Iegūst izvēlēto vizualizācijas veidu
            print(f"Izvēlētais fails: {self.file_path_var.get()}")  # Izvada izvēlēto failu
            print(f"Izvēlētā vizualizācija: {selected_visualization}")  # Izvada izvēlēto vizualizācijas veidu

# Ja skripts tiek palaists tieši, izveido un palaiž lietotni
if __name__ == "__main__":
    App()
