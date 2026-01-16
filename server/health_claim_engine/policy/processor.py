import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import json
import pandas as pd
import time
from .policy_parser import PolicyParser
from ..config import GROQ_API_KEY

def parse_single_policy(pdf_path, save_to_file=True):
    """Parse a single policy PDF and return clauses"""
    # Load ICD database
    icd_db = pd.read_excel("health_claim_engine/data/2026-ICD-10-CM Codes.xlsx")
    
    print(f"Processing {pdf_path}...")
    try:
        parser = PolicyParser(GROQ_API_KEY)
        clauses = parser.parse_policy(pdf_path, icd_db)
        print(f"  ✅ Extracted {len(clauses)} clauses")
        
        # Save results
        result = {
            "policy_file": pdf_path,
            "total_clauses": len(clauses),
            "clauses": clauses
        }
        
        if save_to_file:
            with open("health_claim_engine/data/parsed_policies.json", "w") as f:
                json.dump(result, f, indent=2)
            
            print(f"✅ Saved {len(clauses)} clauses to parsed_policies.json")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Error processing {pdf_path}: {e}")
        return None

def main():
    # For now, process the specific policy file
    policy_file = "20241122 - CIS - ASP.pdf"
    parse_single_policy(policy_file)

if __name__ == "__main__":
    main()