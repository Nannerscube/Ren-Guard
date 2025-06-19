from ultralytics import YOLO
from collections import Counter
import time

# Function to simplify detailed labels to general material categories
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

# Load the YOLO model (update this path if needed)
model = YOLO('my_model.pt')

# Store simplified labels per frame
labels_per_frame = []

print("Starting detection... Press Ctrl+C to stop.\n")

try:
    #Begin webcam stream
    for result in model(source=0, stream=True, imgsz=(1280, 720)):
        frame_labels = []

        for box in result.boxes:
            cls_id = int(box.cls[0])
            raw_label = result.names[cls_id]
            simple_label = simplify_label(raw_label)
            frame_labels.append(simple_label)

        labels_per_frame.append(frame_labels)
        print("Detected materials in this frame:", frame_labels)

except KeyboardInterrupt:
    print("\nDetection stopped by user.")

# Save results to a text file
with open('detected.txt', 'w') as f:
    for i, frame_labels in enumerate(labels_per_frame):
        f.write(f"Frame {i + 1}: {', '.join(frame_labels)}\n")

# Print a summary of all detected materials
all_materials = [label for frame in labels_per_frame for label in frame]
material_counts = Counter(all_materials)

print("\nSummary of detected materials:")
for material, count in material_counts.items():
    print(f"{material}: {count}")

print("\nSaved all detected objects to 'detected.txt'.")