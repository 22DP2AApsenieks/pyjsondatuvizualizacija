import os
import json
import webbrowser
import tkinter as tk
from tkinter import messagebox

class Visualization:
    def __init__(self, logic):
        self.logic = logic
        self.current_index = 0
        self.visualization_limit = 1
        self.visualization_data = []
        self.visualization_window = None

    def visualize_all(self):
        merged_file = os.path.join(os.getcwd(), "merged_results.json")
        
        try:
            if not os.path.exists(merged_file):
                messagebox.showerror("Kļūda", "Nav atrasts apvienotais fails (merged_results.json)")
                return

            with open(merged_file, 'r', encoding='utf-8') as f:
                self.visualization_data = json.load(f)

            if not self.visualization_data:
                messagebox.showinfo("Info", "Nav datu vizualizācijai!")
                return

            # Reset visualization state
            self.current_index = 0
            self.visualization_limit = 1
            
            # Show initial visualization
            self.show_visualizations()

        except Exception as e:
            messagebox.showerror("Kļūda", f"Vizualizācijas kļūda: {str(e)}")

    def show_visualizations(self):
        start = self.current_index
        end = min(self.current_index + self.visualization_limit, len(self.visualization_data))
        current_data = self.visualization_data[start:end]
        
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

        # Store visualization data in logic for line drawing functions
        self.logic.visualization_data = data
        self.logic.box_indexes = []

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

                self.logic.box_indexes.append({
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

                tx_ui, rx_ui = self.logic.TXunRXmainitajs(section_data)
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

        # Add all connection lines
        svg_content.extend(self.logic.draw_sender_receiver_lines())
        svg_content.extend(self.logic.draw_recive_sender_lines())
        svg_content.extend(self.logic.socondarytoprimarry())
        svg_content.extend(self.logic.remote_to_remote_alternate())
        
        svg_content.append('</svg>')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(svg_content))