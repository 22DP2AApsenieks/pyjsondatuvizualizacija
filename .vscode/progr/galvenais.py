import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import glob
import re
import webbrowser
from datetime import datetime
from vizualization import JSONTimeStampVizualizetjas
import subprocess #lai atvertu vizualizac


class JSONTimeStampSaglabatajs:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Datu Saglabātājs un vizualizācijas veidotājs")
        self.directories = {1: None, 2: None, 3: None, 4: None}
        self.reason_ids = {
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
        self.box_indexes = []
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
            
            dir_entry = tk.Entry(frame, width=40)
            dir_entry.pack(side=tk.LEFT, padx=5)
            tk.Button(frame, text="Pārlūkot...", command=lambda num=i: self.browse_directory(num)
                      ).pack(side=tk.LEFT)
            
            tk.Label(frame, text="ID:").pack(side=tk.LEFT, padx=5)
            id_entry = tk.Entry(frame, width=15)
            id_entry.pack(side=tk.LEFT)
            
            setattr(self, f"dir_entry{i}", dir_entry)
            setattr(self, f"id_entry{i}", id_entry)



        def open_vizualizacija():
            # Use the full path to the file
            script_path = r"C:\Users\adams.apsenieks\OneDrive - SAF Tehnika AS\pyjsondatuvizualizacija\.vscode\progr\vizualization.py"
            subprocess.Popen(["python", script_path])

        # Galvenās pogas
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Apstrādāt failus", command=self.process_files).pack(pady=2)
        tk.Button(control_frame, text="Notīrīt visu", command=self.clear_all).pack(pady=2)
        tk.Button(control_frame, text="Parādīt vizualizāciju", command=open_vizualizacija).pack(pady=2) #atvers vizualizacijas failu
        """tk.Button(control_frame, text="Parādīt vizualizāciju", command=self.vizualize_all).pack(pady=2)"""
            #bez šita viss (sākuma stadija) smuki strada, šis visu boja
        # Rezultāti
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
                    date_field, time_field, error_desc = parts[1].strip(), parts[2].strip(), parts[-1].strip()
                    if "Aggregation FSM state changed" in error_desc:
                        error_mapping[(date_field, time_field)] = error_desc
            except Exception as e:
                messagebox.showerror("Kļūda", f"Kļūda, lasot failu {error_file}: {str(e)}")
        return error_mapping

    def process_files(self):
        selected_dirs = [d for d in self.directories.values() if d]
        if not selected_dirs:
            messagebox.showerror("Error", "Please select at least one directory!")
            return

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
                            
                            sections = {
                                'local': data.get('local', {}).get('info', {}),
                                'alternate': data.get('alternate', {}).get('info', {}),
                                'remote': data.get('remote', {}).get('info', {}),
                                'remote_alternate': data.get('remote.alternate', {}).get('info', {})
                            }
                            
                            date_part, time_part = time_stamp.split(' ')
                            error_desc = error_mapping.get((date_part, time_part), "N/A")
                            
                            if error_desc == "N/A":
                                skipped_count += 1
                                continue
                            
                            error_desc = self.decode_error_description(error_desc, mode)
                            
                            entry = {
                                "time_stamp": time_stamp,
                                "device_identifier": current_identifier,
                                "error_description": error_desc,
                                "sections": {}
                            }
                            
                            for section_name, section_data in sections.items():
                                if not section_data:
                                    continue
                                    
                                eth_ip = section_data.get("eth_ip", "N/A")
                                eth_ip_name = self.get_eth_ip_name(eth_ip)
                                
                                entry["sections"][section_name] = {
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
        
        merged_data.sort(key=lambda x: x["time_stamp"])
        merged_file_path = os.path.join(os.getcwd(), "merged_results.json")
        with open(merged_file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=4, ensure_ascii=False)


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
        if not eth_ip or eth_ip == "N/A":
            return "N/A"
        
        if isinstance(eth_ip, dict):
            eth_ip = eth_ip.get("ip", "N/A")
        
        try:
            last_octet = int(eth_ip.split('.')[-1])
        except (ValueError, AttributeError):
            return eth_ip
        
        role_mapping = {
            10: "l primary",
            11: "rem primary",
            12: "l secondary",
            13: "rem secondary"
        }
        
        return role_mapping.get(last_octet, eth_ip)

    def decode_error_description(self, error_desc, mode):
        match = re.search(r'rsn_id:\((\d+)\)', error_desc)
        if match:
            rsn_id = int(match.group(1))
            reason = self.reason_ids.get(mode, {}).get(rsn_id, f"Unknown reason ({rsn_id})")
            error_desc = re.sub(r'rsn_id:\(\d+\)', reason, error_desc)
        return error_desc

    
if __name__ == "__main__":
    root = tk.Tk()
    app = JSONTimeStampSaglabatajs(root)
    root.mainloop()

