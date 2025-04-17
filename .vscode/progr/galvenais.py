import os
import json
import glob
import re
from datetime import datetime
import tkinter as tk
import os
os.system("")

class JSONTimeStampSaglabatajs:
    def __init__(self):
        self.directories = {1: None, 2: None, 3: None, 4: None}
        self.box_indexes = []
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
                raise Exception(f"Error reading file {error_file}: {str(e)}")
        return error_mapping

    def process_files(self, directories, identifiers, mode_var):
        eth_mac_errors = []
        macandip = []
        selected_dirs = [d for d in directories.values() if d]

        if not selected_dirs:
            raise Exception("Please select at least one directory!")

        for dir_num in directories:
            if directories[dir_num] and not identifiers[dir_num]:
                raise Exception(f"Please enter an identifier for directory {dir_num}!")

        total_files, success_count, skipped_count = 0, 0, 0
        merged_data = []
        existing_timestamps = set()
        error_messages = []
        eth_ip_errors = []  # New list to store ETH IP validation errors
        previous_eth_ip=[]

        # First pass: collect all FSM state changes from event logs
        fsm_events = {}
        for dir_num, directory in directories.items():
            if not directory:
                continue
            try:
                error_mapping = self.load_error_mapping(directory)
                for (date_part, time_part), error_desc in error_mapping.items():
                    if "Aggregation FSM state changed" in error_desc:
                        timestamp = f"{date_part} {time_part}"
                        decoded_desc = self.decode_error_description(error_desc, mode_var)
                        fsm_events[timestamp] = {
                            "timestamp": timestamp,
                            "error_description": decoded_desc,
                            "has_json": False  # Will be set to True if we find matching JSON
                        }
            except Exception as e:
                error_messages.append(f"Error processing event logs in directory {dir_num}: {str(e)}")

        # Second pass: process JSON files and match with FSM events


        for dir_num, directory in directories.items():
            if not directory:
                continue
            
            current_identifier = identifiers[dir_num]
            b=0

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
                            
                            # Skip if we've already processed this timestamp
                            if time_stamp in existing_timestamps:
                                skipped_count += 1
                                continue
                            
                            # Mark this timestamp as having JSON data
                            if time_stamp in fsm_events:
                                fsm_events[time_stamp]["has_json"] = True
                            else:
                                # If JSON exists but no eventlog entry, skip it
                                skipped_count += 1
                                continue
                                
                            sections = {
                                'local': data.get('local', {}).get('info', {}),
                                'alternate': data.get('alternate', {}).get('info', {}),
                                'remote': data.get('remote', {}).get('info', {}),
                                'remote_alternate': data.get('remote.alternate', {}).get('info', {})
                            }
                            
                            entry = {
                                "time_stamp": time_stamp,
                                "device_identifier": current_identifier,
                                "error_description": fsm_events[time_stamp]["error_description"],
                                "sections": {}
                            }
                            
                            

                            #lai dabutu mac adresi
                            i=0
                            for section_name, section_data in sections.items():
                                if not section_data:
                                    continue

                                # Izveido kļūdu sarakstus tikai šim ierakstam
                                ip_errors = []
                                mac_errors = []
                                macandip = []

                                # ---- ETH MAC Validation ----
                                eth_mac = section_data.get("eth_mac", "N/A")
                                if eth_mac != 'N/A':
                                    parts1 = [p.lower() for p in eth_mac.split(':')]
                                    if len(parts1) != 6:
                                        mac_errors.append(f"Timestamp {time_stamp}, section {section_name}: Invalid MAC format {eth_mac}")
                                    else:
                                        last_octet_str1 = str(parts1[-1])
                                        if len(set(last_octet_str1)) != len(last_octet_str1):
                                            repeated_octets1 = [octet for octet in last_octet_str1 if last_octet_str1.count(octet) > 1]
                                            mac_errors.append(
                                                f"Timestamp {time_stamp}, section {section_name}: Repeated octets found in MAC '{eth_mac}' ({', '.join(set(repeated_octets1))})"
                                            )
                                        if last_octet_str1 not in ["00", "ac", "f7", "ad", "ae"]:
                                            mac_errors.append(
                                                f"Timestamp {time_stamp}, section {section_name}: Invalid last symbols '{last_octet_str1}' in MAC '{eth_mac}'"
                                            )

                                # ---- ETH IP Validation ----
                                eth_ip = section_data.get("eth_ip", "N/A")
                                eth_ip_name = self.get_eth_ip_name(eth_ip)
                                if eth_ip != 'N/A':
                                    if isinstance(eth_ip, dict):
                                        eth_ip = eth_ip.get('ip', 'N/A')
                                        if eth_ip == 'N/A':
                                            continue

                                    parts = eth_ip.split('.')
                                    if len(parts) != 4:
                                        ip_errors.append(f"Timestamp {time_stamp}, section {section_name}: Invalid IP format '{eth_ip}'")
                                    else:
                                        last_octet_str = str(parts[-1])
                                        try:
                                            last_octet = int(last_octet_str)
                                            if last_octet not in [0, 10, 11, 12, 13]:  # 00 nav derīgs Python skaitlis
                                                ip_errors.append(
                                                    f"Timestamp {time_stamp}, section {section_name}: Invalid last symbols {last_octet} in IP '{eth_ip}'"
                                                )
                                        except ValueError:
                                            ip_errors.append(
                                                f"Timestamp {time_stamp}, section {section_name}: Invalid last symbols '{last_octet_str}' in IP '{eth_ip}'"
                                            )

                                # --- MAC and IP mismatch check ---
                                if self.get_eth_mac_name(eth_mac) != eth_ip_name:
                                    macandip.append(f"Timestamp {time_stamp} ETH MAC state: {self.get_eth_mac_name(eth_mac)} isn't the same as IP state: {eth_ip_name}")

                                eth_ip = section_data.get("eth_ip")  # Or however you're assigning it

                                
                                print("Previous eth_ip:", previous_eth_ip)

                                print("Current eth_ip:", eth_ip)
                                print("\n")
                                previous_eth_ip = eth_ip

                                # Save results for this section
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
                                    "eth_mac": eth_mac,
                                    "eth_ip_name": eth_ip_name,
                                    "eth_mac_name": self.get_eth_mac_name(eth_mac),
                                    "errorsip": ip_errors,
                                    "errorsmac": mac_errors,
                                    "macandip": macandip
                                }

                                

                            merged_data.append(entry)
                            existing_timestamps.add(time_stamp)
                            success_count += 1
                        except Exception as e:
                            error_messages.append(f"[Directory {dir_num}] {file} Error: {str(e)}")
                            continue
        
        # Third pass: add FSM events that didn't have matching JSON files
        for timestamp, event_data in fsm_events.items():
            if not event_data["has_json"] and timestamp not in existing_timestamps:
                entry = {
                    "time_stamp": timestamp,
                    "device_identifier": "",  # Will be filled in next step
                    "error_description": event_data["error_description"],
                    "sections": {}  # Empty sections
                }
                merged_data.append(entry)
        
        # Assign device identifiers to entries without JSON
        for entry in merged_data:
            if not entry.get("device_identifier"):
                # Find the first directory that has this timestamp in its eventlog
                for dir_num, directory in directories.items():
                    if not directory:
                        continue
                    try:
                        error_mapping = self.load_error_mapping(directory)
                        date_part, time_part = entry["time_stamp"].split(' ')
                        if (date_part, time_part) in error_mapping:
                            entry["device_identifier"] = identifiers[dir_num]
                            break
                    except:
                        continue
        
        merged_data.sort(key=lambda x: x["time_stamp"])
        merged_file_path = os.path.join(os.getcwd(), "merged_results.json")
        with open(merged_file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=4, ensure_ascii=False)

        # Store merged_data in the instance for later use
        self.merged_data = merged_data

        # Save ETH IP errors to a separate log file if any were found
        if eth_ip_errors:
            eth_ip_error_msg = "ETH IP validation errors detected:\n" + "\n".join(eth_ip_errors) #viz
        else:
            eth_ip_error_msg = "No ETH IP validation errors found"

        if eth_mac_errors:
            eth_mac_error_msg = "ETH Mac errors:\n" + "\n".join(eth_mac_errors) #vajag vizualizet kkā
        else:
            eth_mac_error_msg = "No ETH Mac errors found"

        macandip_msg=[]
        if macandip:
            macandip_msg = "ETH Isn't the same as Ip state:\n" + "\n".join(macandip)



        return {
            "total_files": total_files,
            "success_count": success_count,
            "skipped_count": skipped_count,
            "merged_file_path": merged_file_path,
            "error_msg": error_messages,  # General processing errors
            "eth_ip_errors": eth_ip_error_msg,  # ETH IP specific validation errors
            "eth_mac_errors": eth_mac_error_msg,  # ETH MAC specific validation errors
            "M": macandip_msg
        }


    def get_eth_ip_name(self, eth_ip):
        if not eth_ip or eth_ip == "N/A":
            return "N/A"
        
        if isinstance(eth_ip, dict):
            eth_ip = eth_ip.get("ip", "N/A")
        
        try:
            last_octet = int(eth_ip.split('.')[-1])
        except (ValueError, AttributeError):
            return eth_ip
        
        role_mapping = { #nosaka statususus
            10: "l primary",
            11: "rem primary",
            12: "l secondary",
            13: "rem secondary"
        }
        
        return role_mapping.get(last_octet, eth_ip)
    
    def get_eth_mac_name(self, eth_mac):
        """Determine the role based on MAC address last octet"""
        if not eth_mac or eth_mac == "N/A":
            return "N/A"
        
        try:
            # Extract last octet from MAC address (after last colon)
            last_octet = eth_mac.split(':')[-1].lower()
        except (ValueError, AttributeError):
            return eth_mac
        
        # Mapping of MAC last octets to their roles
        role_mapping1 = {    
            "ae": "l primary",   # Prim
            "f7": "rem primary", 
            "ac": "l secondary",  
            "ad": "rem secondary"   
        }
        
        return role_mapping1.get(last_octet, eth_mac)

    def decode_error_description(self, error_desc, mode):
        match = re.search(r'rsn_id:\((\d+)\)', error_desc)
        if match:
            rsn_id = int(match.group(1))
            reason = self.reason_ids.get(mode, {}).get(rsn_id, f"Unknown reason ({rsn_id})")
            error_desc = re.sub(r'rsn_id:\(\d+\)', reason, error_desc)
        return error_desc

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
        """Determine which boxes can send data and which 'r' sections can receive."""
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
        """Determine which boxes can receive data (local sections) and which 'r' sections can send."""
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
        #print(line_elements)
        return line_elements


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
            
            # Get traffic port positions
            if remote_primary_box and remote_secondary_box:
                remote_secondary_pos = self.get_traffic_port_position(remote_secondary_box)
                remote_primary_pos = self.get_traffic_port_position(remote_primary_box)
                if remote_secondary_pos and remote_primary_pos:
                    line_elements.append(
                        f'<line x1="{remote_secondary_pos[0]}" y1="{remote_secondary_pos[1]}" x2="{remote_primary_pos[0]}" y2="{remote_primary_pos[1]}" '
                        'class="remote-secondary-primary-line" marker-end="url(#arrowhead)"/>' 
                    )
        return line_elements

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