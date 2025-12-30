import json
import csv
from datetime import datetime, timedelta
from faker import Faker
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Flowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String

fake = Faker()

# ============================================================
#  Custom Placeholder Hospital Logo (Vector)
# ============================================================
class PlaceholderLogo(Flowable):
    def __init__(self, width=80, height=40):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        self.canv.rect(0, 0, self.width, self.height)
        self.canv.setFont("Helvetica-Bold", 10)
        self.canv.drawCentredString(self.width / 2, self.height / 2 - 3, "LOGO")


# ============================================================
#  ICD CSV Loader
# ============================================================
def load_icd_map(csv_path):
    icd_map = {}
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_id = row["filename"].replace(".txt", "").strip()
            icd_map[file_id] = {
                "main_icd": row.get("main_icd", "Not specified"),
                "procedure_icd": row.get("procedure_icd", "Not specified"),
            }
    return icd_map


# ============================================================
#  Uniform Professional Header (Layout A)
# ============================================================
def header(title, hospital_name, patient_name):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "header_title",
        parent=styles["Heading1"],
        fontSize=16,
        alignment=TA_CENTER,
        leading=18,
        spaceAfter=6
    )

    patient_style = ParagraphStyle(
        "patient_info",
        parent=styles["BodyText"],
        fontSize=11,
        alignment=TA_CENTER
    )

    d = Drawing(500, 50)
    d.add(Rect(0, 0, 500, 50, strokeColor=colors.black, fillColor=None))
    d.add(String(250, 30, hospital_name, fontSize=16, textAnchor="middle"))
    d.add(String(250, 10, "Official Medical Document", fontSize=10, textAnchor="middle"))

    return [
        d,
        Spacer(1, 10),
        Paragraph(f"<b>{title}</b>", title_style),
        Spacer(1, 4),
    ]


# ============================================================
#  Universal PDF Builder
# ============================================================
def create_pdf(path, elements):
    path = str(path)
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        topMargin=40, bottomMargin=40,
        leftMargin=50, rightMargin=50
    )
    doc.build(elements)


# ============================================================
#  DATE UTILITIES
# ============================================================
def format_date(dt):
    return dt.strftime("%d-%m-%Y")


# ============================================================
# DOCUMENT GENERATORS
# ============================================================

def doc_admission(info, icd, out_path, patient, doctor, admit_date):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    elements = header("Admission Note", patient["hospital"], patient["name"])

    elements += [
        Paragraph(f"<b>Patient Name:</b> {patient['name']}", body),
        Paragraph(f"<b>Age:</b> {info['age']}", body),
        Paragraph(f"<b>Gender:</b> {info['gender']}", body),
        Paragraph(f"<b>Date of Admission:</b> {format_date(admit_date)}", body),
        Spacer(1, 10),
        Paragraph(f"<b>Chief Complaint:</b> {info['chief_complaint']}", body),
        Paragraph(f"<b>Past Medical History:</b> {info['medical_history']}", body),
    ]

    create_pdf(out_path, elements)


def doc_prescription(info, icd, out_path, patient, doctor, date):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    tests = info.get("pathalogy_test_prescribed_by_the_doctor_only_the_test_name", [])
    imaging = info.get("imaging_exams_prescribed", [])

    elements = header("Doctor Prescription", patient["hospital"], patient["name"])

    elements += [
        Paragraph(f"<b>Patient:</b> {patient['name']}", body),
        Paragraph(f"<b>Age:</b> {info['age']}", body),
        Paragraph(f"<b>Gender:</b> {info['gender']}", body),
        Paragraph(f"<b>Date:</b> {format_date(date)}", body),
        Paragraph(f"<b>Doctor:</b> {doctor}", body),
        Spacer(1, 10),
        Paragraph(f"<b>Medication Prescribed:</b> {info['medication_prescribed_with_dosage']}", body),
        Spacer(1, 10),
        Paragraph("<b>Lab Tests Prescribed:</b>", body),
    ]

    for t in tests:
        elements.append(Paragraph(f"• {t}", body))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Imaging Exams Prescribed:</b>", body))

    for i in imaging:
        elements.append(Paragraph(f"• {i}", body))

    create_pdf(out_path, elements)


