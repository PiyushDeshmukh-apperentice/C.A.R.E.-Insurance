import json
import os
import sys
from pathlib import Path

# Add the automobile_claim_engine directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from claim_input import create_claim_json
from evaluator import evaluate_policy
from cost_estimator import estimate_total_cost
from overlay import process_car_image


def process_automobile_claim(event_data=None, driver_data=None, vehicle_type="car", image_path=None):
    """
    Process automobile claim with given event data, vehicle type, and car image
    """
    # Load policy JSON
    policy_path = os.path.join(os.path.dirname(__file__), "data", "policy.json")
    with open(policy_path, "r") as f:
        policy = json.load(f)

    # Generate claim JSON with provided data (Pass driver_data here!)
    claim = create_claim_json(event_data, driver_data)
    
    # Override vehicle type if specified
    if vehicle_type:
        claim["vehicle"]["category"] = vehicle_type

    # Process car image if provided
    image_result = None
    if image_path and os.path.exists(image_path):
        print(f"🖼️ Processing car image: {image_path}")
        try:
            # Determine output directory (same as vehicle image)
            output_dir = os.path.dirname(image_path) or "."
            
            image_result = process_car_image(image_path, vehicle_type,output_dir)
            
            # Merge damage data into claim
            if image_result and "damage_data" in image_result:
                claim["damage"] = image_result["damage_data"]
                print(f"✅ Damage data extracted: {image_result['damage_data']['type']}")
        except Exception as e:
            print(f"⚠️ Image processing failed (non-fatal): {str(e)}")
            import traceback
            traceback.print_exc()
            print("Continuing with default damage data...")
    else:
        print("⚠️ No image path provided, using default damage data")

    # Step 1: Policy eligibility evaluation
    policy_decision = evaluate_policy(policy, claim)

    # Step 2: Cost estimation (only if policy is active)
    if policy_decision["decision"] == "APPROVED":
        cost_estimate = estimate_total_cost(claim)
    else:
        cost_estimate = {
            "total_estimated_cost": 0,
            "cost_breakdown": [],
            "remarks": "Claim rejected due to policy conditions"
        }

    # Final consolidated output
    final_result = {
        "policy_decision": policy_decision,
        "cost_estimation": cost_estimate
    }

    return claim, final_result, image_result

def main():
    # For standalone testing
    claim, final_result, image_result = process_automobile_claim(image_path="car.jpg")

    # Output
    print("\n================ CLAIM DATA ================\n")
    print(json.dumps(claim, indent=2))

    print("\n================ FINAL DECISION ================\n")
    print(json.dumps(final_result, indent=2))
    
    if image_result:
        print("\n================ IMAGE PROCESSING RESULT ================\n")
        print(f"Output Image: {image_result['output_image_path']}")
        print(f"Damage Data: {json.dumps(image_result['damage_data'], indent=2)}")


if __name__ == "__main__":
    main()
