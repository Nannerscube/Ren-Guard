import RPi.GPIO as GPIO
from time import sleep
from ultralytics import YOLO
from collections import Counter
import requests  # <-- NEW: Needed to send data to the server

# GPIO setup
GPIO.setmode(GPIO.BCM)

# Define pins
servo1_pin = 17  # Base rotation
servo2_pin = 18  # Drop actuator

GPIO.setup(servo1_pin, GPIO.OUT)
GPIO.setup(servo2_pin, GPIO.OUT)

# Set PWM at 50 Hz (standard for servos)
servo1 = GPIO.PWM(servo1_pin, 50)
servo2 = GPIO.PWM(servo2_pin, 50)

servo1.start(0)  # initial duty cycle
servo2.start(0)

# --- Helper: map angle (0–180°) to duty cycle ---
def set_angle(servo, angle):
    duty = 2 + (angle / 18)   # maps 0–180° -> ~2–12% duty cycle
    servo.ChangeDutyCycle(duty)
    sleep(0.5)
    servo.ChangeDutyCycle(0)  # stop sending continuous pulses

# Servo action map based on material
material_actions = {
    "Cardboard":  (0, 0),     # 0° base, 0° drop
    "Plastic":    (0, 120),   # 0° base, 120° drop
    "Glass":      (60, 0),    # 60° base, 0° drop
    "Tin":        (60, 120)   # 60° base, 120° drop
}

# Simplify YOLO label to material
def simplify_label(label):
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
labels_per_frame = []
print("Starting detection... Press Ctrl+C to stop.\n")

try:
    for result in model(source=0, stream=True, imgsz=(1280, 720)):
        frame_labels = []

        for box in result.boxes:
            cls_id = int(box.cls[0])
            raw_label = result.names[cls_id]
            material = simplify_label(raw_label)
            frame_labels.append(material)

            if material in material_actions:
                base_angle, drop_angle = material_actions[material]
                print(f"\nSorting: {material} → Base {base_angle}°, Drop {drop_angle}°")

                # Move base
                set_angle(servo1, base_angle)
                sleep(1)

                # Drop actuator
                set_angle(servo2, drop_angle)
                sleep(1)

                # Return drop actuator to neutral (90°)
                set_angle(servo2, 90)
                sleep(0.5)

        labels_per_frame.append(frame_labels)
        print("Detected materials in this frame:", frame_labels)

except KeyboardInterrupt:
    print("\nDetection stopped by user.")
finally:
    servo1.stop()
    servo2.stop()
    GPIO.cleanup()

# Save detected materials
# Lines 92-95 are replaced to send data to the server instead of writing to a text file.
# with open('detected.txt', 'w') as f:
#     for i, frame_labels in enumerate(labels_per_frame):
#         f.write(f"Frame {i + 1}: {', '.join(frame_labels)}\n")

# Detected objects realtime
all_materials = [label for frame in labels_per_frame for label in frame]
material_counts = Counter(all_materials)
print("\nSummary of detected materials:")
for material, count in material_counts.items():
    print(f"{material}: {count}")

# NEW CODE TO SEND DATA TO SERVER (Replaces the file-saving step)
try:
    # Convert Counter to dict for JSON serialization
    data_to_send = dict(material_counts)
    server_url = "http://localhost:5000/post_data"
    
    print("Detection complete. Sending data to dashboard server...")
    response = requests.post(server_url, json=data_to_send)
    response.raise_for_status() 
    print("Data successfully sent to the server.")
except requests.exceptions.RequestException as e:
    print(f"Failed to send data to the server: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