def doc_imaging(info, icd, out_path, patient, date):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    imaging = info.get("imaging_exams_prescribed", ["Imaging exam"])

    elements = header("Imaging Report", patient["hospital"], patient["name"])

    findings = info.get('findings_of_imaging_report', [])
    if isinstance(findings, list):
        findings = ', '.join(findings) if findings else 'Not specified'
    
    impressions = info.get('impressions_from_the_imaging_report', [])
    if isinstance(impressions, list):
        impressions = ', '.join(impressions) if impressions else 'Not specified'

    elements += [
        Paragraph(f"<b>Patient Name:</b> {patient['name']}", body),
        Paragraph(f"<b>Age:</b> {info['age']}", body),
        Paragraph(f"<b>Gender:</b> {info['gender']}", body),
        Paragraph(f"<b>Date:</b> {format_date(date)}", body),
        Spacer(1, 10),
        Paragraph(f"<b>Exam Performed:</b> {', '.join(imaging)}", body),
        Paragraph(f"<b>Findings:</b> {findings}", body),
        Paragraph(f"<b>Impressions:</b> {impressions}", body),
    ]

    elements += [
        Paragraph(f"<b>Exam Performed:</b> {', '.join(imaging)}", body),
        Paragraph(f"<b>Findings:</b> {findings}", body),
        Paragraph(f"<b>Impressions:</b> {impressions}", body),
    ]

    create_pdf(out_path, elements)


def doc_pathology(info, icd, out_path, patient, date):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    lab_tests = info.get("lab_tests", [])

    elements = header("Pathology Report", patient["hospital"], patient["name"])

    elements += [
        Paragraph(f"<b>Patient Name:</b> {patient['name']}", body),
        Paragraph(f"<b>Age:</b> {info['age']}", body),
        Paragraph(f"<b>Gender:</b> {info['gender']}", body),
        Paragraph(f"<b>Date:</b> {format_date(date)}", body),
        Spacer(1, 10),
        Paragraph("<b>Lab Tests:</b>", body),
    ]

    for t in lab_tests:
        elements.append(Paragraph(f"• {t}", body))

    elements += [
        Spacer(1, 10),
        Paragraph("<b>Notes & Findings:</b>", body),
    ]

    notes = info["pathalogy_test_notes_and_findings"]
    if isinstance(notes, list):
        notes = "\n".join(notes)
    elements.append(Paragraph(notes, body))

    create_pdf(out_path, elements)


def doc_discharge(info, icd, out_path, patient, admit_date, discharge_date):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    elements = header("Discharge Summary", patient["hospital"], patient["name"])

    elements += [
        Paragraph(f"<b>Patient Name:</b> {patient['name']}", body),
        Paragraph(f"<b>Age:</b> {info['age']}", body),
        Paragraph(f"<b>Gender:</b> {info['gender']}", body),
        Paragraph(f"<b>Date of Admission:</b> {format_date(admit_date)}", body),
        Paragraph(f"<b>Date of Discharge:</b> {format_date(discharge_date)}", body),
        Spacer(1, 10),

        Paragraph(f"<b>Reason for Admission:</b> {info['reason_for_admission']}", body),
        Paragraph(f"<b>Medical History:</b> {info['medical_history']}", body),
        Spacer(1, 10),

        Paragraph("<b>Procedures Performed:</b>", body),
    ]

    for p in info.get("procedure_performed", []):
        elements.append(Paragraph(f"• {p}", body))

    elements += [
        Spacer(1, 10),
        Paragraph(f"<b>Procedure Outcome:</b> {info['procedure_outcomes']}", body),
        Paragraph(f"<b>Medications on Discharge:</b> {info['medications_on_discharge']}", body),
        Paragraph(f"<b>Instructions:</b> {info['precautions_to_be_taken']}", body),
        Paragraph(f"<b>Additional Notes:</b> {info['additional_notes']}", body),
    ]

    create_pdf(out_path, elements)


