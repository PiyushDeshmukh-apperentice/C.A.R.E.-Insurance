import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import json
import pandas as pd
from .extraction_agent import ExtractionAgent
from .retrieval_engine import RetrievalEngine
from .decision_agent import DecisionAgent
from ..config import GROQ_API_KEY

def process_single_medical_record(json_file, save_to_file=True):
    """Process a single medical record and return ICD code"""
    # Load ICD database
    icd_db = pd.read_excel("health_claim_engine/data/2026-ICD-10-CM Codes.xlsx")
    
    print(f"Processing {json_file}...")
    try:
        with open(json_file, "r") as f:
            patient_data = json.load(f)

        # Step A: Extraction & Expansion
        agent_a = ExtractionAgent(GROQ_API_KEY)
        query_data = agent_a.generate_queries(patient_data)

        # Step B: Retrieval
        engine = RetrievalEngine(icd_db)
        candidates = engine.get_candidates(query_data['search_queries'])

        # Step C: Decision
        agent_c = DecisionAgent(GROQ_API_KEY)
        final_decision = agent_c.decide(patient_data, candidates, query_data['diagnoses'][0]['raw_text'] if query_data['diagnoses'] else "Unknown condition")

        result = {
            "patient_file": json_file,
            "diagnoses": query_data['diagnoses'],
            "search_queries": query_data['search_queries'],
            "icd_candidates": candidates,
            "final_icd": final_decision.get('selected_code'),
            "confidence": final_decision.get('confidence_score'),
            "reasoning": final_decision.get('reasoning')
        }
        
        print(f"  ICD: {result['final_icd']} (Confidence: {result['confidence']})")
        
        if save_to_file:
            # Save result
            output_data = {
                "records_processed": 1,
                "medical_records": [result]
            }

            with open("medical_icd.json", "w") as f:
                json.dump(output_data, f, indent=2)

            print(f"✅ Saved processed medical record to medical_icd.json")
        
        return result
        
    except Exception as e:
        print(f"  Error processing {json_file}: {e}")
        return None

def main():
    # For now, process the specific medical file
    medical_file = "extracted_data_20260103_171809.json"
    process_single_medical_record(medical_file)

if __name__ == "__main__":
    main()