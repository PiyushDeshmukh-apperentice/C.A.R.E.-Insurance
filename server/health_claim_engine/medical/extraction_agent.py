import json
from groq import Groq

class ExtractionAgent:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def generate_queries(self, patient_data):
        if isinstance(patient_data, dict):
            context_str = json.dumps(patient_data, indent=2)
        else:
            context_str = str(patient_data)

        system_prompt = """
        You are an expert Medical Clinical Documentation Improvement (CDI) specialist.
        
        YOUR GOAL: Translate patient notes into search queries for an ICD-10 database.
        
        CRITICAL INSTRUCTIONS:
        1. **SEMANTIC EXPANSION**: If a term has common medical synonyms, include them. 
           (e.g., If text says "Heart Attack", add "Myocardial Infarction" to search queries).
        2. **FACTUAL STRICTNESS**: Do not infer conditions not present. If the report says "mass", do not write "cancer" unless "malignant" is specified.
        3. **RISK FACTORS**: Explicitly extract Alcohol, Smoking, or History of abnormalities.
        4. **INTENT**: Identify if a procedure is "Cosmetic" or "Medically Necessary".

        Output strictly valid JSON:
        {
          "primary_condition": "The main medical condition extracted verbatim",
          "procedure_intent": "Medical" or "Cosmetic",
          "risk_factors": ["Alcohol abuse", "Smoking", "Diabetes"],
          "search_queries": [
             "Original Term",
             "Standard Medical Term (Synonym 1)",
             "Alternative Description (Synonym 2)"
          ]
        }
        """

        user_prompt = f"""
        Analyze this patient record and generate semantic search queries:
        {context_str}
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
            
            # Safety check
            if "search_queries" not in result:
                result["search_queries"] = [result.get("primary_condition", "")]
                
            return result

        except Exception as e:
            print(f"Extraction Error: {e}")
            return {
                "primary_condition": "Unknown",
                "search_queries": [patient_data.get("chief_complaint", "Medical Assessment")],
                "risk_factors": []
            }