import pandas as pd

REPLACEMENT_THRESHOLD = 0.6

# Cost multipliers for enhanced formula
LABOR_COST_MULTIPLIER = 0.25  # Labor is 25% of base repair cost
CRITICAL_PART_MULTIPLIER = 1.15  # 15% premium for critical parts
CUMULATIVE_DAMAGE_MULTIPLIER = 0.05  # Additional 5% per additional damaged part


def load_parts_dataset(vehicle_type):
    columns = ["vehicle_type", "category", "part_name", "repair_base_cost", "replace_cost", "critical_part"]
    if vehicle_type == "car":
        return pd.read_csv("car_parts_cost_master.csv", header=None, names=columns)
    elif vehicle_type == "bike":
        return pd.read_csv("bike_parts_cost_master.csv", header=None, names=columns)
    elif vehicle_type == "scooty":
        return pd.read_csv("scooty_parts_cost_master.csv", header=None, names=columns)
    else:
        raise ValueError("Unsupported vehicle type")


def calculate_repair_cost(base_repair_cost, severity, is_critical):
    """
    Nuanced repair cost calculation with multiple factors:
    - Base cost adjusted by severity
    - Labor cost proportional to damage severity
    - Critical part premium if applicable
    """
    # Progressive severity scaling (non-linear for higher damages)
    if severity < 0.2:
        severity_factor = severity * 0.8  # Lower costs for minor damage
    elif severity < 0.5:
        severity_factor = severity * 1.0  # Linear scaling for moderate damage
    else:
        severity_factor = 0.5 + (severity - 0.5) * 1.5  # Higher scaling for severe damage
    
    # Base repair cost adjusted by severity
    parts_cost = base_repair_cost * severity_factor
    
    # Labor cost (increases with severity - more damage = more labor needed)
    labor_cost = base_repair_cost * LABOR_COST_MULTIPLIER * severity
    
    # Total repair cost
    repair_total = parts_cost + labor_cost
    
    # Apply critical part multiplier if applicable
    if is_critical:
        repair_total *= CRITICAL_PART_MULTIPLIER
    
    return round(repair_total, 2)


def calculate_replacement_cost(replace_cost, is_critical, total_damaged_parts):
    """
    Nuanced replacement cost calculation:
    - Base replacement cost
    - Critical part premium
    - Cumulative damage factor (multiple parts damaged increases labor cost)
    """
    total = replace_cost
    
    # Apply critical part multiplier
    if is_critical:
        total *= CRITICAL_PART_MULTIPLIER
    
    # Additional labor/overhead for cumulative damage (only if multiple parts)
    if total_damaged_parts > 1:
        cumulative_factor = 1 + (CUMULATIVE_DAMAGE_MULTIPLIER * (total_damaged_parts - 1))
        total *= cumulative_factor
    
    return round(total, 2)


def estimate_part_cost(part, parts_df, total_damaged_parts=1):
    part_name = part["part_name"]
    severity = part["severity"]

    row = parts_df[parts_df["part_name"] == part_name]

    if row.empty:
        return {
            "part_name": part_name,
            "status": "UNKNOWN_PART",
            "estimated_cost": 0
        }

    row = row.iloc[0]
    is_critical = str(row["critical_part"]).lower() == "yes"
    
    # Dynamic threshold: critical parts have lower replacement threshold
    dynamic_threshold = REPLACEMENT_THRESHOLD - 0.1 if is_critical else REPLACEMENT_THRESHOLD

    if severity >= dynamic_threshold:
        cost = calculate_replacement_cost(
            float(row["replace_cost"]),
            is_critical,
            total_damaged_parts
        )
        action = "replace"
    else:
        cost = calculate_repair_cost(
            float(row["repair_base_cost"]),
            severity,
            is_critical
        )
        action = "repair"

    return {
        "part_name": part_name,
        "action": action,
        "severity": severity,
        "estimated_cost": cost,
        "critical_part": is_critical
    }


def estimate_total_cost(claim):
    vehicle_type = claim["vehicle"].get("category", claim["vehicle"].get("type"))
    parts_df = load_parts_dataset(vehicle_type)

    breakdown = []
    total_cost = 0
    critical_damage = False
    
    # Count total damaged parts for cumulative factor
    total_damaged_parts = len(claim["damage"]["damaged_parts"])

    for part in claim["damage"]["damaged_parts"]:
        result = estimate_part_cost(part, parts_df, total_damaged_parts)
        breakdown.append(result)
        total_cost += result["estimated_cost"]

        if result.get("critical_part"):
            critical_damage = True

    return {
        "vehicle_type": vehicle_type,
        "total_estimated_cost": round(total_cost, 2),
        "critical_damage_detected": critical_damage,
        "cost_breakdown": breakdown
    }
