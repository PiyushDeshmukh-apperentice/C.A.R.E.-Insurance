from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import re
import os
import json
from pathlib import Path
from datetime import datetime
from rapidfuzz import fuzz
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GEMMA_API")

# -------------------------------
# CONFIG
# -------------------------------
DIR_PATH = "/mnt/StorageHDD/AIRS/Dataset_AIRS&AICS/cancer/template2_documents_AGED/light/S0212-16112010000100017-1"  # default, will be overridden
OUTPUT_DIR = "extracted"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


DOCUMENT_TYPES = [
    "admission_note",
    "prescription",
    "imaging_report",
    "pathology_report",
    "discharge_summary",
    "bill",
    "insurance"
]

# -------------------------------
# FUZZY MATCH DOC TYPE
# -------------------------------
def get_doc_type(filename):
    filename_lower = filename.lower()
    best_match = max(DOCUMENT_TYPES, key=lambda t: fuzz.ratio(t, filename_lower))
    score = fuzz.ratio(best_match, filename_lower)
    return best_match if score > 50 else None

# -------------------------------
# OCR + LINE FLATTENING
# -------------------------------
def extract_lines(doc_path):
    model = ocr_predictor(pretrained=True)
    doc = DocumentFile.from_pdf(doc_path) if doc_path.endswith(".pdf") else DocumentFile.from_images(doc_path)
    result = model(doc)

    lines = []
    for page in result.pages:
        for block in page.blocks:
            for line in block.lines:
                text = " ".join([word.value for word in line.words]).strip()
                if text:
                    lines.append(text)
    return lines


