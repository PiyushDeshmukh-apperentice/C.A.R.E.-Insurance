import cv2
import json
import numpy as np
import os
import sys
from ultralytics import YOLO
from predict_cnn_severity import predict_severity

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Change to script directory to use relative paths
os.chdir(SCRIPT_DIR)

# Function to get full path relative to script location
def get_model_path(model_name):
    return os.path.join(SCRIPT_DIR, model_name)

def get_image_path(image_name):
    return os.path.join(SCRIPT_DIR, image_name)

# Allow image path to be passed as command line argument
if len(sys.argv) > 1:
    image_filename = sys.argv[1]
else:
    image_filename = "car damage 2.jpg"  # Default image name

# Build paths using relative location
part_model_path = get_model_path("car_parts.pt")
damage_model_path = get_model_path("damages_best.pt")
image_path = get_image_path(image_filename)

print(f"Script directory: {SCRIPT_DIR}")
print(f"Image path: {image_path}")

# Validate image path
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image not found: {image_path}")

# Set default output directory based on image location
output_dir = os.path.dirname(image_path) or "."

# Load models
print(f"Loading models from: {SCRIPT_DIR}")
part_model = YOLO(part_model_path)
damage_model = YOLO(damage_model_path)

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

# ------------------ EXTRACT MASKS AND BOXES ------------------
part_r = part_results[0]
damage_r = damage_results[0]

# Parts model generates MASKS
part_masks = part_r.masks.data.cpu().numpy() if part_r.masks else []
part_boxes = part_r.boxes

# Damage model generates BOUNDING BOXES (no masks)
damage_boxes = damage_r.boxes

# Resize masks to image size
H, W = orig.shape[:2]

def resize_mask(mask):
    return cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)

part_masks = [resize_mask(m) for m in part_masks]

# ------------------ OVERLAY COLORS ------------------
part_color = (0, 255, 0)     # Green
damage_color = (0, 0, 255)   # Red

overlay = orig.copy()

# Draw part masks in green
for mask in part_masks:
    overlay[mask > 0.5] = part_color

# Draw damage bounding boxes in red
for box in damage_boxes:
    bbox = box.xyxy[0].cpu().numpy().astype(int)  # [x1, y1, x2, y2]
    cv2.rectangle(overlay, (bbox[0], bbox[1]), (bbox[2], bbox[3]), damage_color, 2)

# ------------------ INTERSECTION LOGIC ------------------
# Get severity prediction from CNN model
predicted_class, severity_score = predict_severity(image_path)

print(f"\n{'='*60}")
print(f"DETECTION RESULTS:")
print(f"{'='*60}")
print(f"Total Parts Detected: {len(part_masks)}")
print(f"Total Damages Detected: {len(damage_boxes)}")
print(f"Overall Severity: {predicted_class} (Score: {severity_score})")
print(f"{'='*60}\n")

# Dictionary to store damages for each part (key: part_index, value: list of damages)
part_damage_map = {i: [] for i in range(len(part_masks))}

