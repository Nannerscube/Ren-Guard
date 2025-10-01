import requests
import re
import time
from collections import Counter

def parse_and_deduplicate_data(file_path='detected.txt'):
    """
    Reads the detected.txt file, parses the list of materials detected per frame,
    and applies a de-duplication logic: counts a material only once after a 
    'break' (a frame with no valid detection).
    
    Returns a dictionary of final, de-duplicated counts.
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("Error: detected.txt not found. Did you run detect.py first?")
        return {}

    final_counts = Counter()
    # State variable to track the material seen in the previous frame
    # We use 'None' to represent a "space" (empty frame/no valid detection)
    last_detected_material = None
    
    # Define valid materials that should be counted
    valid_materials = {"Cardboard", "Plastic", "Glass", "Tin"}

    for line in lines:
        # Extract the list of materials detected in the current frame from a line like "Frame 1: Cardboard"
        match = re.search(r"Frame \d+: (.*)", line)
        if not match:
            # If the line doesn't match the expected format, treat it as a break
            current_frame_material = None
        else:
            # Clean and split the comma-separated materials
            materials_list = [m.strip() for m in match.group(1).split(',') if m.strip()]
            
            # Find the single most relevant material detected in the current frame
            # This logic assumes the first detected item is the one we care about for counting
            current_frame_material = next((m for m in materials_list if m in valid_materials), None)
        
        #  De-duplication Logic
        # if A valid material is detected in the current frame
        if current_frame_material and current_frame_material in valid_materials:
            
            # If the detected material is DIFFERENT from the one in the previous frame (or if the previous was 'None'),
            # then this is considered a new, successfully introduced item.
            if current_frame_material != last_detected_material:
                final_counts[current_frame_material] += 1
            
            # Update the state to the currently detected material
            last_detected_material = current_frame_material
            
        # if No valid material is detected (e.g., empty frame, or 'Unknown')
        else:
            # This creates the "space" or pause, allowing the next item, even if it's the same type, to be counted.
            last_detected_material = None
                
    return dict(final_counts)

def send_data():
    """
    Calls the parsing function and sends the de-duplicated counts to the web server.
    """
    # Wait a moment to ensure the file has been written by detect.py
    # This wait time may need adjustment depending on how long detect.py runs
    print("Waiting 2 seconds to ensure detect.py has finished writing the file...")
    time.sleep(2)
    
    data_to_send = parse_and_deduplicate_data()
    
    if not data_to_send:
        print("No valid material data was found or counted. Nothing sent.")
        return

    # The URL for the receiving endpoint on the server
    server_url = "http://localhost:5000/post_data"

    try:
        print(f"Sending de-duplicated counts to server: {data_to_send}")
        response = requests.post(server_url, json=data_to_send)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        print("Data successfully sent to the server.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to send data to the server (Is dashboard_server.py running?): {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    send_data()
