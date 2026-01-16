import cv2
import json
import numpy as np
import os
import sys
from ultralytics import YOLO
from predict_cnn_severity import predict_severity

# Get the directory where this script is located for relative model loading
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_model_path(model_name):
    return os.path.join(SCRIPT_DIR, model_name)

def process_car_image(image_path, output_dir=None):
    """
    Process car image to detect damage and generate overlay.
    Arguments:
        image_path (str): Path to the input image.
        output_dir (str, optional): Directory to save the output image. 
                                    Defaults to input image directory.
    """
    print(f"Script directory: {SCRIPT_DIR}")
    print(f"Processing Image: {image_path}")

    # --- 1. Path Configuration (User Requested Logic) ---
    # Ensure image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Set default output directory to same as input image if not provided
    if output_dir is None:
        output_dir = os.path.dirname(image_path) or "."
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define Final Output Path
    output_image_path = os.path.join(output_dir, "final_overlay_output.jpg")

    # --- 2. Load Models ---
    # Build paths using relative location
    part_model_path = get_model_path("models/car_parts.pt")
    damage_model_path = get_model_path("models/damages_best.pt")

    print(f"Loading models from: {SCRIPT_DIR}")
    # Verify models exist
    if not os.path.exists(part_model_path):
        raise FileNotFoundError(f"Car parts model not found at {part_model_path}")
    if not os.path.exists(damage_model_path):
        raise FileNotFoundError(f"Damage model not found at {damage_model_path}")

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

    # Parts model generates MASKS
    part_masks = part_r.masks.data.cpu().numpy() if part_r.masks else []
    part_boxes = part_r.boxes

    # Damage model generates BOUNDING BOXES (Logic adjusted for detection model)
    damage_boxes = damage_r.boxes

    # Helper to resize masks
    def resize_mask(mask):
        return cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)

    part_masks = [resize_mask(m) for m in part_masks]

    # --- 4. Draw Overlay ---
    part_color = (0, 255, 0)     # Green
    damage_color = (0, 0, 255)   # Red
    overlay = orig.copy()

    # Draw part masks in green
    for mask in part_masks:
        overlay[mask > 0.5] = part_color

    # Draw damage bounding boxes in red
    for box in damage_boxes:
        bbox = box.xyxy[0].cpu().numpy().astype(int)
        cv2.rectangle(overlay, (bbox[0], bbox[1]), (bbox[2], bbox[3]), damage_color, 2)

    # --- 5. Logic for Intersection & Severity ---
    # Get severity prediction from CNN model
    try:
        predicted_class, severity_score = predict_severity(image_path)
    except Exception as e:
        print(f"Warning: Severity prediction failed ({e}). Defaulting to moderate.")
        predicted_class, severity_score = "moderate", 0.5

    # Map damages to specific parts
    part_damage_map = {i: [] for i in range(len(part_masks))}

    for j, damage_box in enumerate(damage_boxes):
        d_cls = int(damage_box.cls[0])
        damage_name = damage_model.names[d_cls]
        damage_confidence = float(damage_box.conf[0])
        damage_bbox = damage_box.xyxy[0].cpu().numpy().astype(int)
        
        x1, y1, x2, y2 = damage_bbox
        # Clip to image bounds
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(W, x2), min(H, y2)
        
        damage_box_area = (x2 - x1) * (y2 - y1)
        
        # Variables to track which part 'owns' this damage
        max_overlap_pixels = 0
        max_overlap_part_idx = -1
        max_part_data = None
        
        # Check every part mask against this damage box
        for i, p_mask in enumerate(part_masks):
            mask_region = p_mask[y1:y2, x1:x2]
            part_pixels_in_damage_box = np.sum(mask_region > 0.5)
            
            if part_pixels_in_damage_box > 0:
                overlap_percentage = (part_pixels_in_damage_box / damage_box_area * 100) if damage_box_area > 0 else 0
                total_part_pixels = np.sum(p_mask > 0.5)
                part_overlap_percentage = (part_pixels_in_damage_box / total_part_pixels * 100) if total_part_pixels > 0 else 0
                
                # We assign damage to the part that has the MOST pixels inside the damage box
                if part_pixels_in_damage_box > max_overlap_pixels:
                    max_overlap_pixels = part_pixels_in_damage_box
                    max_overlap_part_idx = i
                    max_part_data = {
                        'overlap_percentage': overlap_percentage,
                        'part_overlap_percentage': part_overlap_percentage,
                        'mask_region': mask_region
                    }
        
        # If we found a valid part for this damage
        if max_overlap_part_idx >= 0 and max_part_data:
            # Threshold to avoid noise
            if max_part_data['overlap_percentage'] > 10 or max_part_data['part_overlap_percentage'] > 5:
                # Highlight the specific intersection in BLUE
                overlap_mask = np.zeros_like(part_masks[max_overlap_part_idx], dtype=bool)
                overlap_mask[y1:y2, x1:x2] = max_part_data['mask_region'] > 0.5
                overlay[overlap_mask] = (255, 0, 0)
                
                part_damage_map[max_overlap_part_idx].append({
                    "damage_type": damage_name,
                    "confidence": round(damage_confidence, 2),
                    "overlap_pixels": int(max_overlap_pixels),
                    "overlap_percentage": round(max_part_data['overlap_percentage'], 1),
                    "part_coverage": round(max_part_data['part_overlap_percentage'], 1)
                })

    # --- 6. Build Return Structure ---
    damaged_parts = []
    for i, damages in part_damage_map.items():
        if damages:  # Only include parts that have damages
            p_cls = int(part_boxes[i].cls[0])
            part_name = part_model.names[p_cls]
            part_confidence = float(part_boxes[i].conf[0])
            
            damaged_parts.append({
                "part_name": part_name,
                "part_confidence": round(part_confidence, 2),
                "severity": severity_score, # Propagate global severity to parts
                "damages": damages
            })

    # Determine overall damage type
    damage_type = "partial"
    if damaged_parts:
        if any(p["severity"] > 0.7 for p in damaged_parts):
            damage_type = "severe"
    else:
        damage_type = "none"

    # Save the overlay image
    cv2.imwrite(output_image_path, overlay)
    print(f"Saved output image to: {output_image_path}")

    # Return the exact dictionary structure required by claim_engine
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

# Legacy support for running this script directly
if __name__ == "__main__":
    # Get image from command line or default
    img_name = sys.argv[1] if len(sys.argv) > 1 else "car.jpg"
    
    try:
        result = process_car_image(img_name)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")