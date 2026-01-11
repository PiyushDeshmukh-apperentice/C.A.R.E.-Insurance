def match_condition(condition, claim):
    for key, expected in condition.items():
        keys = key.split(".")
        value = claim

        for k in keys:
            if k not in value:
                return False
            value = value[k]

        if isinstance(expected, list):
            if value not in expected:
                return False
        else:
            if value != expected:
                return False

    return True


def evaluate_parts_coverage(policy, damaged_parts):
    covered = []
    not_covered = []

    policy_covered_parts = policy["coverage"]["covered_parts"]
    policy_excluded_parts = policy["coverage"]["excluded_parts"]

    for part in damaged_parts:
        part_name = part["part_name"]  # 🔑 FIX

        if part_name in policy_covered_parts:
            covered.append(part_name)
        elif part_name in policy_excluded_parts:
            not_covered.append(part_name)
        else:
            not_covered.append(part_name)

    return covered, not_covered


def evaluate_policy(policy, claim):
    # 1️⃣ Policy active check
    if not claim["policy"]["active"]:
        return {
            "decision": "DENIED",
            "reason": "Policy is not active"
        }

    # 2️⃣ Vehicle eligibility
    if claim["vehicle"]["type"] not in policy["vehicle_eligibility"]["allowed_types"]:
        return {
            "decision": "DENIED",
            "reason": "Vehicle type not eligible"
        }
    
    if "category" in claim["vehicle"]:
        if claim["vehicle"]["category"] not in policy["vehicle_eligibility"]["allowed_categories"]:
            return {
                "decision": "DENIED",
                "reason": "Vehicle category not eligible"
            }


    # 3️⃣ Exclusions
    exclusions = sorted(
        policy.get("exclusions", []),
        key=lambda x: x.get("priority", 0),
        reverse=True
    )

    for rule in exclusions:
        if match_condition(rule["when"], claim):
            return {
                "decision": "DENIED",
                "reason": f"Matched exclusion rule: {rule['rule_id']}"
            }

    # 4️⃣ Event coverage
    if claim["event"]["activity"] not in policy["incident_conditions"]["allowed_activities"]:
        return {
            "decision": "DENIED",
            "reason": "Event not covered under policy"
        }

    # 5️⃣ Parts coverage
    damaged_parts = claim["damage"]["damaged_parts"]
    covered_parts, not_covered_parts = evaluate_parts_coverage(policy, damaged_parts)

    decision = "APPROVED" if covered_parts else "DENIED"

    return {
        "decision": decision,
        "covered_parts": covered_parts,
        "not_covered_parts": not_covered_parts,
        "remarks": "Partial claim approved" if not_covered_parts else "All parts covered"
    }
