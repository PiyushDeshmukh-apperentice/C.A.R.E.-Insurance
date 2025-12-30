from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import re
import json
from pathlib import Path
from datetime import datetime


# -------------------------------
# CONFIG
# -------------------------------
DOC_PATH = "/mnt/StorageHDD/AIRS/digestive_disease/template2_documents_AGED/light/S0212-71992007000700008-1/4_pathology.pdf"
OUTPUT_DIR = "extracted_json"
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
        "date": ["date"],
        "age_gender": ["age", "gen"],
        "id": ["id", "patient id"],
        "address": ["address"]
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
# MAIN DISPATCHER
# -------------------------------
def extract_document(doc_type):
    if doc_type not in DOCUMENT_TYPES:
        raise ValueError("Invalid document type")

    lines = extract_lines(DOC_PATH)

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
    print("Choose document type:")
    for d in DOCUMENT_TYPES:
        print("-", d)

    doc_type = input("Enter document type: ").strip()
    extracted_data = extract_document(doc_type)

    # Build output filename
    doc_name = Path(DOC_PATH).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(OUTPUT_DIR) / f"{doc_name}_{doc_type}_.json"

    # Save JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)

    print("\nExtraction complete")
    print("Saved to:", output_path)

