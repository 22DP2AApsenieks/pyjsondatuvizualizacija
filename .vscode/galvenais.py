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

        # Galvenas pogas
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Apstrādāt failus", command=self.process_files).pack(pady=2)
        tk.Button(control_frame, text="Notīrīt visu", command=self.clear_all).pack(pady=2)
        tk.Button(control_frame, text="Parādīt vizualizāciju", command=self.vizualize_all).pack(pady=2)

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

    def vizualize_all(self):
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

            self.visualization_window = tk.Toplevel(self.root)
            self.visualization_window.title("Visualization")
            
            self.current_index = 0
            self.visualization_limit = 1
            self.visualization_data = merged_data

            self.next_button = tk.Button(self.visualization_window, text="Next ", command=self.next_visualizations)
            self.next_button.pack(pady=10)

            self.iepriekseja_button = tk.Button(self.visualization_window, text="Back ", command=self.previous_visualizations)
            self.iepriekseja_button.pack(pady=10)

            self.show_visualizations()

        except Exception as e:
            messagebox.showerror("Kļūda", f"Vizualizācijas kļūda: {str(e)}")

    def show_visualizations(self):
        start = self.current_index
        end = min(self.current_index + self.visualization_limit, len(self.visualization_data))
        current_data = self.visualization_data[start:end]
        
        print(f"Current data to visualize: {current_data}")

        if not current_data:
            messagebox.showinfo("Info", "Nav vairāk datu!")
            return

        output_path = os.path.join(os.getcwd(), "current_visualization.svg")
        self.generate_state_diagram(current_data, output_path)

        webbrowser.open(output_path)

        if hasattr(self, 'next_button'):
            self.update_next_button_state()

        if hasattr(self, 'iepriekseja_button'):
            self.back_button_state()

    def next_visualizations(self):
        self.current_index += self.visualization_limit
        if self.current_index >= len(self.visualization_data):
            self.current_index = 0  
        self.show_visualizations()

    def previous_visualizations(self):
        self.current_index -= self.visualization_limit
        if self.current_index < 0:
            self.current_index = max(0, len(self.visualization_data) - self.visualization_limit)
        self.show_visualizations()

    def update_next_button_state(self): 
        next_index = self.current_index + self.visualization_limit
        if next_index < len(self.visualization_data):
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    def back_button_state(self):
        next_index = self.current_index + self.visualization_limit
        if next_index < len(self.visualization_data):
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    def determine_senders_and_receivers(self):
        """
        Determine which boxes can send data and which 'r' sections can receive.
        Returns two lists: senders and receivers with their box indexes.
        If both local sections can send, prefer the main local (0) over alternative (2).
        """
        senders = []
        receivers = []
        
        
        # States that can send or receive data
        can_send_states = {1, 2, 3, 5, 7, 8, 10, 11, 12}
        can_receive_states = {1, 2, 3, 5, 8, 11, 10, 12}
        
        for box in self.box_indexes:
            state_index = box['state']
            section_name = box['name']
            section_index = box['section']
            
            # Senders: only if name doesn't start with 'r'
            if not section_name.startswith('r') and state_index in can_send_states:
                senders.append(section_index)
            
            # Receivers: only if name starts with 'r'
            if section_name.startswith('r') and state_index in can_receive_states:
                receivers.append(section_index)

        # Apply rule: prefer local (0) over alternative (2)
        if 0 in senders and 2 in senders:
            senders.remove(2)

        return senders, receivers

    
    def draw_sender_receiver_lines(self):
        """Draw lines from senders to receivers based on state rules"""
        line_elements = []
        
        # Get senders and receivers
        senders, receivers = self.determine_senders_and_receivers()
        
        # Get positions of all boxes
        box_positions = {}
        for box in self.box_indexes:
            if box['timestamp'] not in box_positions:
                box_positions[box['timestamp']] = {}
            center_x = box['x'] + box['width'] / 2
            center_y = box['y'] + box['height'] / 2
            box_positions[box['timestamp']][box['section']] = (center_x, center_y)
        
        # Draw lines from each sender to each receiver
        for timestamp, sections in box_positions.items():
            for sender_idx in senders:
                if sender_idx in sections:
                    sender_x, sender_y = sections[sender_idx]
                    for receiver_idx in receivers:
                        if receiver_idx in sections and receiver_idx != sender_idx:
                            receiver_x, receiver_y = sections[receiver_idx]
                            line_elements.append(
                                f'<line x1="{sender_x}" y1="{sender_y}" x2="{receiver_x}" y2="{receiver_y}" '
                                f'class="sender-receiver-line" marker-end="url(#arrowhead)"/>'
                            )
        
        return line_elements
    def determine_recivers_and_senders(self):
        """
        Determine which boxes can send data and which 'r' sections can receive.
        Returns two lists: senders and receivers with their box indexes.
        If both local sections can send, prefer the main local (0) over alternative (2).
        """
        senders1 = []
        receivers1 = []
        

        # States that can send or receive data
        can_recive1_states = {2, 3, 5, 6, 8, 10, 12}
        can_send1_states = {1, 2, 10, 12}
        
        for box in self.box_indexes:
            state_index = box['state']
            section_name = box['name']
            section_index = box['section']
            
            # Senders: only if name doesn't start with 'r'
            if not section_name.startswith('r') and state_index in can_send1_states:
                senders1.append(section_index)
            
            # Receivers: only if name starts with 'r'
            if section_name.startswith('r') and state_index in can_recive1_states:
                receivers1.append(section_index)

        

        # Apply rule: prefer local (0) over alternative (2)
        if 1 in receivers1 and 3 in receivers1:
            receivers1.remove(3)

        if 0 in senders1 and 2 in senders1:
            senders1.remove(2)

        return receivers1, senders1
    
    def draw_recive_sender_lines(self):
        """Draw lines from reci to loc based on state rules"""
        line_elements1 = []
        
        # Get senders and receivers
        recivers1, senders1 = self.determine_recivers_and_senders()
        
        # Get positions of all boxes
        box_positions = {}
        for box in self.box_indexes:
            if box['timestamp'] not in box_positions:
                box_positions[box['timestamp']] = {}
            center_x = box['x'] + box['width'] / 2
            center_y = box['y'] + box['height'] / 2
            box_positions[box['timestamp']][box['section']] = (center_x, center_y)
        
        # Draw lines from receiver (remote) to sender (local)
        for timestamp, sections in box_positions.items():
            for sender_idx in senders1:
                if sender_idx in sections:
                    sender_x, sender_y = sections[sender_idx]
                    for receiver_idx in recivers1:
                        if receiver_idx in sections and receiver_idx != sender_idx:
                            receiver_x, receiver_y = sections[receiver_idx]
                            #  Reversed direction: from receiver → sender
                            line_elements1.append(
                                f'<line x1="{receiver_x}" y1="{receiver_y}" x2="{sender_x}" y2="{sender_y}" '
                                f'class="recive-sender-line" marker-end="url(#arrowhead)"/>'
                            )
        
        return line_elements1


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

        # SVG content with line styles
        svg_content = [
            f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">',
            '<style>',
            '  .node { fill: #ffffff; stroke: #000000; stroke-width: 2; }',
            '  .label { font: 10px Arial; fill: #333333; }',
            '  .labela { font: 6px Arial; fill: #333333; font-weight: bold;}',
            '  .error { font: 9px Arial; fill: #cc0000; }',
            '  .timestamp { font: 20px Arial; font-weight: bold; fill: #0000cc; }',
            '  .section-label { font: 15px Arial; font-weight: bold; fill: #0000cc; }',
            '  .box-index { font: 12px Arial; font-weight: bold; fill: #000000; }',
            '  .connection-line { stroke: #888888; stroke-width: 2; }',
            '  .diagonal-line { stroke: #aa0000; stroke-width: 3; }',
            '  .sender-receiver-line { stroke: #00aa00; stroke-width: 2; stroke-dasharray: 5,5; }'
            '  .recive-sender-line { stroke: #aa00aa; stroke-width: 2; }'   # Purple for receiver→sender
            '</style>',
            '<defs>',
            '  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">',
            '    <polygon points="0 0, 10 3.5, 0 7" fill="#888888"/>',
            '  </marker>',
            '</defs>'
        ]

        # Clear previous box indexes
        self.box_indexes = []

        # Sakarto datus pec timestamp
        sorted_data = sorted(data, key=lambda x: x.get('time_stamp', 'N/A'))

        for entry_idx, entry in enumerate(sorted_data):
            time_stamp = entry.get('time_stamp', 'N/A')
            error_desc = entry.get('error_description', 'N/A')
            
            # pievienop timestamp un error
            svg_content.append(f'<text class="timestamp" x="{current_x}" y="{current_y - 10}">Timestamp: {time_stamp}</text>')
            svg_content.append(f'<text class="error" x="{current_x}" y="{current_y}">Description: {error_desc}</text>')

            # paskaidro kadu secibu velos
            section_order = ['local', 'remote', 'alternate', 'remote_alternate']
            sections = entry.get('sections', {})

            for section_idx, section_name in enumerate(section_order):
                if section_name not in sections:
                    continue  
                    
                section_data = sections[section_name]
                
                # Pievieno kasti ar indeksu
                svg_content.append(
                    f'<rect class="node" x="{current_x}" y="{current_y + 30}" '
                    f'width="{box_width}" height="{box_height}" rx="5" ry="5" '
                    f'data-entry="{entry_idx}" data-section="{section_idx}">'
                    f'<title>Entry {entry_idx} - Box {section_idx} ({section_name})</title></rect>'
                )

                # Pievieno virsrakstu kASTEI ar indeksu
                svg_content.append(f'<text class="section-label" x="{current_x + 10}" y="{current_y + 60}">{section_name.upper()}</text>')
                svg_content.append(f'<text class="box-index" x="{current_x + box_width - 30}" y="{current_y + 60}">[{section_idx}]</text>')

                text_statement = f'State: {section_data.get("fsm_state", "N/A")}' 
                
                # Determine state index
                state_index = None
                if "Prim.Tx-WAN Rx-ALT" in text_statement:
                    state_index = 1
                elif "Prim.Tx-WAN Rx-WAN" in text_statement:
                    state_index = 2
                elif "primary_tx-alt_rx-wan" in text_statement:
                    state_index = 3
                elif "Primary Mute" in text_statement:
                    state_index = 4
                elif "Prim.Tx-ALT Rx-ALT" in text_statement:
                    state_index = 5
                elif "Secondary Mute" in text_statement:
                    state_index = 6
                elif "Secondary Active" in text_statement:  
                    state_index = 7
                elif "Secondary Protect" in text_statement:
                    state_index = 8
                elif "Start" in text_statement:
                    state_index = 9
                elif "Primary Standby" in text_statement:
                    state_index = 10
                elif "Secondary Protect" in text_statement:
                    state_index = 11
                elif "Secondary Standby" in text_statement:
                    state_index = 12

                # Saglabā indeksus
                self.box_indexes.append({
                    'entry': entry_idx,
                    'section': section_idx,
                    'name': section_name,
                    'x': current_x,
                    'y': current_y + 30,
                    'width': box_width,
                    'height': box_height,
                    'timestamp': time_stamp,
                    'state': state_index  # Store the state index
                })

                state_descriptions = {
                    1: "device active. Var sūtīt, bet uzņem tikai caur sekundāro.",
                    2: "device active. Var visu.",
                    3: "device active. Var saņemt no remote. nevars sanemt no alternative, bet var sutit altern.",
                    4: "device not active and muted. Traffic is neither transmitted over any paths, nor received. Secondary device should be active.",
                    5: "device active. Nevar uzņemt no remote ",
                    6: "device not active and muted. Saņemtais trafiks var tikt nodots primārajam. Primārā izvēlas vai pieņemt vai nē",
                    7: "device not active. dati tiek nosūtīti un saņemti caur outru",
                    8: "device active. Dati tike saņemt un parsutiti tikai caur sekundaro",
                    9: "lkm sāk(nebija minets dokomenta)",
                    10:"Visuvar?",
                    11:"Viss trafiks iet caur sekundaro",
                    12: "Visuvar?",
                }

                if state_index is not None:
                    state_value = state_descriptions[state_index]
                else:
                    state_value = text_statement

                svg_content.append(f'<text class="labela" x="{current_x + 10}" y="{current_y + 90}">{state_value}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 120}">Role: {section_data.get("role_state", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 150}">Config: {section_data.get("role_cfg", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 180}">TX: {section_data.get("tx_state", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 210}">RX: {section_data.get("rx_state", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 240}">Eth IP: {section_data.get("eth_ip", "N/A")}</text>')

                ports = ["LAN1", "LAN2", "LAN3", "WAN"]
                for i, port in enumerate(ports):
                    color = "#70ff70" if port in section_data.get("ports_up", []) else "#ff7070"
                    if port == section_data.get("traffic_port", ""): 
                        color = "purple"
                    
                    svg_content.append(f'<rect x="{current_x + 10 + (i * 100)}" y="{current_y + 270}" width="90" height="20" fill="{color}" stroke="black" stroke-width="0.5"/>')
                    svg_content.append(f'<text class="label" x="{current_x + 15 + (i * 100)}" y="{current_y + 285}">{port}</text>')

                current_x += box_width + 50
                if current_x + box_width > svg_width:
                    current_x = start_x
                    current_y += box_height + 100

        # Add the sender-receiver lines after all boxes are created
        svg_content.extend(self.draw_sender_receiver_lines())
        svg_content.extend(self.draw_recive_sender_lines())
        svg_content.append('</svg>')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_content))
        

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONTimeStampSaglabatajs(root)
    root.mainloop()