# Process each damage bounding box and find the part with maximum area inside it
for j, damage_box in enumerate(damage_boxes):
    d_cls = int(damage_box.cls[0])
    damage_name = damage_model.names[d_cls]
    damage_confidence = float(damage_box.conf[0])
    damage_bbox = damage_box.xyxy[0].cpu().numpy().astype(int)  # [x1, y1, x2, y2]
    
    # Extract the region
    x1, y1, x2, y2 = damage_bbox
    
    # Ensure coordinates are within image bounds
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(W, x2)
    y2 = min(H, y2)
    
    damage_box_area = (x2 - x1) * (y2 - y1)
    
    print(f"\nDamage {j+1}: {damage_name} (confidence: {damage_confidence:.2f})")
    
    # Find which part has the maximum area inside this damage box
    max_overlap_pixels = 0
    max_overlap_part_idx = -1
    overlap_data = []
    
    for i, p_mask in enumerate(part_masks):
        p_cls = int(part_boxes[i].cls[0])
        part_name = part_model.names[p_cls]
        
        # Get the part mask region within the damage box
        mask_region = p_mask[y1:y2, x1:x2]
        
        # Count how many pixels of the part are inside the damage box
        part_pixels_in_damage_box = np.sum(mask_region > 0.5)
        
        if part_pixels_in_damage_box > 0:
            # Calculate overlap percentage
            overlap_percentage = (part_pixels_in_damage_box / damage_box_area * 100) if damage_box_area > 0 else 0
            
            # Total part pixels
            total_part_pixels = np.sum(p_mask > 0.5)
            part_overlap_percentage = (part_pixels_in_damage_box / total_part_pixels * 100) if total_part_pixels > 0 else 0
            
            print(f"  - {part_name}: {part_pixels_in_damage_box} pixels ({overlap_percentage:.1f}% of damage box, {part_overlap_percentage:.1f}% of part)")
            
            overlap_data.append({
                'part_idx': i,
                'part_name': part_name,
                'pixels': part_pixels_in_damage_box,
                'overlap_percentage': overlap_percentage,
                'part_overlap_percentage': part_overlap_percentage,
                'mask_region': mask_region
            })
            
            # Track the part with maximum overlap
            if part_pixels_in_damage_box > max_overlap_pixels:
                max_overlap_pixels = part_pixels_in_damage_box
                max_overlap_part_idx = i
    
    # Only assign damage to the part with maximum area in the damage box
    if max_overlap_part_idx >= 0:
        max_part_data = [d for d in overlap_data if d['part_idx'] == max_overlap_part_idx][0]
        
        # Check if overlap is significant enough
        if max_part_data['overlap_percentage'] > 10 or max_part_data['part_overlap_percentage'] > 5:
            print(f"  ✓ ASSIGNED TO: {max_part_data['part_name']} (MAX area: {max_overlap_pixels} pixels)")
            
            # Highlight the overlapping region in BLUE
            overlap_mask = np.zeros_like(part_masks[max_overlap_part_idx], dtype=bool)
            overlap_mask[y1:y2, x1:x2] = max_part_data['mask_region'] > 0.5
            overlay[overlap_mask] = (255, 0, 0)
            
            # Store damage info for this part
            part_damage_map[max_overlap_part_idx].append({
                "damage_type": damage_name,
                "confidence": round(damage_confidence, 2),
                "overlap_pixels": int(max_overlap_pixels),
                "overlap_percentage": round(max_part_data['overlap_percentage'], 1),
                "part_coverage": round(max_part_data['part_overlap_percentage'], 1)
            })
        else:
            print(f"  ✗ Overlap too small to assign damage")
    else:
        print(f"  ✗ No part found in this damage box")

# Build damaged_parts list from the map
damaged_parts = []
for i, damages in part_damage_map.items():
    if damages:  # Only include parts that have damages
        p_cls = int(part_boxes[i].cls[0])
        part_name = part_model.names[p_cls]
        part_confidence = float(part_boxes[i].conf[0])
        
        damaged_parts.append({
            "part_name": part_name,
            "part_confidence": round(part_confidence, 2),
            "severity": severity_score,
            "damages": damages
        })

# Determine damage type based on severity
damage_type = "none"
if damaged_parts:
    max_severity = max(part["severity"] for part in damaged_parts)
    if max_severity > 0.7:
        damage_type = "severe"
    else:
        damage_type = "partial"

print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"{'='*60}")
print(f"Damage Type: {damage_type}")
print(f"Total Damaged Parts: {len(damaged_parts)}")
for part in damaged_parts:
    print(f"  - {part['part_name']}: {len(part['damages'])} damage(s) detected")
print(f"{'='*60}\n")

# ------------------ SAVE OUTPUT ------------------
# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "final_overlay_output.jpg")
cv2.imwrite(output_path, overlay)

print(f"Saved output image to: {output_path}")

# Save damage report as JSON
damage_report = {
    "image_path": image_path,
    "overall_severity": {
        "class": predicted_class,
        "score": severity_score
    },
    "damage": {
        "type": damage_type,
        "damaged_parts": damaged_parts,
        "total_parts_detected": len(part_masks),
        "total_damages_detected": len(damage_boxes),
        "total_damaged_parts": len(damaged_parts)
    }
}

json_output_path = os.path.join(output_dir, "damage_report.json")
with open(json_output_path, 'w') as f:
    json.dump(damage_report, f, indent=4)

print(f"Saved damage report to: {json_output_path}")
