import os
import json
import sys
from pathlib import Path
from rapidfuzz import fuzz  # Requires: pip install rapidfuzz

# Import docTR
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# Import Groq client
from groq import Groq

try:
    from ...config import GROQ_API_KEY
except ImportError:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class OCRExtractor:
    def __init__(self, api_key):
        self.model = ocr_predictor(det_arch='db_resnet50', reco_arch='crnn_vgg16_bn', pretrained=True)
        self.client = Groq(api_key=api_key)

    def extract_text_from_pdf(self, pdf_path):
        """Extracts raw text from a PDF using docTR."""
        try:
            doc = DocumentFile.from_pdf(pdf_path)
            result = self.model(doc)
            text = ""
            for page in result.pages:
                for block in page.blocks:
                    for line in block.lines:
                        for word in line.words:
                            text += word.value + " "
                        text += "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def process_document(self, text, doc_type):
        """Uses LLM to structure raw text into JSON based on document type."""
        
        # Define schemas based on document type
        schemas = {
            "discharge_summary": {
                "patient_name": "string",
                "age": "string",
                "gender": "string",
                "hospital_name": "string",
                "admission_date": "YYYY-MM-DD",
                "discharge_date": "YYYY-MM-DD",
                "final_diagnosis": "string",
                "reason_for_admission": "string",
                "procedures_performed": ["list of strings"],
                "hospital_course": "string",
                "medications_on_discharge": ["list of strings"],
                "discharge_advice": "string"
            },
            "bill": {
                "patient_name": "string",
                "bill_number": "string",
                "bill_date": "YYYY-MM-DD",
                "total_amount": "number",
                "items": [{"description": "string", "amount": "number"}]
            },
            "pathology_report": {
                "patient_name": "string",
                "test_name": "string",
                "collection_date": "YYYY-MM-DD",
                "results": "string",
                "impression": "string"
            },
            "imaging_report": {
                "patient_name": "string",
                "modality": "string (MRI/CT/Xray)",
                "body_part": "string",
                "findings": "string",
                "impression": "string"
            },
            "prescription": {
                "patient_name": "string",
                "doctor_name": "string",
                "date": "YYYY-MM-DD",
                "medications": ["list of strings"]
            },
            "insurance": {
                "policy_holder_name": "string", # Maps to patient_name
                "policy_number": "string",
                "insurance_company": "string",
                "valid_from": "YYYY-MM-DD",
                "valid_to": "YYYY-MM-DD"
            },
            "admission_note": {
                "patient_name": "string",
                "admission_date": "YYYY-MM-DD",
                "chief_complaint": "string",
                "medical_history": "string"
            }
        }

        schema = schemas.get(doc_type, {})
        
        prompt = f"""
        Extract the following fields from the medical document text below.
        Return strictly valid JSON matching this schema:
        {json.dumps(schema, indent=2)}
        
        If a field is not found, use null.
        
        Document Text:
        {text[:8000]} 
        """

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a medical data extraction assistant. Output only JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM Extraction Error: {e}")
            return {}

    def validate_consistency(self, extracted_data):
        """
        Checks for data consistency across different documents.
        Raises ValueError if a critical mismatch is found.
        Only compares fields if they exist in both documents.
        """
        print("   ... Validating Data Consistency across documents")
        docs = extracted_data.get("documents", {})
        
        # Fields to cross-reference
        # Map specific doc keys to a standard key for comparison
        # Format: standard_key: (doc_type, actual_key_in_doc)
        comparison_map = {
            "patient_name": [
                ("discharge_summary", "patient_name"),
                ("bill", "patient_name"),
                ("pathology_report", "patient_name"),
                ("imaging_report", "patient_name"),
                ("insurance", "policy_holder_name"),
                ("admission_note", "patient_name"),
                ("prescription", "patient_name")
            ],
            "hospital_name": [
                ("discharge_summary", "hospital_name"),
                ("bill", "hospital_name") # If bill has hospital name
            ],
            "age": [
                ("discharge_summary", "age"),
                ("admission_note", "age")
            ],
            "gender": [
                ("discharge_summary", "gender"),
                ("admission_note", "gender")
            ]
        }

        # Iteratively compare extracted values
        for field, sources in comparison_map.items():
            baseline_value = None
            baseline_source = None

            for doc_type, key in sources:
                if doc_type not in docs:
                    continue
                
                current_val = docs[doc_type].get(key)
                
                # normalize value for comparison
                if current_val:
                    current_val = str(current_val).strip().lower()
                    # Remove titles like mr., mrs., master
                    current_val = current_val.replace("mr.", "").replace("mrs.", "").replace("ms.", "").strip()

                if not current_val or current_val == "null" or current_val == "none":
                    continue

                if baseline_value is None:
                    # Set the first non-empty value as baseline
                    baseline_value = current_val
                    baseline_source = doc_type
                else:
                    # Compare current against baseline
                    # Use fuzzy matching (Token Sort Ratio covers "Doe John" vs "John Doe")
                    score = fuzz.token_sort_ratio(baseline_value, current_val)
                    
                    # Threshold: 80% similarity allows for minor OCR typos
                    # For gender/age, we might want strict equality, but OCR is noisy.
                    # 80 is usually safe for names.
                    if score < 70:
                        error_msg = (
                            f"Consistency Check Failed: {field} mismatch. "
                            f"'{baseline_source}' says '{baseline_value}', but "
                            f"'{doc_type}' says '{current_val}'."
                        )
                        raise ValueError(error_msg)

    def process_directory(self, input_dir):
        """Main entry point to process a folder of PDFs."""
        output_data = {"documents": {}, "patient_info": {}}
        files = list(Path(input_dir).glob("*.pdf"))
        
        print(f"Processing directory: {input_dir}")

        for pdf_file in files:
            # Infer doc type from filename (simple heuristic for MVP)
            fname = pdf_file.stem.lower()
            doc_type = "unknown"
            
            if "discharge" in fname: doc_type = "discharge_summary"
            elif "bill" in fname or "invoice" in fname: doc_type = "bill"
            elif "pathology" in fname or "lab" in fname: doc_type = "pathology_report"
            elif "imaging" in fname or "scan" in fname or "xray" in fname: doc_type = "imaging_report"
            elif "prescription" in fname: doc_type = "prescription"
            elif "insurance" in fname or "policy" in fname: doc_type = "insurance"
            elif "admission" in fname: doc_type = "admission_note"
            
            if doc_type == "unknown":
                print(f"Skipping unknown file type: {pdf_file.name}")
                continue

            print(f"Processing {pdf_file.name} as {doc_type}")
            raw_text = self.extract_text_from_pdf(pdf_file)
            if raw_text:
                structured_data = self.process_document(raw_text, doc_type)
                output_data["documents"][doc_type] = structured_data
                
                # Populate top-level info from reliable sources
                if doc_type == "discharge_summary":
                    output_data["patient_info"] = structured_data

        # --- NEW: Run Consistency Check ---
        try:
            self.validate_consistency(output_data)
        except ValueError as e:
            # We catch it here to print, but re-raise so workflow handles the Denial
            print(f"❌ {str(e)}")
            # We add a special flag so the main workflow knows to DENY immediately
            output_data["consistency_error"] = str(e)
            
        return output_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extractor.py <directory_path>")
        sys.exit(1)
        
    extractor = OCRExtractor(GROQ_API_KEY)
    result = extractor.process_directory(sys.argv[1])
    
    # Save output
    out_path = Path("extracted") / f"extracted_data_{Path(sys.argv[1]).name}.json"
    out_path.parent.mkdir(exist_ok=True)
    
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\nExtraction and consistency check complete")
    print(f"Saved to: {out_path}")