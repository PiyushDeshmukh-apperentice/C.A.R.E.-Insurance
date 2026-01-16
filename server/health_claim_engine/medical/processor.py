import os
import json
import pandas as pd
from .extraction_agent import ExtractionAgent
from .retrieval_engine import RetrievalEngine
from .decision_agent import DecisionAgent

# Ensure API Key is loaded
try:
    from ..config import GROQ_API_KEY
except ImportError:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def find_icd_database():
    """Helper to find the ICD database file."""
    candidates = [
        "2026-ICD-10-CM Codes.xlsx - Sheet1.csv",
        "2026-ICD-10-CM Codes.csv",
        "2026-ICD-10-CM Codes.xlsx",
        "icd10.csv"
    ]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    search_paths = [
        os.path.join(base_dir, "..", "data"),
        os.path.join(base_dir, "..", "..", "data"),
        os.path.join(os.getcwd(), "health_claim_engine", "data"),
        os.getcwd()
    ]
    for path in search_paths:
        if not os.path.exists(path):
            continue
        for filename in candidates:
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path):
                print(f"   [INFO] Found ICD Database at: {full_path}")
                return full_path
    return None

def flatten_ocr_data(raw_data):
    """
    Flattens the nested OCR output into a single layer dictionary.
    Includes mappings for specific OCR extractor keys.
    """
    # Start with basic patient info
    flat_data = raw_data.get("patient_info", {}).copy()
    
    # Legacy support (if data is already flat)
    if "documents" not in raw_data:
        flat_data.update(raw_data)
        return flat_data

    docs = raw_data["documents"]
    
    # Helper to safely merge fields
    def merge_from(doc_type, mapping):
        if doc_type in docs:
            data = docs[doc_type]
            for target_key, source_keys in mapping.items():
                # Allow source_keys to be a single string or a list of options
                if isinstance(source_keys, str):
                    source_keys = [source_keys]
                
                for key in source_keys:
                    val = data.get(key)
                    if val:
                        flat_data[target_key] = val
                        break

    # --- MAPPINGS (Updated to match your Extractor) ---
    
    # 1. Discharge Summary (The Golden Source)
    merge_from("discharge_summary", {
        "chief_complaint": "reason_for_admission",
        "diagnosis": ["final_diagnosis", "diagnosis"],
        "procedure_performed": ["procedures_performed", "procedure"],
        "medication_prescribed": ["medications_on_discharge", "medications"],
        "hospital_course": "hospital_course",
        "discharge_advice": "discharge_advice"
    })

    # 2. Pathology 
    merge_from("pathology_report", {
        "pathology_findings": ["results", "findings", "pathological_findings"],
    })

    # 3. Imaging
    merge_from("imaging_report", {
        "imaging_findings": "findings",
        "imaging_impression": ["impression", "conclusion"]
    })
    
    # 4. Admission Note
    merge_from("admission_note", {
        "medical_history": "medical_history",
        "initial_complaint": "chief_complaint"
    })

    # 5. Bill (Fixed keys)
    merge_from("bill", {
        # Check 'total', 'total_amount', or 'grand_total'
        "total_claimed_amount": ["total", "total_amount", "grand_total"]
    })

    # Ensure procedure_performed is a list (Adjudicator often expects a list)
    proc = flat_data.get("procedure_performed")
    if proc and isinstance(proc, str):
        flat_data["procedure_performed"] = [proc]
    
    return flat_data

def process_health_claim_with_engine(extracted_data, policy_name=None):
    # 1. Setup
    icd_file_path = find_icd_database()
    if not icd_file_path:
        raise FileNotFoundError("ICD Database not found.")
    
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing.")

    extractor = ExtractionAgent(GROQ_API_KEY)
    retriever = RetrievalEngine(icd_file_path)
    decider = DecisionAgent(GROQ_API_KEY)

    # 2. Load and Flatten Data
    print("   ... Loading and Flattening Medical Record")
    if isinstance(extracted_data, str) and os.path.exists(extracted_data):
        with open(extracted_data, 'r') as f:
            raw_record = json.load(f)
    else:
        raw_record = extracted_data

    # FLATTEN THE DATA
    patient_record = flatten_ocr_data(raw_record)

    # 3. Extraction
    print("   ... Extractor Agent Running")
    extraction_result = extractor.generate_queries(patient_record)
    search_queries = extraction_result.get("search_queries", [])
    primary_condition = extraction_result.get("primary_condition", "Unknown")

    # 4. Retrieval
    print(f"   ... Searching ICD codes for: {search_queries}")
    candidates = retriever.get_candidates(search_queries)

    # 5. Decision
    print("   ... Decision Agent Running")
    decision_result = decider.decide(patient_record, candidates, primary_condition)

    # 6. Final Payload
    final_output = {
        "decision": "PROCESSING",
        "confidence": decision_result.get("confidence_score", 0.0),
        "summary": decision_result.get("reasoning", ""),
        "diagnosis": {
            "icd_code": decision_result.get("selected_code"),
            "description": extraction_result.get("primary_condition", "Medical Condition")
        },
        "decision_reasons": [],
        "applied_clauses": [],
        "ignored_exclusions": [],
        "audit_reference_id": "PENDING",
        # Pass FLATTENED data to Adjudicator
        "patient_data": {
            **patient_record, 
            "extracted_risk_factors": extraction_result.get("risk_factors", []),
            "procedure_intent": extraction_result.get("procedure_intent", "Medical"),
            "final_icd": decision_result.get("selected_code")
        }
    }

    return final_output 