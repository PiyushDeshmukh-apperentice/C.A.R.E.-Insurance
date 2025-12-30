import json
import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API = os.getenv("API")
genai.configure(api_key=API)

# ----------------------------------------------------
# STRICT JSON EXTRACTION FOR MEDICAL INFORMATION
# ----------------------------------------------------
def extract_structured_medical_info(note_text):

    model = genai.GenerativeModel("gemma-3-27b-it")

    prompt = f"""
You are a medical information extraction system.

Extract the following information from the clinical note and structure it with added infromation which will be helpful in creating synthetic documents:

1. age
2. gender
3. lab_tests
4. chief complaint
5. medical history
6. reason for admission
7. medication prescribed with dosage
8. pathalogy test prescribed by the doctor only the test name
9. precautions to be taken 
10. imaging exams prescibed 
11. findings of imaging report
12. impressions from the imaging report
13. recommendations
14. pathalogy test notes and findings
15. overall hospital course 
16. procedure performed 
17. procedure outcomes
18. medications on discharge
19. additional notes 
20. consultation charges (standard charges in rupees)
21. lab test charges (standard charges in rupees)
22. imaging charges (standard charges in rupees)
23. medication charges (standard charges in rupees)
24. procedure costs (standard charges in rupees)

IMPORTANT RULES:
- charges should differ from procedure to procedure look for the average charges of lab tests, imaging, medication and procedure costs. the costs are not explicity mentioned in the clincal notes it is your job to estimate the cost of each and every procedure and return medication : cost, procedure : cost, lab test : cost, miscellaneous : cost, accomodation : cost and all other different cost on the basis of clincal note
- DO NOT add any extra fields.
- YOU CAN generate assumptions for fields which are not mentioned.
- DO NOT ASK FOR NAMES, DATES.
- RETURN ONLY VALID JSON. No explanations. No markdown.

Clinical Note:
\"\"\"{note_text}\"\"\"
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # JSON parsing
    try:
        return json.loads(raw)
    except:
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except:
            return {"error": "Invalid JSON returned", "raw_text": raw}


# ------------------------------------------------
# PROCESS ALL CLINICAL NOTE FILES
# ------------------------------------------------
def main():

    clinical_notes_dir = Path("/mnt/StorageHDD/PICT/processed_data/cancer_data/clinical_notes")
    output_json_dir = Path("/mnt/StorageHDD/PICT/medical_info_extracted/cancer2_data")
    output_json_dir.mkdir(parents=True, exist_ok=True)

    txt_files = list(clinical_notes_dir.glob("*.txt"))
    print(f"Found {len(txt_files)} clinical note files.")

    for txt_file in txt_files:
        print(f"\n📌 Processing: {txt_file.name}")

        note_text = txt_file.read_text(errors="ignore")
        info = extract_structured_medical_info(note_text)

        json_path = output_json_dir / (txt_file.stem + ".json")
        json_path.write_text(json.dumps(info, indent=2))

        print(f"✅ Saved JSON: {json_path}")

    print("\n🎉 All files processed successfully!")


if __name__ == "__main__":
    main()
