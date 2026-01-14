import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
import time
import random
import os
from pathlib import Path

# Custom CNN Architecture
class CustomCNN(nn.Module):
    def __init__(self, num_classes=3):
        super(CustomCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(16),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 14 * 14, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

def predict_severity(IMAGE_TO_PREDICT):
    print(f"🔮 Predicting severity for: {IMAGE_TO_PREDICT}")
    
    # --- 1. Dynamic Path Configuration ---
    # Get the directory where this script is located
    current_dir = Path(__file__).parent
    # Look for model in the 'models' subdirectory
    # Note: Based on your tree, the file is likely 'best_model.pth'
    MODEL_WEIGHTS_PATH = current_dir / "models" / "best_model.pth"
    
    # Fallback if best_model.pth doesn't exist, try others
    if not MODEL_WEIGHTS_PATH.exists():
         MODEL_WEIGHTS_PATH = current_dir / "models" / "car_severity_model.pth"

    if not MODEL_WEIGHTS_PATH.exists():
        print(f"⚠️ Severity Model not found at {MODEL_WEIGHTS_PATH}. Returning default.")
        return "moderate", 0.5

    CLASS_LABELS = ['01-minor', '02-moderate', '03-major'] 
    NUM_CLASSES = len(CLASS_LABELS)

    # --- 2. Setup Device ---
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = CustomCNN(num_classes=NUM_CLASSES)
    
    try:
        model.load_state_dict(torch.load(str(MODEL_WEIGHTS_PATH), map_location=device))
        model.to(device)
        model.eval() 
    except Exception as e:
        print(f"⚠️ Failed to load model weights: {e}")
        return "moderate", 0.5

    # --- 4. Define Transformations ---
    IMAGE_SIZE = 224
    IMAGENET_MEAN = [0.485, 0.456, 0.406]
    IMAGENET_STD = [0.229, 0.224, 0.225]

    inference_transforms = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)), # Ensure tuple for resize
        transforms.CenterCrop(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    try:
        image = Image.open(IMAGE_TO_PREDICT).convert("RGB")
        input_tensor = inference_transforms(image).unsqueeze(0).to(device)
    except FileNotFoundError:
        print(f"Error: The file '{IMAGE_TO_PREDICT}' was not found.")
        return "unknown", 0.0

    # --- 5. Make a Prediction ---
    with torch.no_grad():
        if device.type == 'cuda':
            start_event = torch.cuda.Event(enable_timing=True)
            end_event = torch.cuda.Event(enable_timing=True)
            start_event.record()
            logits = model(input_tensor)
            end_event.record()
            torch.cuda.synchronize()
            inference_time_ms = start_event.elapsed_time(end_event)
        else:
            start_time = time.perf_counter()
            logits = model(input_tensor)
            end_time = time.perf_counter()
            inference_time_ms = (end_time - start_time) * 1000

    # --- 6. Interpret the Results ---
    predicted_class_id = logits.argmax(dim=-1).item()
    predicted_class_label = CLASS_LABELS[predicted_class_id]

    severity_ranges = {
        0: (0.0, 0.33),      # '01-minor'
        1: (0.33, 0.67),     # '02-moderate'
        2: (0.67, 1.0)       # '03-major'
    }
    
    min_severity, max_severity = severity_ranges[predicted_class_id]
    severity_score = round(random.uniform(min_severity, max_severity), 2)

    print(f"✅ Severity: {predicted_class_label} ({severity_score}) | Time: {inference_time_ms:.2f} ms")

    return predicted_class_label, severity_score

if __name__ == "__main__":
    # Test block
    print("Run via main workflow")