def doc_bill(info, icd, out_path, patient, date):
    styles = getSampleStyleSheet()
    body = styles["BodyText"]

    consultation = info.get("consultation_charges (standard charges in rupees)", info.get("consultation_charges", 0))
    lab_tests = info.get("lab_test_charges (standard charges in rupees)", info.get("lab_test_charges", 0))
    imaging = info.get("imaging_charges (standard charges in rupees)", info.get("imaging_charges", 0))
    medications = info.get("medication_charges (standard charges in rupees)", info.get("medication_charges", 0))
    procedures = info.get("procedure_costs (standard charges in rupees)", info.get("procedure_costs", 0))

    table_data = [
        ["Service", "Cost (₹)"],
        ["Consultation", consultation],
        ["Lab Tests", lab_tests],
        ["Imaging", imaging],
        ["Medications", medications],
        ["Procedures", procedures],
    ]

    table = Table(table_data, colWidths=[300, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements = header("Hospital Bill Summary", patient["hospital"], patient["name"])

    elements += [
        Paragraph(f"<b>Patient Name:</b> {patient['name']}", body),
        Paragraph(f"<b>Age:</b> {info['age']}", body),
        Paragraph(f"<b>Gender:</b> {info['gender']}", body),
        Paragraph(f"<b>Date:</b> {format_date(date)}", body),
        Spacer(1, 20),
        table,
    ]

    create_pdf(out_path, elements)


# ============================================================
# MAIN LOOP
# ============================================================
def main():

    notes_folder = "/mnt/StorageHDD/PICT/processed_data/cancer_data/clinical_notes"
    json_folder  = "/mnt/StorageHDD/PICT/medical_info_extracted"
    output_root  = "/mnt/StorageHDD/PICT/medical_documents"
    csv_path     = "/mnt/StorageHDD/PICT/processed_data/cancer_data/combined.csv"

    icd_map = load_icd_map(csv_path)

    for txt_file in Path(notes_folder).glob("*.txt"):

        file_id = txt_file.stem
        json_path = Path(json_folder) / f"{file_id}.json"

        if not json_path.exists():
            print("Skipping (JSON missing):", file_id)
            continue

        info = json.load(open(json_path))

        # patient constants
        patient = {
            "name": fake.name(),
            "hospital": fake.company() + " Medical Center"
        }
        doctor = fake.name()

        admit_date = datetime.today() - timedelta(days=fake.random_int(2, 12))
        dateshift = fake.random_int(1, 3)

        icd = icd_map.get(file_id, {"main_icd": "Not specified", "procedure_icd": "Not specified"})

        out_dir = Path(output_root) / file_id
        out_dir.mkdir(parents=True, exist_ok=True)

        # Generate all PDFs
        doc_admission(info, icd, out_dir/"1_admission_note.pdf", patient, doctor, admit_date)
        doc_prescription(info, icd, out_dir/"2_doctor_prescription.pdf", patient, doctor, admit_date + timedelta(days=1))
        doc_imaging(info, icd, out_dir/"3_imaging_report.pdf", patient, admit_date + timedelta(days=dateshift))
        doc_pathology(info, icd, out_dir/"4_pathology_report.pdf", patient, admit_date + timedelta(days=dateshift))
        doc_discharge(info, icd, out_dir/"5_discharge_summary.pdf", patient, admit_date, admit_date + timedelta(days=dateshift+1))
        doc_bill(info, icd, out_dir/"6_bill_summary.pdf", patient, admit_date + timedelta(days=dateshift+1))

        print("✔ Generated documents for:", file_id)


if __name__ == "__main__":
    main()


# /mnt/StorageHDD/PICT/medical_documents/S0004-06142006000600012-1