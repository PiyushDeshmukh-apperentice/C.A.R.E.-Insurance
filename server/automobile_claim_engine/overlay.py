import cv2
import json
import numpy as np
import os
import sys
import random
from ultralytics import YOLO
from predict_cnn_severity import predict_severity

# Get the directory where this script is located for relative model loading
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_model_path(model_name):
    return os.path.join(SCRIPT_DIR, model_name)

def process_car_image(image_path, vehicle_type, output_dir=None):
    """
    Process vehicle image to detect damage and generate overlay.
    Arguments:
        image_path (str): Path to the input image.
        vehicle_type (str): Type of vehicle (e.g., 'car', 'scooty').
        output_dir (str, optional): Directory to save the output image. 
    """
    print(f"Script directory: {SCRIPT_DIR}")
    print(f"Processing {vehicle_type.upper()} Image: {image_path}")

    # --- 1. Path Configuration ---
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    if output_dir is None:
        output_dir = os.path.dirname(image_path) or "."
    
    os.makedirs(output_dir, exist_ok=True)
    output_image_path = os.path.join(output_dir, "final_overlay_output.jpg")

    # --- 2. Load Models (Dynamic based on vehicle_type) ---
    if vehicle_type == "scooty":
        part_model_path = get_model_path("models/scooty_parts.pt")
        damage_model_path = get_model_path("models/scooty_damages.pt")
    else: 
        part_model_path = get_model_path("models/car_parts.pt")
        damage_model_path = get_model_path("models/damages_best.pt")

    if not os.path.exists(part_model_path) or not os.path.exists(damage_model_path):
        raise FileNotFoundError("Required YOLO models not found.")

    part_model = YOLO(part_model_path)
    damage_model = YOLO(damage_model_path)

    # --- 3. Run Inference ---
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
        
    orig = image.copy()
    H, W = orig.shape[:2]

    part_results = part_model.predict(source=image_path, show=False, save=False)
    damage_results = damage_model.predict(source=image_path, show=False, save=False)

    part_r = part_results[0]
    damage_r = damage_results[0]

    part_masks = part_r.masks.data.cpu().numpy() if part_r.masks else []
    part_boxes = part_r.boxes
    damage_boxes = damage_r.boxes

    def resize_mask(mask):
        return cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)

    part_masks = [resize_mask(m) for m in part_masks]

    # --- 4. Draw Overlay ---
    part_color = (0, 255, 0)     # Green
    damage_color = (0, 0, 255)   # Red
    overlay = orig.copy()

    for mask in part_masks:
        overlay[mask > 0.5] = part_color

    for box in damage_boxes:
        bbox = box.xyxy[0].cpu().numpy().astype(int)
        cv2.rectangle(overlay, (bbox[0], bbox[1]), (bbox[2], bbox[3]), damage_color, 2)

    # --- 5. Logic for Intersection & Severity ---
    # SCOOTY CLAUSE: Random severity between 0.3 and 0.7
    if vehicle_type == "scooty":
        severity_score = round(random.uniform(0.3, 0.7), 2)
        print(f"ℹ️ Scooty detected: Using random severity score: {severity_score}")
    else:
        try:
            predicted_class, severity_score = predict_severity(image_path)
        except Exception as e:
            print(f"Warning: Severity prediction failed ({e}). Defaulting to 0.5.")
            severity_score = 0.5

    part_damage_map = {i: [] for i in range(len(part_masks))}

    for j, damage_box in enumerate(damage_boxes):
        d_cls = int(damage_box.cls[0])
        damage_name = damage_model.names[d_cls]
        damage_bbox = damage_box.xyxy[0].cpu().numpy().astype(int)
        
        x1, y1, x2, y2 = damage_bbox
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(W, x2), min(H, y2)
        damage_box_area = (x2 - x1) * (y2 - y1)
        
        max_overlap_pixels = 0
        max_overlap_part_idx = -1
        max_part_data = None
        
        for i, p_mask in enumerate(part_masks):
            mask_region = p_mask[y1:y2, x1:x2]
            part_pixels_in_damage_box = np.sum(mask_region > 0.5)
            
            if part_pixels_in_damage_box > max_overlap_pixels:
                max_overlap_pixels = part_pixels_in_damage_box
                max_overlap_part_idx = i
                max_part_data = {
                    'overlap_percentage': (part_pixels_in_damage_box / damage_box_area * 100) if damage_box_area > 0 else 0,
                    'part_overlap_percentage': (part_pixels_in_damage_box / np.sum(p_mask > 0.5) * 100) if np.sum(p_mask > 0.5) > 0 else 0,
                    'mask_region': mask_region
                }
        
        if max_overlap_part_idx >= 0 and max_part_data:
            if max_part_data['overlap_percentage'] > 10 or max_part_data['part_overlap_percentage'] > 5:
                overlap_mask = np.zeros_like(part_masks[max_overlap_part_idx], dtype=bool)
                overlap_mask[y1:y2, x1:x2] = max_part_data['mask_region'] > 0.5
                overlay[overlap_mask] = (255, 0, 0) # Highlight intersection in Blue
                
                part_damage_map[max_overlap_part_idx].append({
                    "damage_type": damage_name,
                    "confidence": round(float(damage_box.conf[0]), 2),
                    "overlap_pixels": int(max_overlap_pixels)
                })

    # --- 6. Build Return Structure ---
    damaged_parts = []
    for i, damages in part_damage_map.items():
        if damages:
            p_cls = int(part_boxes[i].cls[0])
            part_name = part_model.names[p_cls]
            
            # SCOOTY CLAUSE: Remap headlight to front_mudguard
            if vehicle_type == "scooty" and part_name.lower() == "headlight":
                print(f"🔄 Remapping scooty 'headlight' to 'front_mudguard'")
                part_name = "front_mudguard"
            
            damaged_parts.append({
                "part_name": part_name,
                "part_confidence": round(float(part_boxes[i].conf[0]), 2),
                "severity": severity_score,
                "damages": damages
            })

    damage_type = "severe" if any(p["severity"] > 0.7 for p in damaged_parts) else "partial"
    if not damaged_parts: damage_type = "none"

    cv2.imwrite(output_image_path, overlay)
    
    return {
        "output_image_path": output_image_path,
        "damage_data": {
            "type": damage_type,
            "damaged_parts": damaged_parts,
            "total_parts_detected": len(part_masks),
            "total_damages_detected": len(damage_boxes),
            "total_damaged_parts": len(damaged_parts)
        }
    }

if __name__ == "__main__":
    img_name = sys.argv[1] if len(sys.argv) > 1 else "car.jpg"
    v_type = sys.argv[2] if len(sys.argv) > 2 else "car"
    
    try:
        result = process_car_image(img_name, v_type)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")