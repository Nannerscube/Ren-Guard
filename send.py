import requests
import re
import time
import json

def send_data():
    """
    Reads the detected.txt file, parses the final counts, and sends
    them to the web server.
    """
    # Wait a moment to ensure the file has been written by detect.py
    time.sleep(2)
    
    try:
        with open('detected.txt', 'r') as f:
            lines = f.readlines()

        # Find the summary section at the end of the file
        summary_start = -1
        for i, line in enumerate(lines):
            if "Summary of detected materials:" in line:
                summary_start = i + 1
                break
        
        if summary_start == -1:
            print("Could not find summary data in detected.txt.")
            return

        material_counts = {}
        for line in lines[summary_start:]:
            match = re.search(r"(\w+): (\d+)", line)
            if match:
                material = match.group(1)
                count = int(match.group(2))
                material_counts[material] = count

        # The URL for the receiving endpoint on the server
        server_url = "http://localhost:5000/post_data"

        print(f"Sending data to server: {material_counts}")
        response = requests.post(server_url, json=material_counts)
        response.raise_for_status() # Raise an exception for bad status codes
        print("Data successfully sent to the server.")

    except FileNotFoundError:
        print("Error: detected.txt not found. Did you run detect.py first?")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data to the server: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    send_data()
