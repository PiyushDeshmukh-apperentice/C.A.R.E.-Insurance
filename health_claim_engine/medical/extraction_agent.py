import json
import requests
import re
from ..config import GROQ_API_KEY

class ExtractionAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or GROQ_API_KEY
        self.url = "https://api.groq.com/openai/v1/chat/completions"  # Groq API

    def generate_queries(self, patient_data):
        patient_json_string = json.dumps(patient_data, indent=2)

        prompt = f"""
You are an expert Medical Coder.
Read this Patient Record:
{patient_json_string}

Task:
Extract raw diagnostic concepts from the record. Do NOT normalize anatomy terms in the output. Output raw concepts only.

For search purposes, also provide standard medical terminology mappings.

You must NEVER output an ICD code. If you do, the output will be discarded.

Output ONLY valid JSON in this exact format:
{{
  "diagnoses": [
    {{
      "raw_text": "Left paratesticular malignant tumor",
      "anatomy": "paratesticular",
      "laterality": "left",
      "malignancy": "malignant",
      "standard_anatomy": "spermatic cord"
    }}
  ]
}}
"""

        response = self.call_llm(prompt)
        # Extract JSON from the response
        # Look for JSON after explanatory text
        json_match = re.search(r'(\{.*\})', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            data = json.loads(json_str)
            # Now build search queries from raw concepts
            search_queries = self.build_search_queries(data['diagnoses'])
            return {
                "diagnoses": data['diagnoses'],
                "search_queries": search_queries
            }
        else:
            raise ValueError("No JSON found in LLM response")

    def build_search_queries(self, diagnoses):
        queries = []
        for diag in diagnoses:
            raw = diag.get('raw_text', '')
            anatomy = diag.get('anatomy', '')
            standard_anatomy = diag.get('standard_anatomy', anatomy)  # Use standard for search
            laterality = diag.get('laterality', '')
            malignancy = diag.get('malignancy', '')
            
            # Build queries deterministically
            if malignancy and standard_anatomy:
                queries.append(f"{malignancy} neoplasm of {standard_anatomy}")
            if standard_anatomy:
                queries.append(f"neoplasm of {standard_anatomy}")
            if raw:
                queries.append(raw)
            if laterality and standard_anatomy:
                queries.append(f"{laterality} {standard_anatomy} neoplasm")
        
        # Remove duplicates and limit to 3
        unique_queries = list(set(queries))[:3]
        return unique_queries

    def call_llm(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",  # Groq model
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        response = requests.post(self.url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"LLM call failed: {response.text}")