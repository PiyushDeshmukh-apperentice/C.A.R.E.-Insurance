import json
import os
from datetime import datetime
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
API = os.getenv("API")
genai.configure(api_key=API)

fake = Faker()

# ----------------------------------------------------------------
# CONSTANT DOCTOR, PATIENT, DATE (shared across all documents)
# ----------------------------------------------------------------
DOCTOR_NAME = fake.name()
PATIENT_NAME = fake.name()
REPORT_DATE = datetime.today().strftime("%d-%m-%Y")

# ----------------------------------------------------------------
# GEMMA HELPER
# ----------------------------------------------------------------
def gemma_format(prompt):
    model = genai.GenerativeModel("gemma-3-27b-it")
    res = model.generate_content(prompt)
    return res.text.strip()

# ----------------------------------------------------------------
# PDF GENERATOR BASE
# ----------------------------------------------------------------
def create_pdf(filename, elements):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        topMargin=40, bottomMargin=40,
        leftMargin=40, rightMargin=40
    )
    doc.build(elements)

# ----------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------
def header(title):
    styles = getSampleStyleSheet()
    h = Paragraph(f"<b><font size=16>{title}</font></b>", styles["Title"])
    return [h, Spacer(1, 20)]

# ----------------------------------------------------------------
# 1. Doctor Prescription
# ----------------------------------------------------------------
def generate_doctor_prescription(info, out_path):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    prompt = f"""
Create a short doctor prescription based ONLY on this info:

{json.dumps(info, indent=2)}

Do NOT add hallucinations.
Include: complaint, diagnosis, medication instructions, caution notes.
"""

    text = gemma_format(prompt)

    elements = header("Doctor Prescription")

    elements += [
        Paragraph(f"<b>Doctor:</b> {DOCTOR_NAME}", body),
        Paragraph(f"<b>Patient:</b> {PATIENT_NAME}", body),
        Paragraph(f"<b>Date:</b> {REPORT_DATE}", body),
        Spacer(1, 20),
        Paragraph(text.replace("\n", "<br/>"), body),
    ]

    create_pdf(out_path, elements)

# ----------------------------------------------------------------
# 2. Diagnostic Test Prescription
# ----------------------------------------------------------------
def generate_test_prescription(info, out_path):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    tests = info.get("lab_tests", "Not Specified").split(",")
    table_data = [["Test Name"]] + [[t.strip()] for t in tests]

    table = Table(table_data, colWidths=[400])
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,0),colors.lightgrey),
        ('GRID',(0,0),(-1,-1),1,colors.black),
    ]))

    elements = header("Diagnostic Test Prescription")

    elements += [
        Paragraph(f"<b>Ordered By:</b> {DOCTOR_NAME}", body),
        Paragraph(f"<b>Patient:</b> {PATIENT_NAME}", body),
        Spacer(1, 20),
        Paragraph("Recommended Tests:", body),
        Spacer(1, 10),
        table
    ]

    create_pdf(out_path, elements)

# ----------------------------------------------------------------
# 3. Pathology Report (Biopsy)
# ----------------------------------------------------------------
def generate_pathology_report(info, out_path):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    biopsy = info.get("procedure_outcome", "Not Specified")

    prompt = f"Format this biopsy info professionally:\n{biopsy}"
    text = gemma_format(prompt)

    elements = header("Pathology Report (Biopsy Result)")
    elements += [
        Paragraph(f"<b>Patient:</b> {PATIENT_NAME}", body),
        Paragraph(f"<b>Date:</b> {REPORT_DATE}", body),
        Spacer(1, 20),
        Paragraph(text.replace("\n","<br/>"), body),
    ]

    create_pdf(out_path, elements)

# ----------------------------------------------------------------
# 4. Imaging Report (CT/MRI/X-ray)
# ----------------------------------------------------------------
def generate_imaging_report(info, out_path):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    imaging = info.get("imaging_report", "No imaging reported")

    prompt = f"""
Convert this imaging information into a structured radiology report:

{imaging}
"""
    text = gemma_format(prompt)

    elements = header("Imaging Report")
    elements += [
        Paragraph(f"<b>Patient:</b> {PATIENT_NAME}", body),
        Spacer(1, 10),
        Paragraph(text.replace("\n","<br/>"), body),
    ]

    create_pdf(out_path, elements)

