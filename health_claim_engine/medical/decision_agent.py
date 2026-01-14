import json
import requests
import re
from ..config import GROQ_API_KEY

class DecisionAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or GROQ_API_KEY
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def decide(self, patient_data, candidates, primary_condition=None):
        extracted_condition = primary_condition or "Left paratesticular tumor"  # From impressions
        relevant_notes = patient_data.get("pathalogy_test_notes_and_findings", "")

        candidates_str = "\n".join([f"{i+1}. {{code: \"{c['code']}\", desc: \"{c['desc']}\"}}" for i, c in enumerate(candidates)])

        prompt = f"""
Patient Condition: {extracted_condition}
Clinical Notes: {relevant_notes}

I have retrieved these {len(candidates)} Candidate ICD-10 Codes from the database:
{candidates_str}

Task:
Analyze the clinical notes (look for 'malignant', 'benign', specific location).
Select the BEST code from the list above.
If none match, output "None".

You must NEVER output an ICD code outside of selecting from the provided list. If you do, the output will be discarded.

Output JSON:
{{
  "selected_code": "C63.1",
  "confidence_score": "High",
  "reasoning": "Notes indicate 'pleosarcoma' (malignant) and location is 'paratesticular/cord', which maps to Spermatic Cord (C63.1). Excluded D29.2 because pathology confirms malignancy."
}}
"""

        response = self.call_llm(prompt)
        # Extract JSON from the response
        # Look for JSON after "Output JSON:" or in code blocks
        json_match = re.search(r'Output JSON:\s*(\{.*?\})', response, re.DOTALL)
        if not json_match:
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if not json_match:
            # Fallback: find JSON with selected_code
            json_match = re.search(r'(\{[^}]*"selected_code"[^}]*\})', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
        else:
            raise ValueError("No JSON found in LLM response")

    def call_llm(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        response = requests.post(self.url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"LLM call failed: {response.text}")