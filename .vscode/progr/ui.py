import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from galvenais import JSONTimeStampSaglabatajs
from vizualization import Visualization

class JSONTimeStampSaglabatajsUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Datu Saglabātājs un vizualizācijas veidotājs")
        self.logic = JSONTimeStampSaglabatajs()
        self.visualization = Visualization(self.logic)
        self.create_widgets()

    def create_widgets(self):
        # Režīma izvēle
        mode_frame = tk.LabelFrame(self.root, text="Parsing Mode", padx=10, pady=5)
        mode_frame.pack(padx=10, pady=2, fill="x")
        self.mode_var = tk.StringVar(value="2+0 Aggregation")
        ttk.Radiobutton(mode_frame, text="2+0 Aggregation", variable=self.mode_var,
                       value="2+0 Aggregation").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="1+1HSB Protection", variable=self.mode_var,
                       value="1+1HSB Protection").pack(side=tk.LEFT, padx=5)
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        

        # Mapes ievade
        for i in range(1, 5):
            frame = tk.LabelFrame(self.root, text=f"Insert map and ID ({i})", padx=10, pady=5)
            frame.pack(padx=10, pady=2, fill="x")
            
            dir_entry = tk.Entry(frame, width=40)
            dir_entry.pack(side=tk.LEFT, padx=5)
            tk.Button(frame, text="Search...", command=lambda num=i: self.browse_directory(num)
                      ).pack(side=tk.LEFT)
            
            tk.Label(frame, text="ID:").pack(side=tk.LEFT, padx=5)
            id_entry = tk.Entry(frame, width=15)
            id_entry.pack(side=tk.LEFT)
            
            setattr(self, f"dir_entry{i}", dir_entry)
            setattr(self, f"id_entry{i}", id_entry)

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Process, Clear, Visualize buttons
        tk.Button(control_frame, text="Merge failes", command=self.process_files).pack(pady=2)
        tk.Button(control_frame, text="Clean all", command=self.clear_all).pack(pady=2)
        tk.Button(control_frame, text="Show animation", command=self.vizualize_all).pack(pady=2)

        # Navigācijas pogas
        nav_frame = tk.Frame(control_frame)
        nav_frame.pack(pady=5)
        tk.Button(nav_frame, text="Back", command=self.visualization.previous_visualizations, bg="lightcoral", fg="black").pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Next", command=self.visualization.next_visualizations, bg="lightgreen", fg="black").pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="About(LV/ENG)", command=self.about ).pack(pady=20)


        # Rezultati
        self.result_frame = tk.LabelFrame(self.root, text="Results", padx=10, pady=10)
        self.result_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.result_text = tk.Text(self.result_frame, height=15, width=100)
        self.result_text.pack(side=tk.LEFT, fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.result_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.result_text.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.result_text.yview)

    def browse_directory(self, dir_num):
        directory = filedialog.askdirectory(title=f"Chose map {dir_num}")
        if directory:
            getattr(self, f"dir_entry{dir_num}").delete(0, tk.END)
            getattr(self, f"dir_entry{dir_num}").insert(0, directory)
            self.logic.directories[dir_num] = directory

    def clear_all(self):
        for i in range(1, 5):
            getattr(self, f"dir_entry{i}").delete(0, tk.END)
            getattr(self, f"id_entry{i}").delete(0, tk.END)
            self.logic.directories[i] = None
        self.result_text.delete(1.0, tk.END)

    def process_files(self):
        identifiers = {}
        for dir_num in self.logic.directories:
            if self.logic.directories[dir_num]:
                identifier = getattr(self, f"id_entry{dir_num}").get().strip()
                identifiers[dir_num] = identifier

                

        try:
            result = self.logic.process_files(self.logic.directories, identifiers, self.mode_var.get())
            
            summary = (
                f"\n=== SUMMARY ===\n"
                f"Total JSON files processed: {result['total_files']}\n"
                f"Successfully saved: {result['success_count']}\n"
                f"Skipped: {result['skipped_count']}\n"
                f"Merged file saved at: {result['merged_file_path']}\n"
                f"errors: {result.get('error_msg',)}\n"
                f"{result.get('eth_ip_errors',)}\n"
                f"{result.get('eth_mac_errors',)}\n"
                f"{result.get('M')}"

            )
            self.result_text.insert(tk.END, summary)
            messagebox.showinfo("Complete", f"Processed {result['total_files']} files")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.result_text.insert(tk.END, f"Error: {str(e)}\n")
            

    def animacijaspaskaidrojums(self):
        paskaidrojums_logs = tk.Toplevel(self.root)
        paskaidrojums_logs.title("Vizualization explanation")

        frame = tk.Frame(paskaidrojums_logs, padx=10, pady=10)
        frame.pack()

        # Zaļš
        zalais = tk.Label(frame, text="[port] Green: Port is active (UP status)",
                        bg="lightgreen", anchor="w", width=50, font=("Arial", 12))
        zalais.pack(fill="x", pady=2)

        # Dzeltens
        dzeltens = tk.Label(frame, text="[port] Yellow: Trafic port(datu traffic_port)",
                            bg="lightyellow", anchor="w", width=50, font=("Arial", 12))
        dzeltens.pack(fill="x", pady=2)

        # Sarkans
        sarkans = tk.Label(frame, text="[port] Red: Not active",
                        bg="lightcoral", anchor="w", width=50, font=("Arial", 12))
        sarkans.pack(fill="x", pady=2)

        ps = tk.Label(frame, text="If the visualization is empty (not displayed), then in this case the relationship between the eventlog and the json file could not be found.", 
                         anchor="w", width=50, font=("Arial", 12))
        ps.pack(fill="x", pady=2)

        ok_btn = tk.Button(paskaidrojums_logs, text="Okey", command=paskaidrojums_logs.destroy)
        ok_btn.pack(pady=10)

    def about(self):
        about_logs = tk.Toplevel(self.root)
        about_logs.title("About")

        frame = tk.Frame(about_logs, padx=30, pady=40)
        frame.pack()

        apraksts = ( #sll this vill be dispalyed for user
            "LV(below is ENG)"
            "\n"
            "\n"
            "Šī programma ir izstrādāta SAF Tehnikas ražoto iekārtu 'Integra' datu pārraides ceļa vizualizācijai. Tā apstrādā JSON žurnāla datus un eventlog ierakstus, apvienojot tos vienotā vizualizācijā."
            "\n"
            "Galvenās iespējas:\n"
            "• Apstrāde līdz pat 4 dažādām mapēm ar JSON un uventlog failiem.\n"
            "• Atbalsta divus darbības režīmus: '2+0 Aggregation' un '1+1 HSB Protection'.\n"
            "• Spēj automātiski izvilkt, filtrēt un saglabāt laika zīmogus un citas būtiskas vērtības.\n"
            "• Izveido apvienotu žurnālu failu ar visiem datiem.\n"
            "• Sniedz datu apkopojumu (cik failu apstrādāti, izlaisti utt.).\n"
            "• Nodrošina vienkāršu un skaidru vizualizāciju – ar krāsām un paskaidrojumiem.\n"
            "\n"
            "Kā lietot:\n"
            "1. Palaižiet programmu\n"
            "2. Zemāk ievadi mapes ceļu (vai izmanto 'Pārlūkot') un identificējošo ID (piemēram, ID: 11).\n"
            "3. Spied 'Apstrādāt failus' – programma analizēs JSON datus un parādīs rezultātu.\n"
            "4. Izmanto 'Parādīt vizualizāciju', lai redzētu datu ceļu, aprakstu un statusa krāsas un portu aktivitāti.\n"
            "   – Zaļš: Ports aktīvs\n"
            "   – Dzeltens: Notiek datu satiksme\n"
            "   – Sarkans: Ports neaktīvs vai neeksistē\n"
            "5. Navigē starp vizualizācijām ar pogām 'Next' un 'Back'.\n"
            "6. Spied 'Notīrīt visu', lai iztīrītu ievadlaukus un sāktu no jauna.\n"
            "\n"
            "Piezīme:\n"
            "– Vizualizācijas tiek rādītas uz esošā loga bāzes, netiek atvērti lieki logi.\n"
            "– Ja rodas kļūdas, tās tiks parādītas rezultātu sadaļā un paziņojumā.\n"
            "\n"
            "Izstrāde sākta: 2025gada marta beigās\n"
            "Versija: 1.0\n"
            "\n"
            "\n"
            "\n"
            "\n"
            "ENG"
            "\n"
            "This program is designed to visualize the data transmission path of SAF Tehnika’s ‘Integra’ devices.\n"
            "It processes JSON log data and eventlog entries, combining them into a unified visualization.\n\n"

            "Main features:\n"
            "• Processes up to 4 different folders with JSON and eventlog files.\n"
            "• Supports two operating modes: '2+0 Aggregation' and '1+1 HSB Protection'.\n"
            "• Can automatically extract, filter, and save timestamps and other key values.\n"
            "• Generates a combined log file with all relevant data.\n"
            "• Provides data summary (e.g., how many files were processed, skipped, etc.).\n"
            "• Delivers a simple and clear visualization – with colors and explanations.\n\n"

            "How to use:\n"
            "1. Launch the program\n"
            "2. Enter the folder path below (or use ‘Browse’) and provide an identifying ID (e.g., ID: 11).\n"
            "3. Click ‘Process Files’ – the program will analyze the JSON data and display the result.\n"
            "4. Use ‘Show Visualization’ to see the data path, descriptions, status colors, and port activity.\n"
            "   – Green: Port is active\n"
            "   – Yellow: Data traffic is ongoing\n"
            "   – Red: Port is inactive or does not exist\n"
            "5. Navigate between visualizations using the ‘Next’ and ‘Back’ buttons.\n"
            "6. Click ‘Clear All’ to reset the input fields and start fresh.\n\n"

            "Note:\n"
            "– Visualizations are shown in the existing window; no unnecessary windows are opened.\n"
            "– If any errors occur, they will appear in the result section and via popup notifications.\n\n"
            "Development started: End of March 2025\n"
            "Version: 1.0"


            
        )

        text_widget = tk.Text(frame, wrap="word", height=30, width=80, font=("Arial", 11))
        text_widget.insert(tk.END, apraksts)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack()

        tk.Button(about_logs, text="Close", command=about_logs.destroy).pack(pady=10)



    def vizualize_all(self):
        self.animacijaspaskaidrojums()
        self.visualization.vizualize_all()
    