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


def create_claim_json(event_data=None):
    """
    Create claim JSON with user-provided event data
    If event_data is None, uses default values
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

    claim = {
        "event": event_data,

        "driver": {
            "name": "Amit Kulkarni",
            "age": 34,
            "gender": "male",
            "licensed": True,
            "experience_years": 12,
            "under_influence": False
        },

        # 🔑 IMPORTANT CHANGE IS HERE
        "vehicle": {
            "type": "private",      # matches policy eligibility
            "category": "car",      # matches vehicle dataset type
            "usage": "private"
        },

        "damage": {
            "type": "partial",
            "damaged_parts": [
                {
                    "part_name": "front_bumper",
                    "severity": 0.4
                },
                {
                    "part_name": "headlamp_left",
                    "severity": 0.7
                }
            ]
        },

        "policy": {
            "active": True
        }
    }

    return claim
