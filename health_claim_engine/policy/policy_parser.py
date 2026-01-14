import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import fitz  # PyMuPDF
import json
import re
sys.path.append('..')
from ..medical.extraction_agent import ExtractionAgent
from ..medical.retrieval_engine import RetrievalEngine
from ..config import GROQ_API_KEY

class PolicyParser:
    def __init__(self, api_key=None):
        self.api_key = api_key or GROQ_API_KEY
        self.extraction_agent = ExtractionAgent(self.api_key)
        
        # Rule priority for conflict resolution (higher = more restrictive)
        self.RULE_PRIORITY = {
            "exclusion": 4,
            "waiting_period": 3,
            "limit": 2,
            "coverage": 1
        }

    def parse_pdf(self, pdf_path):
        """Extract text from PDF page-wise"""
        doc = fitz.open(pdf_path)
        pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            pages.append({
                "page_num": page_num + 1,
                "text": text
            })
        doc.close()
        return pages

    def merge_pages_by_section(self, pages):
        """DISABLED: Section merging was causing massive recall loss. Using page windows instead."""
        # For now, treat each page as its own "section" to restore clause count
        sections = []
        for page in pages:
            sections.append({
                "title": f"Page {page['page_num']}",
                "text": page['text'],
                "pages": [page['page_num']]
            })
        return sections

    def extract_clauses(self, sections):
        """Use LLM to extract atomic clauses from sections with recall protection"""
        all_clauses = []
        for section in sections:
            # First attempt: strict atomic clauses
            clauses = self._extract_clauses_attempt(section, strict=True)
            
            # If no clauses found, retry with bullet-point extraction (recall protection)
            if not clauses:
                print(f"  No clauses found in {section['title']}, retrying with bullet-point extraction...")
                clauses = self._extract_clauses_attempt(section, strict=False)
            
            if clauses:
                # Don't overwrite LLM-extracted section
                for clause in clauses:
                    clause['section'] = clause.get('section', section['title'])
                    clause['pages'] = section['pages']
                all_clauses.extend(clauses)
            else:
                print(f"  Still no clauses found in {section['title']}")
                
        return all_clauses

    def _extract_clauses_attempt(self, section, strict=True):
        """Single extraction attempt with configurable strictness"""
        if strict:
            prompt = f"""
SYSTEM: You are an expert insurance policy analyst. Output ONLY valid JSON array.

TASK: Extract atomic clauses from this policy section.

SECTION: {section['title']}
CONTENT:
{section['text']}

OUTPUT: JSON array only
[
  {{
    "clause_id": "IV.1(a)",
    "section": "Exclusions",
    "raw_text": "Attempted suicide or intentional self-inflicted injury"
  }}
]
"""
        else:
            # More permissive: extract any bullet points, numbered items, or distinct statements
            prompt = f"""
SYSTEM: You are an insurance policy analyst. Output ONLY valid JSON array.

TASK: Extract ANY rule-like statements from this text. Include:
- Numbered or bulleted items
- Parenthetical statements
- Any text that looks like a rule or condition

SECTION: {section['title']}
CONTENT:
{section['text']}

OUTPUT: JSON array only
[
  {{
    "clause_id": "1",
    "section": "General",
    "raw_text": "Any rule-like statement you can find"
  }}
]
"""

        response = self.call_llm(prompt)
        
        # Clean response
        response = response.strip()
        prefixes_to_remove = [
            "Based on the provided policy document section,",
            "Here are the extracted clauses:",
            "```json",
            "```"
        ]
        
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Try to extract JSON array
        if response.startswith('['):
            try:
                clauses = json.loads(response)
                return clauses
            except json.JSONDecodeError as e:
                print(f"JSON decode error in {section['title']}: {e}")
                return []
        else:
            return []

    def extract_medical_concepts(self, clauses):
        """Extract medical concepts from clauses"""
        for clause in clauses:
            prompt = f"""
SYSTEM: You are a medical concept extractor. Output ONLY valid JSON. No explanations.

TASK: Extract medical concepts from this clause.

CLAUSE: {clause['raw_text']}

OUTPUT: JSON only
{{
  "medical_concepts": ["cancer", "heart disease"],
  "conditions": ["malignant", "severe"]
}}
"""
            response = self.call_llm(prompt)
            
            response = response.strip()
            
            # Remove common prefixes
            prefixes_to_remove = ["Here are the medical concepts:", "```json", "```"]
            for prefix in prefixes_to_remove:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()
            
            try:
                concepts = json.loads(response)
                clause.update(concepts)
            except json.JSONDecodeError as e:
                print(f"JSON decode error for concepts in clause {clause.get('clause_id', 'unknown')}: {e}")
                clause['medical_concepts'] = []
                clause['conditions'] = []
                continue

    def extract_rule_logic(self, clauses):
        """Extract structured rule logic from clauses for rule engine"""
        for clause in clauses:
            prompt = f"""
SYSTEM: You are an insurance rule extractor. Output ONLY valid JSON. No explanations.

TASK: Extract rule logic from this clause.

CLAUSE: {clause['raw_text']}
SECTION: {clause.get('section', 'Unknown')}

OUTPUT: JSON only
{{
  "rule_type": "coverage|exclusion|limit|waiting_period",
  "limits": [
    {{
      "type": "fixed_amount|percentage|capped_amount",
      "value": 40000,
      "currency": "INR",
      "percentage_of": "SI",
      "condition": "per_occurrence|annual|lifetime"
    }}
  ],
  "waiting_periods": [
    {{
      "condition": "hernia|pre_existing|general",
      "months": 24,
      "description": "Waiting period for hernia surgery"
    }}
  ],
  "coverage_conditions": [
    {{
      "type": "age_limit|treatment_type|hospitalization",
      "min_age": 18,
      "max_age": 65,
      "treatment_types": ["surgery", "medical_management"],
      "requires_hospitalization": true
    }}
  ],
  "exclusions": [
    {{
      "condition": "self_inflicted|pre_existing|cosmetic",
      "description": "Attempted suicide or intentional self-inflicted injury"
    }}
  ]
}}
"""
            response = self.call_llm(prompt)
            
            response = response.strip()
            
            # Remove common prefixes
            prefixes_to_remove = ["Here is the rule logic:", "Based on the clause:", "```json", "```"]
            for prefix in prefixes_to_remove:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()
            
            try:
                rule_logic = json.loads(response)
                clause['rule_logic'] = rule_logic
            except json.JSONDecodeError as e:
                print(f"JSON decode error for rule logic in clause {clause.get('clause_id', 'unknown')}: {e}")
                clause['rule_logic'] = {
                    "rule_type": "unknown",
                    "limits": [],
                    "waiting_periods": [],
                    "coverage_conditions": [],
                    "exclusions": []
                }
                continue

    def extract_tables(self, pages):
        """Extract tables from PDF pages"""
        # Open PDF once for efficiency
        pdf_path = pages[0].get('pdf_path') if pages else None
        if not pdf_path:
            return []
            
        doc = fitz.open(pdf_path)
        tables_data = []
        
        for page in pages:
            page_obj = doc.load_page(page['page_num'] - 1)
            
            # Find tables using PyMuPDF
            tabs = page_obj.find_tables()
            for tab in tabs:
                table_data = tab.extract()
                if table_data:
                    tables_data.append({
                        "page": page['page_num'],
                        "table_data": table_data,
                        "headers": table_data[0] if table_data else []
                    })
        
        doc.close()
        return tables_data

    def parse_table_rules(self, tables):
        """Parse rule information from tables (waiting periods, limits, etc.)"""
        table_rules = []
        for table in tables:
            prompt = f"""
Analyze this table from an insurance policy and extract rule information.

Table Headers: {table['headers']}
Table Data: {table['table_data']}

Common table types in insurance policies:
1. Waiting Periods table
2. Sum Insured limits table  
3. Coverage limits table
4. Disease-specific rules table

Output ONLY valid JSON array of rules:
[
  {{
    "rule_type": "waiting_period|limit|coverage",
    "condition": "hernia|diabetes|cancer",
    "waiting_months": 24,
    "limit_amount": 40000,
    "description": "24-month waiting period for hernia"
  }}
]
"""
            response = self.call_llm(prompt)
            json_match = re.search(r'(\[.*\])', response, re.DOTALL)
            if json_match:
                try:
                    rules = json.loads(json_match.group(1))
                    for rule in rules:
                        rule['source'] = 'table'
                        rule['page'] = table['page']
                    table_rules.extend(rules)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error for table on page {table['page']}: {e}")
                    continue
        return table_rules

    def map_to_icd(self, clauses, icd_db):
        """Map medical concepts to ICD codes using retrieval engine with broader matching"""
        engine = RetrievalEngine(icd_db)
        for clause in clauses:
            concepts = clause.get('medical_concepts', [])
            if concepts:
                # Build comprehensive search queries
                queries = []
                for concept in concepts:
                    # Add base concept
                    queries.append(concept)
                    
                    # Add with conditions
                    conditions = clause.get('conditions', [])
                    for condition in conditions:
                        queries.append(f"{condition} {concept}")
                    
                    # Add common variations
                    if concept.lower() in ['cancer', 'tumor']:
                        queries.extend(['malignant neoplasm', 'neoplasm', 'carcinoma'])
                    elif concept.lower() in ['heart', 'cardiac']:
                        queries.extend(['cardiovascular', 'cardiac disease'])
                    
                    # Add rule-specific context
                    rule_logic = clause.get('rule_logic', {})
                    waiting_periods = rule_logic.get('waiting_periods', [])
                    for wp in waiting_periods:
                        if wp.get('condition'):
                            queries.append(f"{wp['condition']} {concept}")
                
                # Get more candidates for broader coverage
                candidates = engine.get_candidates(queries, max_candidates=10)
                
                # Prioritize common codes over rare ones
                prioritized_candidates = []
                for candidate in candidates:
                    code = candidate.get('code', '')
                    # Boost common ICD-10 patterns
                    if re.match(r'^[A-Z]\d{2}(\.\d+)?$', code):  # Standard ICD format
                        # Prefer codes without high specificity (fewer decimal places)
                        specificity = len(code.split('.')) - 1
                        candidate['priority'] = 1.0 / (specificity + 1)  # Higher priority for less specific
                    else:
                        candidate['priority'] = 0.1
                    
                    prioritized_candidates.append(candidate)
                
                # Sort by priority and take top candidates
                prioritized_candidates.sort(key=lambda x: x.get('priority', 0), reverse=True)
                clause['icd_candidates'] = prioritized_candidates[:5]  # Top 5 most relevant

                # Sort by priority and take top candidates
                prioritized_candidates.sort(key=lambda x: x.get('priority', 0), reverse=True)
                clause['icd_candidates'] = prioritized_candidates[:5]  # Top 5 most relevant

    def resolve_rule_conflicts(self, rules):
        """Resolve conflicting rules using priority system"""
        if not rules:
            return rules
            
        # Sort by priority (higher priority first)
        resolved_rules = sorted(rules, key=lambda r: self.RULE_PRIORITY.get(r.get('rule_type', 'unknown'), 0), reverse=True)
        
        # For same priority, prefer more specific rules
        final_rules = []
        seen_types = set()
        
        for rule in resolved_rules:
            rule_type = rule.get('rule_type')
            if rule_type not in seen_types:
                final_rules.append(rule)
                seen_types.add(rule_type)
                
        return final_rules

    def parse_policy(self, pdf_path, icd_db):
        """Full pipeline: PDF -> Tables as Clauses -> Text Clauses -> Rules -> ICD -> Resolution"""
        pages = self.parse_pdf(pdf_path)
        
        # Add pdf_path to pages for table extraction
        for page in pages:
            page['pdf_path'] = pdf_path
        
        # STEP 1: Extract table rows as primary clauses (CIS PDFs are table-heavy)
        table_clauses = self.extract_table_clauses(pages)
        
        # STEP 2: Extract text-based clauses  
        sections = self.merge_pages_by_section(pages)
        text_clauses = self.extract_clauses(sections)
        
        # STEP 3: Combine all clauses
        all_clauses = table_clauses + text_clauses
        print(f"Total clauses before processing: {len(all_clauses)} (tables: {len(table_clauses)}, text: {len(text_clauses)})")
        
        # STEP 4: Extract rule logic from all clauses
        self.extract_medical_concepts(all_clauses)
        self.extract_rule_logic(all_clauses)
        
        # STEP 5: Map to ICD
        self.map_to_icd(all_clauses, icd_db)
        
        # STEP 6: Return all processed clauses (don't aggressively resolve conflicts yet)
        # Conflict resolution should happen during claim adjudication, not policy parsing
        print(f"Final processed clauses: {len(all_clauses)}")
        return all_clauses

    def extract_table_clauses(self, pages):
        """Extract table rows as clauses first (critical for CIS PDFs)"""
        table_clauses = []
        
        # Open PDF once for efficiency
        pdf_path = pages[0].get('pdf_path') if pages else None
        if not pdf_path:
            return table_clauses
            
        doc = fitz.open(pdf_path)
        
        for page in pages:
            page_obj = doc.load_page(page['page_num'] - 1)
            
            # Find tables
            tabs = page_obj.find_tables()
            for tab_idx, tab in enumerate(tabs):
                table_data = tab.extract()
                if not table_data or len(table_data) < 2:  # Need header + at least one data row
                    continue
                    
                headers = table_data[0] if table_data else []
                
                # Process each data row as a potential clause
                for row_idx, row in enumerate(table_data[1:], 1):  # Skip header
                    if not row or all(not cell.strip() for cell in row if cell):
                        continue  # Skip empty rows
                    
                    # Convert table row to clause format
                    clause_text = " | ".join(str(cell).strip() for cell in row if cell and cell.strip())
                    
                    if len(clause_text) < 10:  # Skip very short rows
                        continue
                        
                    clause = {
                        "clause_id": f"Table_{page['page_num']}_{tab_idx}_{row_idx}",
                        "section": "Table_Data",  # Will be refined by LLM
                        "raw_text": clause_text,
                        "source": "table",
                        "table_headers": headers,
                        "pages": [page['page_num']]
                    }
                    
                    table_clauses.append(clause)
        
        doc.close()
        print(f"Extracted {len(table_clauses)} clauses from tables")
        return table_clauses

    def call_llm(self, prompt):
        import requests
        import time
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "llama-3.1-8b-instant",  # Groq model
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }
                response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
                
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
                elif response.status_code == 429:  # Rate limit
                    wait_time = 10 * (attempt + 1)  # Exponential backoff
                    print(f"Rate limit hit, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"LLM call failed: {response.text}")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(5)
        
        raise Exception("Max retries exceeded")