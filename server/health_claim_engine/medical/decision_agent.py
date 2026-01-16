import json
from groq import Groq

class DecisionAgent:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def decide(self, patient_data, icd_candidates, extracted_condition):
        # Format candidates clearly
        candidates_str = "\n".join([
            f"- {c['code']}: {c['desc']} (Match Score: {c['score']})"
            for c in icd_candidates
        ])
        
        if isinstance(patient_data, dict):
            patient_context = json.dumps(patient_data, indent=2)
        else:
            patient_context = str(patient_data)

        system_prompt = """
        You are a strict Medical Coding Auditor. Your job is to select the ONE correct ICD-10 code.

        RULES FOR SELECTION:
        1. **SEMANTIC MATCHING**: You MUST use your general medical knowledge to match terms. 
           - Example: If patient has "Renal Calculus" and candidate is "N20.0 Calculus of kidney", SELECT IT. They are the same.
           - Example: If patient has "Hepatic Malignancy" and candidate is "C22.0 Liver Cell Carcinoma", SELECT IT.
        
        2. **FACTUAL BOUNDARIES**: Do NOT cross clinical boundaries.
           - If pathology says "Benign", DO NOT pick a "Malignant" code, even if it's the only option.
           - If pathology is "Inconclusive", DO NOT pick a specific diagnosis code.
        
        3. **SPECIFICITY**: Prefer specific codes (e.g., "Right Eye") over general ones ("Unspecified Eye") if the data supports it.

        4. **EXCLUSIONS**:
           - If "Alcohol" is a factor in a liver case, prioritize Alcohol-related codes (K70).
           - If "Cosmetic" intent is found for plastic surgery, look for Z-codes (Z41.1).

        Output strictly valid JSON:
        {
          "selected_code": "The chosen ICD code (or 'None' if no match)",
          "confidence_score": 0.95,
          "reasoning": "Explain the semantic link between the patient notes and the selected code."
        }
        """

        user_prompt = f"""
        **Patient Record:**
        {patient_context}

        **Primary Search Condition:**
        {extracted_condition}

        **Candidate Codes (Generated via fuzzy search):**
        {candidates_str}

        **Instruction:**
        Select the code that clinially matches the patient record. 
        Use semantic understanding (synonyms) but strictly adhere to the clinical facts (benign vs malignant).
        """

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Decision Error: {e}")
            return {
                "selected_code": icd_candidates[0]['code'] if icd_candidates else "R69",
                "confidence_score": 0.5,
                "reasoning": "Fallback due to error."
            }