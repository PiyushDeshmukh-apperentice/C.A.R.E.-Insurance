import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import subprocess

# --- FIX: Import the NEW function from your rectified processor.py ---
from .medical.processor import process_health_claim_with_engine
from .policy.processor import parse_single_policy
from .adjudication.adjudicator import ClaimAdjudicator, load_policy_data

class ClaimAutomationWorkflow:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.output_dir = Path.cwd() / "health_claim_engine" / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_ocr(self, input_directory: str) -> str:
        """Run OCR on input directory and return the extracted JSON file"""
        print("🔍 Running OCR on documents...")
        # Run the OCR extractor script
        # Ensure the path to extractor.py is correct relative to where you run python
        command = ["python", "health_claim_engine/ocr/extractor.py", input_directory]
        try:
            subprocess.run(command, check=True, cwd=os.getcwd())
            # Find the latest output file in extracted/
            extracted_dir = Path("extracted")
            if extracted_dir.exists():
                output_files = list(extracted_dir.glob("extracted_data_*.json"))
                if output_files:
                    latest = max(output_files, key=lambda p: p.stat().st_mtime)
                    return str(latest)
            return None
        except subprocess.CalledProcessError as e:
            print(f"❌ OCR failed: {e}")
        return None

    def process_medical_records(self, extracted_json: str) -> Dict:
        """Process medical record through the NEW medical pipeline"""
        print("🏥 Processing medical record with Rectified Engine...")
        
        # --- FIX: Use the new engine function ---
        # This uses the new Extraction -> Retrieval -> Decision agents we just fixed
        record = process_health_claim_with_engine(extracted_json)
        
        return record

    def check_policy_parsed(self, policy_name: str) -> bool:
        """Check if policy is already parsed"""
        policy_file = Path("health_claim_engine/data/parsed_policies.json")
        if not policy_file.exists():
            return False
        try:
            with open(policy_file, "r") as f:
                data = json.load(f)
            # Simple check if filenames match
            return os.path.basename(data.get("policy_file", "")) == os.path.basename(policy_name)
        except:
            return False

    def parse_policy_if_needed(self, policy_path: str):
        """Parse policy if not already done"""
        if not self.check_policy_parsed(policy_path):
            print("📄 Parsing policy document...")
            parse_single_policy(policy_path)
        else:
            print("✅ Policy already parsed.")

    def run_adjudication(self, medical_record: Dict, policy_data: Dict) -> Dict:
        """Run claim adjudication"""
        print("⚖️ Running claim adjudication...")
        adjudicator = ClaimAdjudicator()
        
        # The new processor returns 'patient_data' inside the result
        # We need to extract that to pass to the adjudicator
        patient_data_for_adj = medical_record.get('patient_data', {})
        
        # We also need to inject the Final ICD from the Decision Agent
        patient_data_for_adj['final_icd'] = medical_record.get('diagnosis', {}).get('icd_code')
        
        result = adjudicator.adjudicate_claim(patient_data_for_adj, policy_data['clauses'])
        
        return {
            "medical_record": medical_record,
            "adjudication": {
                "decision": result.decision.value,
                "reason": result.reason,
                "covered_components": result.covered_components,
                "excluded_components": result.excluded_components,
                "confidence_score": result.confidence_score
            }
        }

    def save_results(self, result: Dict, timestamp: str):
        """Save final result"""
        output_file = self.output_dir / f"adjudication_result_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"💾 Result saved to {output_file}")

    def run_workflow(self, input_directory: str, policy_path: str):
        """Main workflow execution"""
        print("🚀 WORKFLOW STARTED")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Step 1: OCR
        extracted_json = self.run_ocr(input_directory)
        if not extracted_json:
            print("❌ OCR failed. Aborting.")
            return

        # Step 2: Medical Pipeline (Updated)
        medical_record = self.process_medical_records(extracted_json)
        if not medical_record:
            print("❌ Failed to process medical record. Aborting.")
            return
        # Step 2: Medical Pipeline
        # Load the JSON to check for OCR Consistency errors FIRST
        with open(f"extracted/extracted_data_{Path(input_directory).name}.json", "r") as f:
            ocr_data = json.load(f)
            
        if "consistency_error" in ocr_data:
            print(f"❌ Consistency Error Detected: {ocr_data['consistency_error']}")
            final_result = {
                "adjudication": {
                    "decision": "denied",
                    "reason": f"Data Mismatch: {ocr_data['consistency_error']}",
                    "confidence_score": 1.0,
                    "covered_components": [],
                    "excluded_components": ["Patient/Hospital Information Mismatch"]
                }
            }
            self.save_results(final_result, timestamp)
            return final_result

        # If no error, proceed as normal
        medical_record = self.process_medical_records(extracted_json)
  
        # Step 3: Policy Check/Parse
        self.parse_policy_if_needed(policy_path)

        # Step 4: Load Policy
        policy_data = load_policy_data()

        # Step 5: Adjudication
        result = self.run_adjudication(medical_record, policy_data)

        # Step 6: Save Results
        self.save_results(result, timestamp)

        print("✅ Workflow completed successfully!")
        return result

def main():
    if len(sys.argv) != 3:
        print("Usage: python -m health_claim_engine.main_workflow <input_directory> <policy_pdf>")
        return

    input_dir = sys.argv[1]
    policy_pdf = sys.argv[2]

    try:
        from .config import GROQ_API_KEY
    except ImportError:
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    workflow = ClaimAutomationWorkflow(GROQ_API_KEY)
    workflow.run_workflow(input_dir, policy_pdf)

if __name__ == "__main__":
    main()