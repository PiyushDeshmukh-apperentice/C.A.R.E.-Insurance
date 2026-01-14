import cv2
import json
import numpy as np
import os
from pathlib import Path
from ultralytics import YOLO
from predict_cnn_severity import predict_severity

def process_car_image(image_path: str, output_dir: str = None) -> dict:
    """
    Process car image to detect damage and generate overlay
    Returns: {
        "output_image_path": str,
        "damage_data": {
            "type": str,
            "damaged_parts": [{"part_name": str, "severity": float}]
        }
    }
    """
    try:
        # Ensure image exists
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Set default output directory
        if output_dir is None:
            output_dir = os.path.dirname(image_path) or "."
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Load models with proper paths
        engine_dir = os.path.dirname(__file__)
        models_dir = os.path.join(engine_dir, "models")
        
        part_model_path = os.path.join(models_dir, "best.pt")  # Car parts detection model
        damage_model_path = os.path.join(models_dir, "damage_model.pt")  # Damage severity model
        
        # Verify models exist before loading
        if not os.path.exists(part_model_path):
            raise FileNotFoundError(f"Car parts model not found at {part_model_path}")
        if not os.path.exists(damage_model_path):
            raise FileNotFoundError(f"Damage model not found at {damage_model_path}")
            
        part_model = YOLO(part_model_path)
        damage_model = YOLO(damage_model_path)
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        orig = image.copy()
        
        # Run inference
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
        
        # Extract masks
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
        
        # Create overlay
        part_color = (0, 255, 0)     # Green
        damage_color = (0, 0, 255)   # Red
        
        overlay = orig.copy()
        
        # Draw part masks
        for mask in part_masks:
            overlay[mask > 0.5] = part_color
        
        # Draw damage masks
        for mask in damage_masks:
            overlay[mask > 0.5] = damage_color
        
        # Process intersection and get damaged parts
        damaged_parts = []
        
        # Get severity prediction from CNN model
        try:
            predicted_class, severity_score = predict_severity(image_path)
        except:
            severity_score = 0.5
            predicted_class = "unknown"
        
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
                    print(f"Damage detected: {part_name} is {damage_name}")
                    
                    # Highlight intersection in BLUE
                    overlay[intersection] = (255, 0, 0)
                    
                    # Store damaged part info with severity from CNN prediction
                    damaged_parts.append({
                        "part_name": part_name,
                        "severity": float(severity_score)
                    })
        
        # Determine damage type based on severity
        damage_type = "none"
        if damaged_parts:
            max_severity = max(part["severity"] for part in damaged_parts)
            if max_severity > 0.7:
                damage_type = "severe"
            else:
                damage_type = "partial"
        
        # Save output image
        output_image_path = os.path.join(output_dir, "final_overlay_output.jpg")
        cv2.imwrite(output_image_path, overlay)
        print(f"Saved output image to: {output_image_path}")
        
        return {
            "output_image_path": output_image_path,
            "damage_data": {
                "type": damage_type,
                "damaged_parts": damaged_parts
            }
        }
    
    except Exception as e:
        print(f"Error processing car image: {str(e)}")
        raise

# Legacy: Keep script execution for backward compatibility
if __name__ == "__main__":
    image_path = "car.jpg"
    result = process_car_image(image_path)
    
    print(json.dumps(result, indent=2))