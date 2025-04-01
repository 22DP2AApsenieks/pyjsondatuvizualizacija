import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import glob
import re
import webbrowser
from datetime import datetime

class JSONTimeStampSaglabatajs:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Datu Saglabātājs un vizualizācijas veidotājs")
        self.directories = {1: None, 2: None, 3: None, 4: None}
        self.reason_ids = { #šie uzreiz(orģināli error id cipari) nomaina uz eror nosaukumu
            "2+0 Aggregation": {
                0: "Configuration Commit (AGGR_FSM_RSN_CFG_COMMIT)",
                1: "Enable (AGGR_FSM_RSN_ENABLE)",
                2: "Configured as Primary (AGGR_FSM_RSN_CFG_IS_PRIMARY)",
                3: "Configured as Secondary (AGGR_FSM_RSN_CFG_IS_SECONDARY)",
                4: "Local Traffic Port Down (AGGR_FSM_RSN_LCL_TP_DOWN)",
                5: "Local AirLOS (AGGR_FSM_RSN_LCL_AIRLOS)",
                6: "Remote AirLOS (AGGR_FSM_RSN_REM_AIRLOS)",
                7: "Remote Down (AGGR_FSM_RSN_REM_DOWN)",
                8: "Remote Down Alternative OK (AGGR_FSM_RSN_REM_DOWN_ALT_OK)",
                9: "Alternative AirLOS (AGGR_FSM_RSN_ALT_AIRLOS)",
                10: "Alternative Broken (AGGR_FSM_RSN_ALT_BROKEN)",
                11: "Alternative Down (AGGR_FSM_RSN_ALT_DOWN)",
                12: "Alternative Traffic Port Down (AGGR_FSM_RSN_ALT_TP_DOWN)",
                13: "Alternative Active Secondary (AGGR_FSM_RSN_ALT_ACTIVE_SEC)",
                14: "Remote Alternative AirLOS (AGGR_FSM_RSN_REM_ALT_AIRLOS)",
                15: "Remote Alternative Broken (AGGR_FSM_RSN_REM_ALT_BROKEN)",
                16: "Remote Alternative Down (AGGR_FSM_RSN_REM_ALT_DOWN)",
                17: "Remote Alternative Active Secondary (AGGR_FSM_RSN_REM_ALT_ACTIVE_SEC)",
                18: "Remote Alternative Active Secondary with Alternative Broken (AGGR_FSM_RSN_REM_ALT_ACTIVE_SEC_ALT_BROKEN)",
                19: "Secondary Path Fail (AGGR_FSM_RSN_SECONDARY_PATH_FAIL)",
                20: "Alternative OK (AGGR_FSM_RSN_ALT_OK)",
                21: "Remote Up Sync OK (AGGR_FSM_RSN_REM_UP_SYNC_OK)",
                22: "Secondary Path OK (AGGR_FSM_RSN_SECONDARY_PATH_OK)"
            },
            "1+1HSB Protection": {
                0: "Configuration Commit (PROT_FSM_RSN_CFG_COMMIT)",
                1: "Enable (PROT_FSM_RSN_ENABLE)",
                2: "Configured as Primary (PROT_FSM_RSN_CFG_IS_PRIMARY)",
                3: "Configured as Secondary (PROT_FSM_RSN_CFG_IS_SECONDARY)",
                4: "Alternative Down (PROT_FSM_RSN_ALT_DOWN)",
                5: "Alternative TX Enable (PROT_FSM_RSN_ALT_TX_ENABLE)",
                6: "Alternative TX Secondary (PROT_FSM_RSN_ALT_TX_SECONDARY)",
                7: "Alternative TX Mute (PROT_FSM_RSN_ALT_TX_MUTE)",
                8: "Alternative Standby (PROT_FSM_RSN_ALT_STANDBY)",
                9: "Alternative Standby Broken (PROT_FSM_RSN_ALT_STANDBY_BROKEN)",
                10: "Alternative Force Standby (PROT_FSM_RSN_ALT_FORCESTANDBY)",
                11: "Alternative Sync Loss (PROT_FSM_RSN_ALT_SYNCLOSS)",
                12: "Alternative Traffic Port Down (PROT_FSM_RSN_ALT_TP_DOWN)",
                13: "Alternative Broken (PROT_FSM_RSN_ALT_BROKEN)",
                14: "Local TX Fail (PROT_FSM_RSN_LCL_TX_FAIL)",
                15: "Local TX/RX Fail (PROT_FSM_RSN_LCL_TXRX_FAIL)",
                16: "Local Sync Loss (PROT_FSM_RSN_LCL_SYNCLOSS)",
                17: "Local Traffic Port Down (PROT_FSM_RSN_LCL_TP_DOWN)",
                18: "Local Alternative Link Down (PROT_FSM_RSN_LCL_ALTLINK_DOWN)"
            }
        }
        self.create_widgets()

    def create_widgets(self):
        # Režima izvele
        mode_frame = tk.LabelFrame(self.root, text="Parsing Mode", padx=10, pady=5)
        mode_frame.pack(padx=10, pady=2, fill="x")
        self.mode_var = tk.StringVar(value="2+0 Aggregation")
        ttk.Radiobutton(mode_frame, text="2+0 Aggregation", variable=self.mode_var,
                       value="2+0 Aggregation").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="1+1HSB Protection", variable=self.mode_var,
                       value="1+1HSB Protection").pack(side=tk.LEFT, padx=5)

        # Mapes ievade
        for i in range(1, 5):
            frame = tk.LabelFrame(self.root, text=f"Ievadiet mapi un identifikatoru ({i})", padx=10, pady=5)
            frame.pack(padx=10, pady=2, fill="x")
            
            # Mapes cels
            dir_entry = tk.Entry(frame, width=40)
            dir_entry.pack(side=tk.LEFT, padx=5)
            tk.Button(frame, text="Pārlūkot...", command=lambda num=i: self.browse_directory(num)
                      ).pack(side=tk.LEFT)
            
            # ID ievade
            tk.Label(frame, text="ID:").pack(side=tk.LEFT, padx=5)
            id_entry = tk.Entry(frame, width=15)
            id_entry.pack(side=tk.LEFT)
            
            setattr(self, f"dir_entry{i}", dir_entry)
            setattr(self, f"id_entry{i}", id_entry)

        

        # Galvenas pogas
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Apstrādāt failus", command=self.process_files).pack(pady=2)
        tk.Button(control_frame, text="Notīrīt visu", command=self.clear_all).pack(pady=2)
        tk.Button(control_frame, text="Parādīt vizualizāciju", command=self.vizualize_all).pack(pady=2) #pievienoju pogu vizualizacijai

        # Rezultati
        self.result_frame = tk.LabelFrame(self.root, text="Rezultāti", padx=10, pady=10)
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
            getattr(self, f"dir_entry{dir_num}").delete(0, tk.END)
            getattr(self, f"dir_entry{dir_num}").insert(0, directory)
            self.directories[dir_num] = directory

    def clear_all(self):
        for i in range(1, 5):
            getattr(self, f"dir_entry{i}").delete(0, tk.END)
            getattr(self, f"id_entry{i}").delete(0, tk.END)
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
                    date_field, time_field, error_desc = parts[1].strip(), parts[2].strip(), parts[-1].strip() #sadal datus(laiks, datums, error(pedejais rinda))
                    if "Aggregation FSM state changed" in error_desc:
                        error_mapping[(date_field, time_field)] = error_desc
            except Exception as e:
                messagebox.showerror("Kļūda", f"Kļūda, lasot failu {error_file}: {str(e)}")
        return error_mapping

    def process_files(self):
        # Apstrada/parbauda ievadi(faailu)c
        selected_dirs = [d for d in self.directories.values() if d]
        if not selected_dirs:
            messagebox.showerror("Kļūda", "Lūdzu, atlasiet vismaz vienu mapi!")
            return

        # Parbauda id
        identifiers = {}
        for dir_num in self.directories:
            if self.directories[dir_num]:
                identifier = getattr(self, f"id_entry{dir_num}").get().strip()
                if not identifier:
                    messagebox.showerror("Kļūda", f"Lūdzu, ievadiet identifikatoru mapei {dir_num}!")
                    return
                identifiers[dir_num] = identifier

        self.result_text.delete(1.0, tk.END)
        total_files, success_count, skipped_count = 0, 0, 0
        merged_data = []
        existing_timestamps = set()

        for dir_num, directory in self.directories.items():
            if not directory:
                continue
            
            error_mapping = self.load_error_mapping(directory)
            current_identifier = identifiers[dir_num]
            mode = self.mode_var.get()

            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.json'):
                        total_files += 1
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            if 'time_stamp' not in data:
                                raise KeyError("Trūkst 'time_stamp' lauka")
                            
                            time_stamp = data["time_stamp"]
                            if time_stamp in existing_timestamps:
                                skipped_count += 1
                                continue
                            
                            # Ievada datus(aizpildit)
                            local_info = data.get("local", {}).get("info", {})
                            local_fsm_state = local_info.get("fsm_state", "")
                            local_traffic_port = local_info.get("traffic_port", "")
                            local_ports_up = local_info.get("ports_up", [])
                            
                            date_part, time_part = time_stamp.split(' ')
                            error_desc = error_mapping.get((date_part, time_part), "N/A")
                            
                            if error_desc == "N/A":
                                skipped_count += 1
                                continue
                            
                            # Darbojas ar error desc
                            error_desc = self.decode_error_description(error_desc, mode)
                            
                            merged_data.append({
                                "time_stamp": time_stamp,
                                "device_identifier": current_identifier,
                                "local_fsm_state": local_fsm_state,
                                "local_traffic_port": local_traffic_port,
                                "local_ports_up": local_ports_up,
                                "error_description": error_desc
                            })
                            
                            existing_timestamps.add(time_stamp)
                            success_count += 1
                        except Exception as e:
                            self.result_text.insert(tk.END, f"[Mape {dir_num}] {file} Kļūda: {str(e)}\n")
        
        merged_data.sort(key=lambda x: x["time_stamp"])
        merged_file_path = os.path.join(os.getcwd(), "merged_results.json")
        with open(merged_file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=4, ensure_ascii=False)

        summary = (
            f"\n=== REZULTĀTU KOPSUMMA ===\n"
            f"Kopējais JSON failu skaits: {total_files}\n"
            f"Izdevās saglabāt: {success_count}\n"
            f"Izlaisti: {skipped_count}\n"
            f"Apvienotais fails saglabāts: {merged_file_path}\n"
        )
        self.result_text.insert(tk.END, summary)
        messagebox.showinfo("Pabeigts", f"Apstrādāti {total_files} faili")

    def decode_error_description(self, error_desc, mode):
        # Aizvieto rsn id ar tā paskaidrojumu
        match = re.search(r'rsn_id:\((\d+)\)', error_desc)
        if match:
            rsn_id = int(match.group(1))
            reason = self.reason_ids.get(mode, {}).get(rsn_id, f"Unknown reason ({rsn_id})")
            error_desc = re.sub(r'rsn_id:\(\d+\)', reason, error_desc)
        return error_desc
    
    def vizualize_all(self):
        """Ģenerē SVG vizualizāciju un atver to pārlūkā"""
        merged_file = os.path.join(os.getcwd(), "merged_results.json")
        
        try:
            if not os.path.exists(merged_file):
                messagebox.showerror("Kļūda", "Nav atrasts apvienotais fails (merged_results.json)")
                return

            with open(merged_file, 'r', encoding='utf-8') as f:
                merged_data = json.load(f)

            if not merged_data:
                messagebox.showinfo("Info", "Nav datu vizualizācijai!")
                return

            # Izveido SVG nosaukumu un saturu
            svg_file = os.path.join(os.getcwd(), "network_visualization.svg")
            self.generate_state_diagram(merged_data, svg_file)
            
            # Atver SVG failu
            webbrowser.open(svg_file)
            messagebox.showinfo("Pabeigts", "Vizualizācija veiksmīgi ģenerēta un atvērta!")

        except Exception as e:
            messagebox.showerror("Kļūda", f"Vizualizācijas kļūda: {str(e)}")

    def generate_state_diagram(self, data, output_path):
        """Ģenerē SVG attēlu ar stāvokļu pārejām un paplašinātu informāciju par ierīces identifikatoru un trafika portu."""
        # Visi izmeri
        svg_width = 22000
        svg_height = 1800
        start_x = 150
        start_y = 100
        step_x = 600  #linijas garumam
        current_x = start_x
        current_y = start_y

        #kastes dimensions
        box_width = 250
        box_height = 140

        svg_content = [
            f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
            '<style>',
            '  .node { fill: #ffffff; stroke: #000000; stroke-width: 2; }',
            '  .label { font: 14px Arial; fill: #333333; }',
            '  .error { font: 6px Arial; fill: #cc0000; }',
            '  .arrow { marker-end: url(#arrowhead); stroke: #000000; stroke-width: 2; }',
            '</style>',
            '<defs>',
            '  <marker id="arrowhead" markerWidth="40" markerHeight="7" refX="9" refY="3.5" orient="auto">',
            '    <polygon points="0 0, 10 3.5, 0 7" fill="#000000"/>',
            '  </marker>',
            '</defs>'
        ]

        previous_state = None
        for idx, entry in enumerate(data):
            # savac datus no 
            state = entry.get('local_fsm_state', 'N/A')
            device = entry.get('device_identifier', 'N/A')
            ports = ', '.join(entry.get('local_ports_up', []))
            traffic = entry.get('local_traffic_port', 'N/A')
            time = entry.get('time_stamp', 'N/A')
            error = entry.get('error_description', '')

            # Erors viss kastes(ja ir, bet 100% butu jabut)
            if error:
                error_text_x = current_x + box_width / 2
                error_text_y = current_y - 10  # cik daudz virs kastes
                svg_content.append(
                    f'<text class="error" x="{error_text_x}" y="{error_text_y}" text-anchor="middle">{error}</text>'
                )

            # Izveido taisnsturi ar apaliem sturiem
            svg_content.append(
                f'<rect class="node" x="{current_x}" y="{current_y}" width="{box_width}" height="{box_height}" rx="5" ry="5"/>'
            )
            
            # kalkule pozicijas
            line_height = 20
            text_x = current_x + 10
            text_y = current_y + 20
            
            svg_content.append(f'<text class="label" x="{text_x}" y="{text_y}">{state}</text>')
            text_y += line_height
            svg_content.append(f'<text class="label" x="{text_x}" y="{text_y}">Device: {device}</text>')
            text_y += line_height
            svg_content.append(f'<text class="label" x="{text_x}" y="{text_y}">Ports: {ports}</text>')
            text_y += line_height
            svg_content.append(f'<text class="label" x="{text_x}" y="{text_y}">Traffic: {traffic}</text>')
            text_y += line_height
            svg_content.append(f'<text class="label" x="{text_x}" y="{text_y}">{time}</text>')

            # Ja izpildas, pievieno bultu starp kastem
            if previous_state is not None:
                arrow_start = previous_state['x'] + box_width
                arrow_y = previous_state['y'] + box_height / 2
                arrow_end = current_x
                svg_content.append(f'<path class="arrow" d="M {arrow_start} {arrow_y} L {arrow_end} {arrow_y}"/>')

            previous_state = {'x': current_x, 'y': current_y}
            current_x += step_x

            # ja svg grib īsāku un to padara mazāk platu izpildas nosacijums:
            if current_x + step_x > svg_width:
                current_x = start_x
                current_y += box_height + 60  #  papildus vertikala ataluma starp rindam

        svg_content.append('</svg>')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_content))


if __name__ == "__main__":
    root = tk.Tk()
    app = JSONTimeStampSaglabatajs(root)
    root.mainloop()