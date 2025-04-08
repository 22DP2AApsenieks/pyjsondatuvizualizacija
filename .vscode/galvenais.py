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

    def get_wan_positions(self):
        """Returns a dictionary mapping timestamps and sections to their WAN port center positions"""
        wan_positions = {}
        
        for box in self.box_indexes:
            if box['timestamp'] not in wan_positions:
                wan_positions[box['timestamp']] = {}
            
            # Calculate WAN position based on whether it's local or remote
            if not box['name'].startswith('r'):  # Local - WAN is last (right side)
                wan_x = box['x'] + box['width'] - 50  # Right side minus half of port width
            else:  # Remote - WAN is first (left side)
                wan_x = box['x'] + 50  # Left side plus half of port width
                
            wan_y = box['y'] + box['height'] - 40  # Y position of ports area
            
            wan_positions[box['timestamp']][box['section']] = (wan_x, wan_y)
        
        return wan_positions

    def determine_senders_and_receivers(self):
        """
        Determine which boxes can send data and which 'r' sections can receive.
        Returns two lists: senders and receivers with their box indexes.
        If both local sections can send, prefer the main local (0) over alternative (2).
        """

        senders = []
        receivers = []

        # Define valid states for each category
        local_send_states = {1, 2, 3, 5, 10, 12}
        local_alt_send_states = {1, 2, 3, 7, 8, 10, 11, 12}
        remote_recv_states = {2, 3, 10, 5, 12}
        remote_alt_recv_states = {1, 2, 6, 8, 10, 11, 12}  

        for box in self.box_indexes:
            state = box['state']
            name = box['name']
            section = box['section']

            if not name.startswith('r'):
                # Local sender
                if section == 0 and state in local_send_states:
                    senders.append(section)
                elif section == 2 and state in local_alt_send_states:
                    senders.append(section)
            else:
                # Remote receiver
                if section == 1 and state in remote_recv_states:
                    receivers.append(section)
                elif section == 3 and state in remote_alt_recv_states:
                    receivers.append(section)

        # Prefer section 0 over 2
        if 0 in senders and 2 in senders:
            senders.remove(2)

        if 1 in receivers and 3 in receivers:
            receivers.remove(3)

        return senders, receivers

    def determine_recivers_and_senders(self):
        """
        Determine which boxes can receive data (local sections) and which 'r' sections can send.
        Returns two lists: local_receivers and remote_senders with their box indexes.
        Prefer the main local (0) over alternative (2).
        """
        local_receivers = []
        remote_senders = []

        # Define valid states for each category
        local_receive_states = {1, 2, 3, 6, 10, 12}
        local_alt_receive_states = {1, 2, 3, 6, 7, 8, 10, 11, 12}
        remote_send_states = {1, 2, 3, 7, 8, 10, 12}
        remote_alt_send_states = {1, 2, 6, 7, 8, 10, 12}

        for box in self.box_indexes:
            state = box['state']
            name = box['name']
            section = box['section']

            if not name.startswith('r'):
                # Local receiver
                if section == 0 and state in local_receive_states:
                    local_receivers.append(section)
                elif section == 2 and state in local_alt_receive_states:
                    local_receivers.append(section)
            else:
                # Remote sender
                if section == 1 and state in remote_send_states:
                    remote_senders.append(section)
                elif section == 3 and state in remote_alt_send_states:
                    remote_senders.append(section)

        # Prefer section 0 over 2
        if 0 in local_receivers and 2 in local_receivers:
            local_receivers.remove(2)

        if 1 in remote_senders and 3 in remote_senders:
            remote_senders.remove(3)

        return local_receivers, remote_senders

    def draw_sender_receiver_lines(self):
        """Draw lines from senders to receivers based on state rules, connecting WAN ports"""
        line_elements = []
        
        # Get senders and receivers
        senders, receivers = self.determine_senders_and_receivers()
        
        # Get WAN positions of all boxes
        wan_positions = self.get_wan_positions()
        
        # Draw lines from each sender to each receiver
        for timestamp, sections in wan_positions.items():
            for sender_idx in senders:
                if sender_idx in sections:
                    sender_x, sender_y = sections[sender_idx]
                    for receiver_idx in receivers:
                        if receiver_idx in sections and receiver_idx != sender_idx:
                            receiver_x, receiver_y = sections[receiver_idx]
                            line_elements.append(
                                f'<line x1="{sender_x}" y1="{sender_y}" x2="{receiver_x}" y2="{receiver_y}" '
                                f'class="sender-receiver-line" marker-end="url(#arrowhead)">'
                               # '<animate attributeName="stroke-opacity" values="0;1;0" dur="2s" repeatCount="indefinite"/>'
                                #'<animate attributeName="stroke-width" values="1;3;1" dur="2s" repeatCount="indefinite"/>'
                                '</line>'
                            )
        
        return line_elements

    def draw_recive_sender_lines(self):
        """Draw lines from remote senders to local receivers, connecting WAN ports"""
        line_elements = []

        receivers, senders = self.determine_recivers_and_senders()

        # Get WAN positions of all boxes
        wan_positions = self.get_wan_positions()

        # Draw lines from sender (remote) → receiver (local)
        for timestamp, sections in wan_positions.items():
            for sender_idx in senders:
                if sender_idx in sections:
                    sender_x, sender_y = sections[sender_idx]
                    for receiver_idx in receivers:
                        if receiver_idx in sections and receiver_idx != sender_idx:
                            receiver_x, receiver_y = sections[receiver_idx]
                            line_elements.append(
                                f'<line x1="{sender_x}" y1="{sender_y}" x2="{receiver_x}" y2="{receiver_y}" '
                                f'class="recive-sender-line" marker-end="url(#arrowhead)">'
                                '</line>'
                            )

        return line_elements
    
    def get_traffic_port_position(self, box):
        """Get center coordinates of traffic port for given box"""
        entry_idx = box['entry']
        section_name = box['name']
        section_data = self.visualization_data[entry_idx]['sections'].get(section_name, {})
        traffic_port = section_data.get('traffic_port', 'N/A')

        # Determine port order based on section type
        if section_name.startswith('remote'):
            port_order = ["WAN", "LAN1", "LAN2", "LAN3"]
        else:
            port_order = ["LAN1", "LAN2", "LAN3", "WAN"]

        try:
            port_index = port_order.index(traffic_port)
        except ValueError:
            return None

        # Calculate port center coordinates
        x = box['x'] + 160 + (port_index * 35) + 45
        y = box['y'] + 240 + 10  # 240 from box top, 10 from port top

        return (x, y)
    


    def socondarytoprimarry(self):
        """Draw lines from secondary to primary, connecting Traffic ports."""
        line_elements = []  # Initialize the list to collect all line elements

        # Loop through each unique 'entry' in self.box_indexes (set to eliminate duplicates)
        for entry in set(box['entry'] for box in self.box_indexes):
            local_box = None
            alternate_box = None

            # Find 'local' and 'alternate' boxes for the current entry
            for box in self.box_indexes:
                if box['entry'] == entry:
                    if box['name'] == 'local':
                        local_box = box
                    elif box['name'] == 'alternate':
                        alternate_box = box

            # Get the role configs for 'local' and 'alternate'
            local_role = self.visualization_data[entry]['sections'].get('local', {}).get("role_cfg", "N/A").lower()
            alternate_role = self.visualization_data[entry]['sections'].get('alternate', {}).get("role_cfg", "N/A").lower()

            # Role resolution to determine primary and secondary boxes
            primary_box = None
            secondary_box = None

            if local_role == 'primary' and alternate_role == 'secondary':
                primary_box = local_box
                secondary_box = alternate_box
            elif local_role == 'secondary' and alternate_role == 'primary':
                primary_box = alternate_box
                secondary_box = local_box
            elif local_role == 'secondary' and alternate_role != 'primary':
                secondary_box = local_box
                raise ValueError(f"Entry '{entry}' has a secondary box but no valid primary.")
            elif alternate_role == 'secondary' and local_role != 'primary':
                secondary_box = alternate_box
                raise ValueError(f"Entry '{entry}' has a secondary box but no valid primary.")
            else:
                raise ValueError(f"Entry '{entry}' must have one primary and one secondary. Got roles: local={local_role}, alternate={alternate_role}")

            # Get positions for the primary and secondary boxes
            secondary_pos = self.get_traffic_port_position(secondary_box)
            primary_pos = self.get_traffic_port_position(primary_box)

            # Ensure both positions are valid and then create the line element as a string
            if secondary_pos and primary_pos:
                line_elements.append(
                    f'<line x1="{secondary_pos[0]}" y1="{secondary_pos[1]}" x2="{primary_pos[0]}" y2="{primary_pos[1]}" '
                    'class="secondary-primary-line" marker-end="url(#arrowhead)"/>'
                )

        # Ensure all lines are processed
        print(f"Total lines generated: {len(line_elements)}")  # Debugging the number of lines
        print(line_elements)  # Print all generated lines for verification

        # Write the generated lines to a JSON file after the loop completes
        with open("line_elements_output.json", "w") as json_file:
            json.dump(line_elements, json_file, indent=4)

        return line_elements



    # Example function to analyze JSON data and print primary and secondary info
    def analyze_json_files(json_data):
        result = []

        # Function to get the role status based on role_cfg
        def get_role_status(role_cfg):
            if role_cfg == "primary":
                return "primary"
            elif role_cfg == "secondary":
                return "secondary"
            else:
                return "unknown"

        # Process each JSON entry based on timestamps
        for entry in json_data:
            time_stamp = entry.get("time_stamp")
            sections = entry.get("sections", {})

            # Get the role_cfg for 'local' and 'alternate'
            local_role = get_role_status(sections.get("local", {}).get("role_cfg"))
            alternate_role = get_role_status(sections.get("alternate", {}).get("role_cfg"))

            # Determine primary and secondary roles
            if local_role == "primary" and alternate_role == "secondary":
                primary = "local"
                secondary = "alternate"
            elif local_role == "secondary" and alternate_role == "primary":
                primary = "alternate"
                secondary = "local"
            else:
                primary = "unknown"
                secondary = "unknown"

            # Store result with timestamp and roles
            result.append({
                "time_stamp": time_stamp,
                "primary": primary,
                "secondary": secondary
            })

            # Display primary and secondary names (if available)
            print(f"Entry '{entry}' - Primary: {primary}, Secondary: {secondary}")

        return result


    # Example: Reading and processing JSON
    with open("merged_results.json", "r") as file:
        json_data = json.load(file)

    # Analyze and print the results
    output = analyze_json_files(json_data)
    for item in output:
        print(f"Timestamp: {item['time_stamp']} - Primary: {item['primary']} - Secondary: {item['secondary']}")
        
        
    def remote_to_remote_alternate(self):
        """Draw lines from remote to remote_alternate, connecting Traffic ports"""
        line_elements = []
        # Find all remote and remote_alternate sections
        for entry in set(box['entry'] for box in self.box_indexes):
            remote_box = None
            remote_alternate_box = None
            for box in self.box_indexes:
                if box['entry'] == entry:
                    if box['name'] == 'remote':
                        remote_box = box
                    elif box['name'] == 'remote_alternate':
                        remote_alternate_box = box
            # Get role configurations for remote and remote_alternate
            remote_role = self.visualization_data[entry]['sections'].get('remote', {}).get("role_cfg", "N/A").lower()
            remote_alternate_role = self.visualization_data[entry]['sections'].get('remote_alternate', {}).get("role_cfg", "N/A").lower()
            # Debugging print statements
            print(f"Entry '{entry}' - Remote Role: {remote_role}, Remote Alternate Role: {remote_alternate_role}")
            # Resolve primary and secondary roles for remote and remote_alternate
            remote_primary_box, remote_secondary_box = None, None
            if remote_role == 'primary' and remote_alternate_role == 'secondary':
                remote_primary_box = remote_box
                remote_secondary_box = remote_alternate_box
            elif remote_role == 'secondary' and remote_alternate_role == 'primary':
                remote_primary_box = remote_alternate_box
                remote_secondary_box = remote_box
            elif remote_role == 'secondary' and remote_alternate_role != 'primary':
                remote_secondary_box = remote_box
                raise ValueError(f"Entry '{entry}' has a secondary remote box but no valid primary.")
            elif remote_alternate_role == 'secondary' and remote_role != 'primary':
                remote_secondary_box = remote_alternate_box
                raise ValueError(f"Entry '{entry}' has a secondary remote_alternate box but no valid primary.")
            else:
                raise ValueError(f"Entry '{entry}' must have one remote primary and one remote secondary. Got roles: remote={remote_role}, remote_alternate={remote_alternate_role}")
            # Display which box is primary and which is secondary
            print(f"Entry '{entry}' - Remote Primary: {remote_primary_box['name']}, Remote Secondary: {remote_secondary_box['name']}")
            # At this point, all roles are resolved, and boxes are correctly set
            # Get traffic port positions
            if remote_primary_box and remote_secondary_box:
                remote_secondary_pos = self.get_traffic_port_position(remote_secondary_box)
                remote_primary_pos = self.get_traffic_port_position(remote_primary_box)
                # Debugging positions
                print(f"Remote Secondary Position: {remote_secondary_pos}")
                print(f"Remote Primary Position: {remote_primary_pos}")
                if remote_secondary_pos and remote_primary_pos:
                    line_elements.append(
                        f'<line x1="{remote_secondary_pos[0]}" y1="{remote_secondary_pos[1]}" x2="{remote_primary_pos[0]}" y2="{remote_primary_pos[1]}" '
                        'class="remote-secondary-primary-line" marker-end="url(#arrowhead)"/>' 
                    )
        return line_elements



                
        
        
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
            '  .sender-receiver-line { stroke: #aa00aa; stroke-width: 2; }',
            '  .secondary-primary-line { stroke: #aa0000; stroke-width: 2; }',
            '  .remote-secondary-primary-line { stroke: #aa0000; stroke-width: 2; }',
            '  .recive-sender-line { stroke: #aa00aa; stroke-width: 2; }',
            '  .traffic-flow { animation: pulse 2s infinite; }',
            '  @keyframes pulse {',
            '    0% { stroke-opacity: 0.3; stroke-width: 1; }',
            '    50% { stroke-opacity: 1; stroke-width: 3; }',
            '    100% { stroke-opacity: 0.3; stroke-width: 1; }',
            '  }',
            '</style>',
            '<defs>',
            '  <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">',
            '    <polygon points="0 0, 10 3.5, 0 7" fill="#888888"/>',
            '  </marker>',
            '</defs>'
        ]

        self.box_indexes = []
        sorted_data = sorted(data, key=lambda x: x.get('time_stamp', 'N/A'))

        for entry_idx, entry in enumerate(sorted_data):
            time_stamp = entry.get('time_stamp', 'N/A')
            error_desc = entry.get('error_description', 'N/A')

            svg_content.append(f'<text class="timestamp" x="{current_x}" y="{current_y - 10}">Timestamp: {time_stamp}</text>')
            svg_content.append(f'<text class="error" x="{current_x}" y="{current_y}">Description: {error_desc}</text>')

            section_order = ['local', 'remote', 'alternate', 'remote_alternate']
            sections = entry.get('sections', {})

            for section_idx, section_name in enumerate(section_order):
                if section_name not in sections:
                    continue

                section_data = sections[section_name]

                svg_content.append(
                    f'<rect class="node" x="{current_x}" y="{current_y + 30}" '
                    f'width="{box_width}" height="{box_height}" rx="5" ry="5" '
                    f'data-entry="{entry_idx}" data-section="{section_idx}">'
                    f'<title>Entry {entry_idx} - Box {section_idx} ({section_name})</title></rect>'
                )

                svg_content.append(f'<text class="section-label" x="{current_x + 10}" y="{current_y + 60}">{section_name.upper()}</text>')
                svg_content.append(f'<text class="box-index" x="{current_x + box_width - 30}" y="{current_y + 60}">[{section_idx}]</text>')

                text_statement = f'State: {section_data.get("fsm_state", "N/A")}'
                state_index = None
                if "Prim.Tx-WAN Rx-ALT" in text_statement:
                    state_index = 1
                elif "Prim.Tx-WAN Rx-WAN" in text_statement:
                    state_index = 2
                elif "Prim.Tx-ALT Rx-WAN" in text_statement:
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
                elif "Secondary Standby" in text_statement:
                    state_index = 12

                self.box_indexes.append({
                    'entry': entry_idx,
                    'section': section_idx,
                    'name': section_name,
                    'x': current_x,
                    'y': current_y + 30,
                    'width': box_width,
                    'height': box_height,
                    'timestamp': time_stamp,
                    'state': state_index
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
                    10: "Visuvar?1",
                    12: "Visuvar?2",
                }

                state_value = state_descriptions.get(state_index, text_statement)
                svg_content.append(f'<text class="labela" x="{current_x + 10}" y="{current_y + 90}">{state_value}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 120}">Role: {section_data.get("role_state", "N/A")}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 150}">Config: {section_data.get("role_cfg", "N/A")}</text>')

              
                tx_ui, rx_ui = self.TXunRXmainitajs(section_data)
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 180}">TX: {tx_ui}</text>')
                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 210}">RX: {rx_ui}</text>')

                svg_content.append(f'<text class="label" x="{current_x + 10}" y="{current_y + 240}">Eth IP: {section_data.get("eth_ip", "N/A")}</text>')

                ports = ["LAN1", "LAN2", "LAN3", "WAN"]
                port_order = ports.copy()
                if section_name.startswith('r'):
                    port_order.remove("WAN")
                    port_order.insert(0, "WAN")

                for i, port in enumerate(port_order):
                    color = "#70ff70" if port in section_data.get("ports_up", []) else "#ff7070"
                    if port == section_data.get("traffic_port", ""):
                        color = "yellow"
                    x_pos = current_x + 30 + (i * 120)
                    svg_content.append(f'<rect x="{x_pos}" y="{current_y + 270}" width="90" height="20" fill="{color}" stroke="black" stroke-width="1.5"/>')
                    svg_content.append(f'<text class="label" x="{x_pos + 5}" y="{current_y + 285}">{port}</text>')

                current_x += box_width + 50
                if current_x + box_width > svg_width:
                    current_x = start_x
                    current_y += box_height + 100

        svg_content.extend(self.draw_sender_receiver_lines())
        svg_content.extend(self.draw_recive_sender_lines())
        svg_content.extend(self.socondarytoprimarry())
        svg_content.extend(self.remote_to_remote_alternate())
        svg_content.append('</svg>')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_content))

    def TXunRXmainitajs(self, section_data):
        ui_translations = {
            "trunk": "Balanced between Primary link [WAN] and Secondary link [via LAN2]",
            "primary": "Over Primary link [WAN]",
            "secondary": "Over Secondary link [via LAN2]",
            "none": "Tx traffic discarded [Tx Mute]",
            "disable": "Rx traffic discarded",
            "alt_port": "From Primary unit [via LAN2] to Radio [WAN]",
            "traffic_port": "From Traffic [LAN] port to Radio [WAN]",
            "both": "Over Primary link [WAN] and Secondary link [via LAN2]",
            "radio_port-alt_port": "From Radio [WAN] to Primary unit [via LAN2]",
            "radio_port-traffic_port": "From Radio [WAN] to Traffic [LAN] port",
            "unknown": "None"
        }

        tx_state = section_data.get("tx_state", "unknown")
        rx_state = section_data.get("rx_state", "unknown")
        return ui_translations.get(tx_state, "None"), ui_translations.get(rx_state, "None")



if __name__ == "__main__":
    root = tk.Tk()
    app = JSONTimeStampSaglabatajs(root)
    root.mainloop()