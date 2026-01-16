def get_event_details_from_user():
    """
    Get event details from user input
    """
    print("\n" + "="*50)
    print("EVENT DETAILS INPUT")
    print("="*50)
    
    date = input("Enter event date (YYYY-MM-DD): ")
    time = input("Enter event time (HH:MM): ")
    activity = input("Enter activity type (e.g., road_accident, theft, vandalism): ")
    
    print("\nLocation Details:")
    street = input("Enter street name: ")
    city = input("Enter city: ")
    state = input("Enter state: ")
    
    event = {
        "date": date,
        "time": time,
        "activity": activity,
        "location": {
            "street": street,
            "city": city,
            "state": state
        }
    }
    
    return event

def load_damage_from_report(report_path="damage_report.json"):
    """Load damage data from JSON report (Legacy)"""
    import json
    import os
    
    default_damage = {
        "type": "partial",
        "damaged_parts": []
    }
    
    if os.path.exists(report_path):
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
                return report.get("damage", default_damage)
        except Exception:
            return default_damage
    return default_damage

def create_claim_json(event_data=None, driver_data=None):
    """
    Create claim JSON.
    Now accepts driver_data to prevent hardcoding.
    """
    # Use provided event data or default values
    if event_data is None:
        event_data = {
            "date": "2025-01-15",
            "time": "18:45",
            "activity": "road_accident",
            "location": {
                "street": "Baner Road",
                "city": "Pune",
                "state": "Maharashtra"
            }
        }

    # Use provided driver data OR fallback to default
    if driver_data is None:
        # Check if driver data is nested in event_data (common in API payload)
        if "driver" in event_data:
            driver_data = event_data["driver"]
            # Remove driver from event_data to keep structure clean
            event_data_clean = event_data.copy()
            del event_data_clean["driver"]
            event_data = event_data_clean
        else:
            driver_data = {
                "name": "Amit Kulkarni",
                "age": 34,
                "gender": "male",
                "licensed": True,
                "experience_years": 12,
                "under_influence": False
            }

    # Load default damage (will be overwritten by image processor later)
    damage_data = {
        "type": "unknown",
        "damaged_parts": []
    }

    claim = {
        "event": event_data,
        "driver": driver_data,
        "vehicle": {
            "type": "private",      
            "category": "car",      
            "usage": "private"
        },
        "damage": damage_data,
        "policy": {
            "active": True
        }
    }

    return claim