import json
from claim_input import create_claim_json
from evaluator import evaluate_policy
from cost_estimator import estimate_total_cost


def main():
    # Load policy JSON
    with open("policy.json", "r") as f:
        policy = json.load(f)

    # Generate claim JSON
    claim = create_claim_json()

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

    # Output
    print("\n================ CLAIM DATA ================\n")
    print(json.dumps(claim, indent=2))

    print("\n================ FINAL DECISION ================\n")
    print(json.dumps(final_result, indent=2))


if __name__ == "__main__":
    main()