# -------------------------------
# GLOBAL RULES
# -------------------------------
def normalize_key(text):
    text = text.lower()
    text = re.sub(r"[\/\-\_]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def apply_global_rules(lines):
    data = {
        "hospital_name": None,
        "patient_info": {},
        "doctor_name": None
    }

    # 1. Header: Hospital name
    hospital_keywords = ["hospital", "medical", "general", "institute"]
    for line in lines:
        if any(k in line.lower() for k in hospital_keywords):
            data["hospital_name"] = line
            header_index = lines.index(line)
            break
    else:
        header_index = 0

    # 2. Personal info (after header)
    personal_keywords = {
        "patient_name": ["patient"],
        "date": ["date: "],
        "age_gender": ["age", "gen"],
        "id": ["id", "patient id"],
        "address": ["addres"]
    }

    for line in lines[header_index + 1 : header_index + 15]:
        if ":" not in line:
            continue

        key_part, value_part = line.split(":", 1)
        key_norm = normalize_key(key_part)

        for field, keywords in personal_keywords.items():
            if any(k in key_norm for k in keywords):
                if value_part.strip():  # avoid empty values
                    data["patient_info"][field] = value_part.strip()

    # 3. Doctor name (global search)
    for line in lines:
        if "dr." in line.lower():
            data["doctor_name"] = line
            break

    return data

def normalize_heading(text):
    text = text.lower()
    text = re.sub(r"[\/]", " ", text)     # remove /
    text = re.sub(r"\s+", " ", text)      # collapse spaces
    return text.strip().replace(" ", "_")


# -------------------------------
# HELPER: EXTRACT TEXT BELOW HEADING
# -------------------------------
# def extract_below_heading(lines, heading, stop_headings=None):
#     collected = []
#     capture = False

#     for line in lines:
#         if heading.lower() in line.lower():
#             capture = True
#             continue

#         if capture:
#             if stop_headings and any(h.lower() in line.lower() for h in stop_headings):
#                 break
#             collected.append(line)

#     return " ".join(collected).strip()
def extract_below_heading(lines, heading, stop_headings=None):
    collected = []
    capture = False

    heading_norm = normalize_heading(heading)

    stop_norms = [normalize_heading(h) for h in stop_headings] if stop_headings else []

    for line in lines:
        line_norm = normalize_heading(line)

        if heading_norm in line_norm:
            capture = True
            continue

        if capture:
            if stop_norms and any(s in line_norm for s in stop_norms):
                break
            collected.append(line)

    return " ".join(collected).strip()



# -------------------------------
# DOCUMENT-SPECIFIC RULES
# -------------------------------
def admission_note_rules(lines):
    return {
        "chief_complaint": extract_below_heading(
            lines,
            "Chief complaint",
            stop_headings=["Medical history"]
        ),
        "medical_history": extract_below_heading(
            lines,
            "Medical history"
        )
    }


def prescription_rules(lines):
    return {
        "medications": extract_below_heading(lines, "Medications"),
        "tests_prescribed": extract_below_heading(lines, "Tests"),
        "imaging_prescribed": extract_below_heading(lines, "Imaging")
    }


def imaging_report_rules(lines):
    return {
        "findings": extract_below_heading(lines, "Findings"),
        "impression": extract_below_heading(lines, "Impression")
    }


def pathology_report_rules(lines):
    return {
        "results": extract_below_heading(lines, "Results"),
        "pathological_findings": extract_below_heading(lines, "Pathological Findings"),
    }


def discharge_summary_rules(lines):
    headings = [
        "Final Diagnosis",
        "Procedures Performed",
        "Hospital Course",
        "Medications on Discharge",
        "Condition / Remarks",
        "Discharge Advice"
    ]

    data = {}
    data["reason_for_admission"] = extract_below_heading(
        lines, "Reason for admission", headings
    )

    for h in headings:
        data[normalize_heading(h)] = extract_below_heading(
            lines, h, headings
        )

    return data


def bill_rules(lines):
    charges = {}
    items = ["Consultation", "Lab", "Imaging", "Meds", "Procedures", "Total"]

    for i, line in enumerate(lines):
        for item in items:
            if item.lower() in line.lower():
                if i + 1 < len(lines):
                    charges[item.lower()] = lines[i + 1]

    return charges


def insurance_rules(lines):
    return {
        "diagnosis": extract_below_heading(lines, "Diagnosis")
    }


# -------------------------------
# CONSISTENCY CHECKING
# -------------------------------
def get_full_text(data):
    # Concatenate all string values in the data dict
    texts = []
    for v in data.values():
        if isinstance(v, str):
            texts.append(v)
        elif isinstance(v, dict):
            texts.append(get_full_text(v))
    return " ".join(texts).strip()


def check_consistency_with_gemma(text1, text2, doc_type):
    # Configure API key - user needs to set this
    genai.configure(api_key=API_KEY)  # Replace with actual key
    model = genai.GenerativeModel('gemma-3-27b-it')  # Using Gemini as Gemma is not directly available, but assuming it's similar
    prompt = f"Are the medical information in these two texts consistent? Text 1 (discharge summary): {text1[:2000]} Text 2 ({doc_type}): {text2[:2000]}. Answer with Yes or No ONLY"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# -------------------------------
# MAIN DISPATCHER
# -------------------------------
def extract_document(doc_type, doc_path):
    if doc_type not in DOCUMENT_TYPES:
        raise ValueError("Invalid document type")

    lines = extract_lines(doc_path)

    result = {}
    result.update(apply_global_rules(lines))

    if doc_type == "admission_note":
        result.update(admission_note_rules(lines))
    elif doc_type == "prescription":
        result.update(prescription_rules(lines))
    elif doc_type == "imaging_report":
        result.update(imaging_report_rules(lines))
    elif doc_type == "pathology_report":
        result.update(pathology_report_rules(lines))
    elif doc_type == "discharge_summary":
        result.update(discharge_summary_rules(lines))
    elif doc_type == "bill":
        result.update(bill_rules(lines))
    elif doc_type == "insurance":
        result.update(insurance_rules(lines))

    return result


# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    DIR_PATH = input("Enter directory path containing documents: ").strip() or DIR_PATH

    extracted = {}
    for file in Path(DIR_PATH).iterdir():
        if file.is_file() and file.suffix.lower() in ['.pdf', '.jpg', '.png', '.jpeg']:
            doc_type = get_doc_type(file.stem)
            if doc_type:
                print(f"Processing {file.name} as {doc_type}")
                data = extract_document(doc_type, str(file))
                extracted[doc_type] = data
            else:
                print(f"Skipping {file.name}, no matching doc type")

    if not extracted:
        print("No documents processed.")
        exit()

    # Merge common fields
    common = {
        "hospital_name": None,
        "patient_info": {},
        "doctor_name": None
    }
    for data in extracted.values():
        if data["hospital_name"] and not common["hospital_name"]:
            common["hospital_name"] = data["hospital_name"]
        for k, v in data["patient_info"].items():
            if k not in common["patient_info"] or not common["patient_info"][k]:
                common["patient_info"][k] = v
        if data["doctor_name"] and not common["doctor_name"]:
            common["doctor_name"] = data["doctor_name"]

    # Documents with specific data
    documents = {}
    for dt, data in extracted.items():
        specific = {k: v for k, v in data.items() if k not in ["hospital_name", "patient_info", "doctor_name"]}
        specific["full_text"] = get_full_text(specific)
        documents[dt] = specific

    # Consistency checks
    consistency = {}

    # Patient info consistency
    patient_fields = ["patient_name", "age_gender", "address"]
    for field in patient_fields:
        values = [d["patient_info"].get(field) for d in extracted.values() if d["patient_info"].get(field)]
        unique_values = list(set(values))
        if len(unique_values) > 1:
            consistency[f"{field}_consistent"] = False
            consistency[f"{field}_values"] = unique_values
        else:
            consistency[f"{field}_consistent"] = True

    # Text consistency with discharge summary
    if "discharge_summary" in extracted:
        discharge_text = documents["discharge_summary"]["full_text"]
        text_types = ["prescription", "imaging_report", "pathology_report", "insurance"]
        for tt in text_types:
            if tt in documents:
                other_text = documents[tt]["full_text"]
                result = check_consistency_with_gemma(discharge_text, other_text, tt)
                consistency[f"{tt}_consistent_with_discharge"] = result

    # Final JSON
    final_data = {
        **common,
        "documents": documents,
        "consistency_checks": consistency
    }

    # Save to single JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(OUTPUT_DIR) / f"extracted_data_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print("\nExtraction and consistency check complete")
    print("Saved to:", output_path)

