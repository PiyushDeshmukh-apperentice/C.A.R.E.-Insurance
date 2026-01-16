import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class Decision(Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PARTIALLY_COVERED = "partially_covered"
    MANUAL_REVIEW = "manual_review"
    PENDING_REVIEW = "pending_review"

@dataclass
class AdjudicationResult:
    decision: Decision
    reason: str
    covered_components: List[str]
    excluded_components: List[str]
    applicable_clauses: List[Dict]
    confidence_score: float

def load_policy_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    policy_path = os.path.join(base_dir, "..", "data", "parsed_policies.json")
    if not os.path.exists(policy_path):
        fallback = os.path.join(os.getcwd(), "health_claim_engine", "data", "parsed_policies.json")
        if os.path.exists(fallback):
            policy_path = fallback
    with open(policy_path, "r") as f:
        return json.load(f)

class ClaimAdjudicator:
    def adjudicate_claim(self, medical_record: Dict, policy_clauses: List[Dict]) -> AdjudicationResult:
        patient_data = medical_record.get('patient_data', medical_record)
        
        self.risk_factors = [r.lower() for r in patient_data.get('extracted_risk_factors', [])]
        self.intent = patient_data.get('procedure_intent', 'Medical').lower()
        self.final_icd = patient_data.get('final_icd', '')
        
        self.full_record_text = (
            str(patient_data.get('medical_history', '')) + " " +
            str(patient_data.get('hospital_course', '')) + " " +
            str(patient_data.get('chief_complaint', '')) + " " +
            str(patient_data.get('diagnosis', '')) + " " +
            str(patient_data.get('reason_for_admission', ''))
        ).lower()

        applicable_clauses = policy_clauses

        # 1. EXCLUSIONS (High Priority)
        exclusion = self._check_exclusions(applicable_clauses, patient_data)
        if exclusion: return exclusion

        # 2. WAITING PERIODS (This catches Pre-Existing conditions correctly)
        waiting = self._check_waiting_periods(applicable_clauses, patient_data)
        if waiting: return waiting
        
        # 3. LIMITS
        limit_result = self._check_limits(applicable_clauses, patient_data)
        if limit_result: return limit_result

        # 4. AMBIGUITY
        ambiguous = self._check_ambiguity(patient_data, applicable_clauses)
        if ambiguous: return ambiguous

        # 5. COVERAGE
        return self._check_coverage(applicable_clauses, patient_data)

    def _check_exclusions(self, clauses, data):
        """
        Check specific exclusion criteria in STRICT priority order.
        """
        exclusions = [c for c in clauses if 'exclusion' in c.get('section', '').lower() or 'table' in c.get('section', '').lower()]

        # --- PRIORITY 1: BEHAVIORAL (Alcohol/Drugs) ---
        for excl in exclusions:
            txt = excl.get('raw_text', '').lower()
            if 'alcohol' in txt or 'substance' in txt:
                if any(r for r in self.risk_factors if 'alcohol' in r or 'substance' in r):
                    return self._deny(excl, "Patient history indicates Alcohol/Substance abuse")

        # --- PRIORITY 2: INTENT (Cosmetic) ---
        for excl in exclusions:
            txt = excl.get('raw_text', '').lower()
            if 'cosmetic' in txt:
                if 'cosmetic' in self.intent or 'aesthetic' in self.intent:
                    if 'accident' not in self.full_record_text:
                        return self._deny(excl, "Procedure intent identified as Cosmetic/Aesthetic")

        # --- PRIORITY 3: MEDICAL NECESSITY (Investigation Only) ---
        for excl in exclusions:
            txt = excl.get('raw_text', '').lower()
            if 'investigation' in txt and 'evaluation' in txt:
                # Logic: Deny if NO Surgery AND NO Curative Meds
                
                procs = data.get('procedure_performed', [])
                has_surgery = False
                if procs and isinstance(procs, list):
                    for p in procs:
                        p_clean = str(p).lower().strip()
                        bad_keywords = ['none', 'null', 'evaluation', 'investigation', 'scan', 'test', 'monitor', 'check']
                        # Valid surgery must be substantial and not a diagnostic term
                        if len(p_clean) > 3 and not any(bk in p_clean for bk in bad_keywords):
                            has_surgery = True
                            break
                
                meds = data.get('medication_prescribed', [])
                has_curative_meds = False
                if meds and isinstance(meds, list):
                    ignored = ['vitamin', 'supplement', 'pain', 'analgesic', 'paracetamol', 'pan 40', 'calcium', 'syrup', 'tears']
                    for m in meds:
                        m_clean = str(m).lower()
                        if not any(i in m_clean for i in ignored):
                            has_curative_meds = True
                            break
                
                if not has_surgery and not has_curative_meds:
                     return self._deny(excl, "Admission primarily for investigation (No active surgery or curative medication found)")

        # --- PRIORITY 4: PRE-EXISTING (Absolute Exclusions Only) ---
        # CRITICAL FIX: Do NOT deny "Pre-Existing" here if the clause mentions "Waiting Period".
        # We want the Waiting Period logic (Priority 2) to handle that, so we can check Policy Age.
        for excl in exclusions:
            txt = excl.get('raw_text', '').lower()
            if 'pre-existing' in txt:
                # Skip if this is actually a pointer to waiting periods
                if 'waiting' in txt or 'months' in txt or '36' in txt or '48' in txt:
                    continue
                
                if self._is_pre_existing(data):
                    return self._deny(excl, "Condition identified as Pre-Existing (Absolute Exclusion)")

        return None

    def _check_waiting_periods(self, clauses, data):
        # 1. Trigger if Pre-Existing is found
        if self._is_pre_existing(data):
            
            # 2. Find the Waiting Period Clause
            wp_clause = None
            for c in clauses:
                txt = c.get('raw_text', '').lower()
                sec = c.get('section', '').lower()
                if 'waiting' in sec or 'waiting' in txt:
                    if 'pre-existing' in txt:
                        wp_clause = c
                        break
                    if not wp_clause: wp_clause = c
            
            # 3. Apply Logic
            if wp_clause:
                policy_age = data.get('policy_age_months')
                
                # Strict: Unknown age = Deny
                if policy_age is None:
                    return self._deny(wp_clause, "Pre-existing condition detected. Policy age unverified (Default Deny).")
                
                try:
                    if int(policy_age) < 36:
                        return self._deny(wp_clause, "Waiting period for Pre-Existing condition not met")
                except:
                    return self._deny(wp_clause, "Waiting period verification error")
        return None

    def _check_limits(self, clauses, data):
        sub_limits = [c for c in clauses if 'limit' in c.get('section', '').lower()]
        for limit in sub_limits:
            txt = limit.get('raw_text', '').lower()
            if 'cataract' in txt and 'cataract' in self.full_record_text:
                 return AdjudicationResult(
                    decision=Decision.PARTIALLY_COVERED,
                    reason=f"Claim restricted by Sub-Limit: {txt[:50]}...",
                    covered_components=["Partial Coverage"],
                    excluded_components=["Amount exceeding sub-limit"],
                    applicable_clauses=[limit],
                    confidence_score=0.9
                )
        return None

    def _check_coverage(self, clauses, data):
        cov_clause = next((c for c in clauses if 'general' in c.get('section', '').lower()), clauses[0] if clauses else {})
        return AdjudicationResult(
            decision=Decision.APPROVED,
            reason="Claim approved - covered under policy terms",
            covered_components=["Base Coverage"],
            excluded_components=[],
            applicable_clauses=[cov_clause],
            confidence_score=0.85
        )

    def _deny(self, clause, reason):
        return AdjudicationResult(
            decision=Decision.DENIED,
            reason=reason,
            covered_components=[],
            excluded_components=[clause.get('raw_text', '')[:100]],
            applicable_clauses=[clause],
            confidence_score=0.9
        )

    def _is_pre_existing(self, data):
        if any('pre-existing' in r for r in self.risk_factors): return True
        
        # Keyword scan
        keywords = ['known case', 'history of', 'diagnosed with', 'chronic', 'long standing', 'dm type 2', 'htn', 'diabetes', 'hypertension']
        text = self.full_record_text
        
        for k in keywords:
            if k in text:
                # Check for negation context (e.g. "No history of diabetes")
                idx = text.find(k)
                context = text[max(0, idx-20):idx+len(k)+5]
                if 'no ' not in context and 'nil ' not in context and 'not ' not in context:
                    return True
        return False
    
    def _check_ambiguity(self, data, clauses):
        return None