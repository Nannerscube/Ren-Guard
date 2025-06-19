from ultralytics import YOLO
from collections import Counter
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# Servo setup
factory = PiGPIOFactory()
servo1 = Servo(17, pin_factory=factory)  # Base rotation
servo2 = Servo(18, pin_factory=factory)  # Drop actuator

# Helper to convert degrees to gpiozero value (-1 to 1)
def angle_to_value(degrees):
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
                servo1.value = angle_to_value(base_angle)
                sleep(1)

                # Drop
                servo2.value = angle_to_value(drop_angle)
                sleep(1)

                # Return drop to neutral (90° value=0)
                servo2.value = 0
                sleep(0.5)

        labels_per_frame.append(frame_labels)
        print("Detected materials in this frame:", frame_labels)

except KeyboardInterrupt:
    print("\nDetection stopped by user.")

# Save detected materials
with open('detected.txt', 'w') as f:
    for i, frame_labels in enumerate(labels_per_frame):
        f.write(f"Frame {i + 1}: {', '.join(frame_labels)}\n")

# Detected objects realtime
all_materials = [label for frame in labels_per_frame for label in frame]
material_counts = Counter(all_materials)
print("\nSummary of detected materials:")
for material, count in material_counts.items():
    print(f"{material}: {count}")

print("\nSaved all detected objects to 'detected.txt'.")