# ----------------------------------------------------------------
# 5. Hospital Admission Note
# ----------------------------------------------------------------
def generate_admission_note(info, out_path):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    prompt = f"Create a structured admission note from:\n{json.dumps(info,indent=2)}"
    text = gemma_format(prompt)

    elements = header("Hospital Admission Note")
    elements += [
        Paragraph(text.replace("\n","<br/>"), body)
    ]
    create_pdf(out_path, elements)

# ----------------------------------------------------------------
# 6. Surgery / Procedure Note
# ----------------------------------------------------------------
def generate_procedure_note(info, out_path):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    procedure = info.get("medical_procedure", "Not Specified")

    prompt = f"Convert this into a neat procedure note:\n{procedure}"
    text = gemma_format(prompt)

    elements = header("Surgery / Procedure Note")
    elements += [
        Paragraph(text.replace("\n","<br/>"), body)
    ]

    create_pdf(out_path, elements)

# ----------------------------------------------------------------
# 7. Hospital Discharge Summary
# ----------------------------------------------------------------
def generate_discharge_summary(info, out_path):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    prompt = f"Format a full discharge summary from:\n{json.dumps(info,indent=2)}"
    text = gemma_format(prompt)

    elements = header("Hospital Discharge Summary")
    elements += [
        Paragraph(text.replace("\n","<br/>"), body)
    ]

    create_pdf(out_path, elements)

# ----------------------------------------------------------------
# 8. Hospital Bill Summary
# ----------------------------------------------------------------
def generate_bill_summary(info, out_path):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    table_data = [
        ["Service", "Cost"],
        ["Consultation", "₹500"],
        ["Lab Tests", "₹1200"],
        ["Imaging", "₹2500"],
        ["Medications", "₹850"],
        ["Procedure", "₹4000"],
        ["Total", "₹9050"],
    ]

    table = Table(table_data, colWidths=[300,100])
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(1,0),colors.lightgrey),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ]))

    elements = header("Hospital Billing Summary")
    elements += [
        Paragraph(f"<b>Patient:</b> {PATIENT_NAME}", body),
        Spacer(1, 20),
        table
    ]

    create_pdf(out_path, elements)

# ----------------------------------------------------------------
# 9. Insurance Claim Supporting Document
# ----------------------------------------------------------------
def generate_insurance_doc(info, out_path):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    prompt = f"Produce a short insurance justification from:\n{json.dumps(info,indent=2)}"
    text = gemma_format(prompt)

    elements = header("Insurance Claim Supporting Document")
    elements += [
        Paragraph(text.replace("\n","<br/>"), body)
    ]

    create_pdf(out_path, elements)

# ----------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------
def main():
    json_path = "/mnt/StorageHDD/PICT/medical_info_extracted/S0004-06142005001000011-3.json"
    output_folder = "/mnt/StorageHDD/PICT/medical_documents"
    os.makedirs(output_folder, exist_ok=True)

    info = json.load(open(json_path))

    generate_doctor_prescription(info, f"{output_folder}/S0004-06142005001000011-3doctor_prescription.pdf")
    generate_test_prescription(info, f"{output_folder}/S0004-06142005001000011-3test_prescription.pdf")
    generate_pathology_report(info, f"{output_folder}/S0004-06142005001000011-3pathology_report.pdf")
    generate_imaging_report(info, f"{output_folder}/S0004-06142005001000011-3imaging_report.pdf")
    generate_admission_note(info, f"{output_folder}/S0004-06142005001000011-3admission_note.pdf")
    generate_procedure_note(info, f"{output_folder}/S0004-06142005001000011-3procedure_note.pdf")
    generate_discharge_summary(info, f"{output_folder}/S0004-06142005001000011-3discharge_summary.pdf")
    generate_bill_summary(info, f"{output_folder}/S0004-06142005001000011-3billing_summary.pdf")
    generate_insurance_doc(info, f"{output_folder}/S0004-06142005001000011-3insurance_document.pdf")

    print("\n✔ All 9 PDFs generated successfully!")

if __name__ == "__main__":
    main()
