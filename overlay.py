import cv2
import json
import random
import numpy as np
from ultralytics import YOLO

# ------------------ LOAD MODELS ------------------
part_model = YOLO("car_part_model.pt")
damage_model = YOLO("car_damage_model.pt")

image_path = "car.jpg"
image = cv2.imread(image_path)
orig = image.copy()

# ------------------ RUN INFERENCE ------------------
part_results = part_model.predict(
    source=image_path,
    show=False,
    save=False
)

damage_results = damage_model.predict(
    source=image_path,
    show=False,
    save=False
)

# ------------------ EXTRACT MASKS ------------------
part_r = part_results[0]
damage_r = damage_results[0]

part_masks = part_r.masks.data.cpu().numpy() if part_r.masks else []
damage_masks = damage_r.masks.data.cpu().numpy() if damage_r.masks else []

part_boxes = part_r.boxes
damage_boxes = damage_r.boxes

# Resize masks to image size
H, W = orig.shape[:2]

def resize_mask(mask):
    return cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)

part_masks = [resize_mask(m) for m in part_masks]
damage_masks = [resize_mask(m) for m in damage_masks]

# ------------------ OVERLAY COLORS ------------------
part_color = (0, 255, 0)     # Green
damage_color = (0, 0, 255)   # Red

overlay = orig.copy()

# Draw part masks
for mask in part_masks:
    overlay[mask > 0.5] = part_color

# Draw damage masks
for mask in damage_masks:
    overlay[mask > 0.5] = damage_color

# ------------------ INTERSECTION LOGIC ------------------
damaged_parts = []

for i, p_mask in enumerate(part_masks):
    p_cls = int(part_boxes[i].cls[0])
    part_name = part_model.names[p_cls]

    for j, d_mask in enumerate(damage_masks):
        d_cls = int(damage_boxes[j].cls[0])
        damage_name = damage_model.names[d_cls]
        damage_confidence = float(damage_boxes[j].conf[0])

        # Pixel-wise intersection
        intersection = np.logical_and(p_mask > 0.5, d_mask > 0.5)
        overlap_pixels = np.sum(intersection)

        if overlap_pixels > 100:  # threshold to avoid noise
            print(f"{part_name} is {damage_name}")

            # Highlight intersection in BLUE
            overlay[intersection] = (255, 0, 0)
            
            # Store damaged part info
            damaged_parts.append({
                "part_name": part_name,
                "severity": round(random.uniform(0, 1), 2)
            })

# Determine damage type based on severity
damage_type = "none"
if damaged_parts:
    max_severity = max(part["severity"] for part in damaged_parts)
    if max_severity > 0.7:
        damage_type = "severe"
    else:
        damage_type = "partial"

# ------------------ SAVE OUTPUT ------------------
output_path = "final_overlay_output.jpg"
cv2.imwrite(output_path, overlay)

print(f"Saved output image to: {output_path}")

# Save damage report as JSON
damage_report = {
    "damage": {
        "type": damage_type,
        "damaged_parts": damaged_parts
    }
}

json_output_path = "damage_report.json"
with open(json_output_path, 'w') as f:
    json.dump(damage_report, f, indent=4)

print(f"Saved damage report to: {json_output_path}")
