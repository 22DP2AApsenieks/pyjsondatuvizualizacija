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
        # Režīma izvēle
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
        """Process JSON files, extract data including eth_ip, and save merged results."""
        # Validate directories
        selected_dirs = [d for d in self.directories.values() if d]
        if not selected_dirs:
            messagebox.showerror("Error", "Please select at least one directory!")
            return

        # Validate identifiers
        identifiers = {}
        for dir_num in self.directories:
            if self.directories[dir_num]:
                identifier = getattr(self, f"id_entry{dir_num}").get().strip()
                if not identifier:
                    messagebox.showerror("Error", f"Please enter an identifier for directory {dir_num}!")
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
                                raise KeyError("Missing 'time_stamp' field")
                            
                            time_stamp = data["time_stamp"]
                            if time_stamp in existing_timestamps:
                                skipped_count += 1
                                continue
                            
                            # Extract data from all sections
                            sections = {
                                'local': data.get('local', {}).get('info', {}),
                                'alternate': data.get('alternate', {}).get('info', {}),
                                'remote': data.get('remote', {}).get('info', {}),
                                'remote_alternate': data.get('remote.alternate', {}).get('info', {})
                            }
                            
                            # parbauda error desc
                            date_part, time_part = time_stamp.split(' ')
                            error_desc = error_mapping.get((date_part, time_part), "N/A")
                            
                            if error_desc == "N/A":
                                skipped_count += 1
                                continue
                            
                            error_desc = self.decode_error_description(error_desc, mode)
                            
                            # izveido entry
                            entry = {
                                "time_stamp": time_stamp,
                                "device_identifier": current_identifier,
                                "error_description": error_desc,
                                "sections": {}
                            }
                            
                            # Add data for each section
                            for section_name, section_data in sections.items():
                                if not section_data:
                                    continue
                                    
                                eth_ip = section_data.get("eth_ip", "N/A")
                                eth_ip_name = self.get_eth_ip_name(eth_ip)
                                
                                entry["sections"][section_name] = {  #te var izveletos, ko rakstis iekas
                                    "fsm_state": section_data.get("fsm_state", "N/A"),
                                    "role_state": section_data.get("role_state", "N/A"),
                                    "role_cfg": section_data.get("role_cfg", "N/A"),
                                    "tx_state": section_data.get("tx_state", "N/A"),
                                    "rx_state": section_data.get("rx_state", "N/A"),
                                    "traffic_port": section_data.get("traffic_port", "N/A"),
                                    "alt_port": section_data.get("alt_port", "N/A"),
                                    "ports_up": section_data.get("ports_up", []),
                                    "eth_ip": eth_ip,
                                    "eth_ip_name": eth_ip_name,
                                }
                            
                            merged_data.append(entry)
                            existing_timestamps.add(time_stamp)
                            success_count += 1
                        except Exception as e:
                            self.result_text.insert(tk.END, f"[Directory {dir_num}] {file} Error: {str(e)}\n")
        
        # Sort and save results
        merged_data.sort(key=lambda x: x["time_stamp"])
        merged_file_path = os.path.join(os.getcwd(), "merged_results.json")
        with open(merged_file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=4, ensure_ascii=False)

        # Display summary
        summary = (
            f"\n=== SUMMARY ===\n"
            f"Total JSON files processed: {total_files}\n"
            f"Successfully saved: {success_count}\n"
            f"Skipped: {skipped_count}\n"
            f"Merged file saved at: {merged_file_path}\n"
        )
        self.result_text.insert(tk.END, summary)
        messagebox.showinfo("Complete", f"Processed {total_files} files")

    def get_eth_ip_name(self, eth_ip):
        """Determine device role based on the last octet of the IP address."""
        if not eth_ip or eth_ip == "N/A":
            return "N/A"
        
        # Handle cases where eth_ip might be in a dictionary
        if isinstance(eth_ip, dict):
            eth_ip = eth_ip.get("ip", "N/A")
        
        # Extract last octet
        try:
            last_octet = int(eth_ip.split('.')[-1])
        except (ValueError, AttributeError):
            return eth_ip  # Return original if not a valid IP
        
        # Map last octet to role names
        role_mapping = {
            10: "l primary",
            11: "rem primary",
            12: "l secondary",
            13: "rem secondary"
        }
        
        return role_mapping.get(last_octet, eth_ip)  # Return role name or original IP

    def decode_error_description(self, error_desc, mode):
        # Aizvieto rsn id ar tā paskaidrojumu
        match = re.search(r'rsn_id:\((\d+)\)', error_desc)
        if match:
            rsn_id = int(match.group(1))
            reason = self.reason_ids.get(mode, {}).get(rsn_id, f"Unknown reason ({rsn_id})")
            error_desc = re.sub(r'rsn_id:\(\d+\)', reason, error_desc)
        return error_desc
    

      
    def vizualize_all(self):
        """Generate SVG visualization and open it in a browser."""
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

            # uztaisa jaunu logu vizualizacijam
            self.visualization_window = tk.Toplevel(self.root)
            self.visualization_window.title("Visualization")
            
            self.current_index = 0
            self.visualization_limit = 1  # cik vizualizacijas radis
            self.visualization_data = merged_data

            # POGA, kas ļaus apskatit nakamos 4
            self.next_button = tk.Button(self.visualization_window, text="Next ", command=self.next_visualizations)
            self.next_button.pack(pady=10)

            #poga iešanai atpaskaļ
            self.iepriekseja_button = tk.Button(self.visualization_window, text="Back ", command=self.previous_visualizations)
            self.iepriekseja_button.pack(pady=10)

            self.show_visualizations()

        except Exception as e:
            messagebox.showerror("Kļūda", f"Vizualizācijas kļūda: {str(e)}")

    

    def show_visualizations(self):
        """Display the current set of visualizations."""
        # dabuj datus
        current_data = self.visualization_data[self.current_index:self.current_index + self.visualization_limit]
        
        print(f"Current data to visualize: {current_data}")  # erroriem

        if not current_data:
            messagebox.showinfo("Info", "Nav vairāk datu!")
            return

        # genere svg
        output_path = os.path.join(os.getcwd(), "current_visualization.svg")
        self.generate_state_diagram(current_data, output_path)

        webbrowser.open(output_path)#atver

        if hasattr(self, 'next_button'):
            self.update_next_button_state()

        if hasattr(self, 'iepriekseja_button'):
            self.back_button_state()


    def next_visualizations(self):
        """Navigate to the next set of visualizations."""
        self.current_index += self.visualization_limit
        if self.current_index >= len(self.visualization_data):
            self.current_index = 0  
        self.show_visualizations()

    def previous_visualizations(self):
        """Navigate to the previous set of visualizations."""
        self.current_index -= self.visualization_limit
        if self.current_index < 0:
            self.current_index = max(0, len(self.visualization_data) - self.visualization_limit)
        self.show_visualizations()


    def update_next_button_state(self): 
        """Update the state of the next button based on remaining data."""
        next_index = self.current_index + self.visualization_limit
        if next_index < len(self.visualization_data):
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    def back_button_state(self): #back visualaiku strada. Man slinkums sobrid to labot tho
        """Update the state of the next button based on remaining data."""
        next_index = self.current_index + self.visualization_limit
        if next_index < len(self.visualization_data):
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)


    def generate_state_diagram(self, data, output_path):
        """Generate SVG image with state transitions and detailed information."""
        svg_width = 1200
        svg_height = 800
        start_x = 50
        start_y = 50
        box_width = 500
        box_height = 300
        current_x = start_x
        current_y = start_y

        # SVG content izskatam
        svg_content = [
            f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
            '<style>',
            '  .node { fill: #ffffff; stroke: #000000; stroke-width: 2; }',
            '  .label { font: 10px Arial; fill: #333333; }',
            '  .error { font: 9px Arial; fill: #cc0000; }',
            '  .timestamp { font: 20px Arial; font-weight: bold; fill: #0000cc; }',
            '  .section-label { font: 15px Arial; font-weight: bold; fill: #0000cc; }',
            '</style>'
        ]

        # Sakarto datus pec timestamp
        sorted_data = sorted(data, key=lambda x: x.get('time_stamp', 'N/A'))

        for entry in sorted_data:
            time_stamp = entry.get('time_stamp', 'N/A')
            error_desc = entry.get('error_description', 'N/A')
            
            # pievienop timestamp un error
            svg_content.append(f'<text class="timestamp" x="{current_x}" y="{current_y - 10}">Timestamp: {time_stamp}</text>')
            svg_content.append(f'<text class="error" x="{current_x}" y="{current_y}">Description: {error_desc}</text>')

            # paskaidro kadu secibu velos
            section_order = ['local', 'remote', 'alternate', 'remote_alternate']
            sections = entry.get('sections', {})
            

            for section_name in section_order:
                if section_name not in sections:
                    continue  
                    
                section_data = sections[section_name]
                
                # Pievieno kasti 
                svg_content.append(
                    f'<rect class="node" x="{current_x}" y="{current_y + 30}" width="{box_width}" height="{box_height}" rx="5" ry="5"/>'
                )

                # Pievieno virsrakstu kASTEI
                svg_content.append(f'<text class="section-label" x="{current_x + 10}" y="{current_y + 60}">{section_name.upper()}</text>')
                
                # Pievieno laukus ieksa kvadrata
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 90}">State: {section_data.get("fsm_state", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 120}">Role: {section_data.get("role_state", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 150}">Config: {section_data.get("role_cfg", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 180}">TX: {section_data.get("tx_state", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 210}">RX: {section_data.get("rx_state", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 240}">Eth IP: {section_data.get("eth_ip", "N/A")}</text>')

                # porta statusa paradisana
                ports = ["LAN1", "LAN2", "LAN3", "WAN"]
                for i, port in enumerate(ports):
                    # parbauda vai ports ir up, ja ir tad ir zals
                    color = "#70ff70" if port in section_data.get("ports_up", []) else "#ff7070"
                    
                    # parmaina krasu, tikai ja redz traf port (purple)
                    if port == section_data.get("traffic_port", ""): 
                        color = "purple"
                    
                    svg_content.append(f'<rect x="{current_x + 10 + (i * 100)}" y="{current_y + 270}" width="90" height="20" fill="{color}" stroke="black" stroke-width="0.5"/>')
                    svg_content.append(f'<text class="label" x="{current_x + 15 + (i * 100)}" y="{current_y + 285}">{port}</text>')

                # Parvieto poziciju
                current_x += box_width + 50
                if current_x + box_width > svg_width:
                    current_x = start_x
                    current_y += box_height + 100

        svg_content.append('</svg>')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_content))

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONTimeStampSaglabatajs(root)
    root.mainloop()