# Updated detect.py with a Flask web server

from ultralytics import YOLO
from collections import Counter
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread

# Servo setup
factory = PiGPIOFactory()
servo1 = Servo(17, pin_factory=factory)  # Base rotation
servo2 = Servo(18, pin_factory=factory)  # Drop actuator

# Helper to convert degrees to gpiozero value (-1 to 1)
def angle_to_value(degrees):
    """Converts a degree value to the -1 to 1 range for the servo."""
    return (degrees / 90.0) - 1

# Servo action map based on material
material_actions = {
    "Cardboard":  (0, 0),     # 0° base, 0° drop
    "Plastic":    (0, 120),   # 0° base, 120° drop
    "Glass":      (60, 0),    # 60° base, 0° drop
    "Tin":        (60, 120)   # 60° base, 120° drop
}

# Simplify YOLO label to material
def simplify_label(label):
    """Simplifies the raw YOLO label to a known material category."""
    if label.startswith("Tin_Can"):
        return "Tin"
    elif label.startswith("Cardboard"):
        return "Cardboard"
    elif label.startswith("Plastic"):
        return "Plastic"
    elif label.startswith("Glass"):
        return "Glass"
    else:
        return "Unknown"

# Load YOLO model
model = YOLO('my_model.pt')

# Global variable to store detected materials and their counts
# This is accessed by both the Flask app and the detection thread.
material_counts = {
    "Plastic": 0,
    "Cardboard": 0,
    "Glass": 0,
    "Tin": 0
}

# Flask App setup
app = Flask(__name__)
CORS(app)  # Enable CORS for the web page

# API endpoint to get the current recycling data
@app.route('/data')
def get_data():
    """Returns the current material counts as a JSON response."""
    return jsonify(material_counts)

# A thread to run the YOLO detection continuously in the background
def run_detection():
    """
    Main function for the detection thread.
    It continuously processes frames, updates material counts, and controls servos.
    """
    print("Starting detection... Press Ctrl+C to stop.")
    try:
        # source=0 means a webcam
        for result in model(source=0, stream=True, imgsz=(1280, 720)):
            # Loop through each detected object in the frame
            for box in result.boxes:
                cls_id = int(box.cls[0])
                raw_label = result.names[cls_id]
                material = simplify_label(raw_label)
                
                # Update the global counts for the web dashboard
                if material in material_counts:
                    material_counts[material] += 1
                
                print(f"Detected: {material}")

                # Control servos for sorting
                if material in material_actions:
                    base_angle, drop_angle = material_actions[material]
                    print(f"\nSorting: {material} -> Base {base_angle}°, Drop {drop_angle}°")
                    
                    # Move base
                    servo1.value = angle_to_value(base_angle)
                    sleep(1)
                    
                    # Drop
                    servo2.value = angle_to_value(drop_angle)
                    sleep(1)
                    
                    # Return drop to neutral (90° value=0)
                    servo2.value = 0
                    sleep(0.5)

            # Wait a moment before processing the next frame
            sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nDetection stopped by user.")
    except Exception as e:
        print(f"An error occurred in detection thread: {e}")

# Start the detection thread
detection_thread = Thread(target=run_detection)
detection_thread.daemon = True # Daemon threads are terminated when the main thread stops
detection_thread.start()

# Run the Flask app
if __name__ == '__main__':
    # Run on all available network interfaces on port 5000
    app.run(host='0.0.0.0', port=5000)
