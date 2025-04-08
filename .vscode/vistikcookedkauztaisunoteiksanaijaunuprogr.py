import json

# Example function to determine if a role is primary or secondary
def get_role_status(role_cfg):
    if role_cfg == "primary":
        return "primary"
    elif role_cfg == "secondary":
        return "secondary"
    else:
        return "unknown"

# Function to analyze JSON data
def analyze_json_files(json_data):
    line_elements = []

    # Loop through each JSON object (based on timestamp)
    for entry in json_data:
        time_stamp = entry.get("time_stamp")
        sections = entry.get("sections", {})
        
        # Get the role_cfg for 'local' and 'alternate'
        local_role = get_role_status(sections.get("local", {}).get("role_cfg"))
        alternate_role = get_role_status(sections.get("alternate", {}).get("role_cfg"))
        
        # Determine which is primary and which is secondary
        if local_role == "primary" and alternate_role == "secondary":
            primary = "local"
            secondary = "alternate"
        elif local_role == "secondary" and alternate_role == "primary":
            primary = "alternate"
            secondary = "local"
        else:
            primary = "unknown"
            secondary = "unknown"
        
        line_elements.append({
            "time_stamp": time_stamp,
            "primary": primary,
            "secondary": secondary
        })
    
    return line_elements

# Read the JSON file
with open("merged_results.json", "r") as file:
    json_data = json.load(file)

# Analyze the data
output = analyze_json_files(json_data)

# Output results
for item in output:
    print(f"Timestamp: {item['time_stamp']} - Primary: {item['primary']} - Secondary: {item['secondary']}")
