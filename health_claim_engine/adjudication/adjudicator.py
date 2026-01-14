import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import json
import pandas as pd
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from ..medical.extraction_agent import ExtractionAgent
from ..medical.retrieval_engine import RetrievalEngine
from ..medical.decision_agent import DecisionAgent
from ..config import GROQ_API_KEY

class Decision(Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PARTIALLY_COVERED = "partially_covered"
    MANUAL_REVIEW = "manual_review"

@dataclass
class AdjudicationResult:
    decision: Decision
    reason: str
    covered_components: List[str]
    excluded_components: List[str]
    applicable_clauses: List[Dict]
    confidence_score: float

def load_medical_data():
    """Load processed medical record"""
    with open("medical_icd.json", "r") as f:
        return json.load(f)

def load_policy_data():
    """Load parsed policy clauses"""
    with open("health_claim_engine/data/parsed_policies.json", "r") as f:
        return json.load(f)

def process_medical_record(json_file: str, save_to_file=False) -> Optional[Dict]:
    """Process a single medical record and return ICD data (integrated from parse_medical.py)"""
    try:
        # Load ICD database
        icd_db = pd.read_excel("health_claim_engine/data/2026-ICD-10-CM Codes.xlsx")

        with open(json_file, "r") as f:
            raw_data = json.load(f)

        # Handle OCR output format
        if 'documents' in raw_data:
            docs = raw_data['documents']
            patient_data = raw_data.get('patient_info', {})
            if 'discharge_summary' in docs:
                ds = docs['discharge_summary']
                patient_data.update({
                    'chief_complaint': ds.get('reason_for_admission', ''),
                    'impressions_from_the_imaging_report': ds.get('final_diagnosis', ''),
                    'procedure_performed': ds.get('procedures_performed', []),
                    'medication_prescribed_with_dosage': ds.get('medications_on_discharge', []),
                    'overall_hospital_course': ds.get('hospital_course', ''),
                    'total_estimated_cost': ds.get('total_estimated_cost', 0)
                })
            if 'pathology_report' in docs:
                pr = docs['pathology_report']
                patient_data['pathalogy_test_notes_and_findings'] = pr.get('results', '')
            if 'imaging_report' in docs:
                ir = docs['imaging_report']
                patient_data['impressions_from_the_imaging_report'] = ir.get('impression', '')
            # Add more mappings as needed
        else:
            # Handle direct format
            if 'claim_data' in raw_data:
                patient_data = raw_data['claim_data']
            else:
                patient_data = raw_data

        # Step A: Extraction & Expansion
        agent_a = ExtractionAgent(GROQ_API_KEY)
        query_data = agent_a.generate_queries(patient_data)

        # Add delay to avoid rate limiting
        time.sleep(1)

        # Step B: Retrieval
        engine = RetrievalEngine(icd_db)
        candidates = engine.get_candidates(query_data['search_queries'])

        # Step C: Decision
        agent_c = DecisionAgent(GROQ_API_KEY)
        final_decision = agent_c.decide(patient_data, candidates, query_data['diagnoses'][0]['raw_text'] if query_data['diagnoses'] else "Unknown condition")

        # Add delay to avoid rate limiting
        time.sleep(1)

        result = {
            "patient_file": json_file,
            "diagnoses": query_data['diagnoses'],
            "search_queries": query_data['search_queries'],
            "icd_candidates": candidates,
            "final_icd": final_decision.get('selected_code'),
            "confidence": final_decision.get('confidence_score'),
            "reasoning": final_decision.get('reasoning'),
            "patient_data": patient_data  # Include original patient data for adjudication
        }

        return result

    except Exception as e:
        print(f"❌ Error processing {json_file}: {e}")
        return None

class ClaimAdjudicator:
    """Advanced claim adjudication engine with rule priority system"""

    def __init__(self):
        self.rule_priority = {
            'exclusions': 1,
            'waiting_periods': 2,
            'limits': 3,
            'coverage': 4
        }

    def adjudicate_claim(self, medical_record: Dict, policy_clauses: List[Dict]) -> AdjudicationResult:
        """
        Main adjudication logic following rule priority:
        1. Check exclusions (highest priority)
        2. Check waiting periods
        3. Check limits
        4. Check coverage (lowest priority)
        """

        medical_icd = medical_record.get('final_icd', '')
        patient_data = medical_record.get('patient_data', {})

        # Merge patient_data into medical_record for easier access
        medical_record.update(patient_data)

        # Find applicable clauses for this ICD
        applicable_clauses = self._find_applicable_clauses(medical_icd, policy_clauses)

        if not applicable_clauses:
            return AdjudicationResult(
                decision=Decision.MANUAL_REVIEW,
                reason="No policy clauses found matching the medical ICD code",
                covered_components=[],
                excluded_components=[],
                applicable_clauses=[],
                confidence_score=0.0
            )

        # Rule Priority Check 1: Exclusions
        exclusion_result = self._check_exclusions(applicable_clauses, medical_record)
        if exclusion_result:
            return exclusion_result

        # Rule Priority Check 2: Waiting Periods
        waiting_period_result = self._check_waiting_periods(applicable_clauses, medical_record)
        if waiting_period_result:
            return waiting_period_result

        # Rule Priority Check 3: Coverage
        coverage_result = self._check_coverage(applicable_clauses, medical_record)
        if coverage_result.decision in [Decision.APPROVED, Decision.PARTIALLY_COVERED]:
            return coverage_result

        # Rule Priority Check 4: Limits (only if not covered)
        limit_result = self._check_limits(applicable_clauses, medical_record)
        if limit_result:
            return limit_result

        return coverage_result

    def _find_applicable_clauses(self, medical_icd: str, policy_clauses: List[Dict]) -> List[Dict]:
        """Find policy clauses that apply to the medical condition"""
        applicable = []

        # Check if it's a cancer-related ICD (C00-D49 range)
        medical_icd = medical_icd or ''
        is_cancer = medical_icd.startswith(('C', 'D')) and len(medical_icd) >= 3

        for clause in policy_clauses:
            # Always include exclusions, general terms, and table data
            section = clause.get('section', '').lower()
            if section in ['exclusions', 'general', 'table_data', 'sub-limits', 'waiting period']:
                applicable.append(clause)
            # Include coverage-related clauses
            elif section in ['coverage', 'benefits', 'notes']:
                applicable.append(clause)
            # For cancer cases, include any clause that might be relevant
            elif is_cancer and 'cancer' in str(clause).lower():
                applicable.append(clause)

        return applicable

    def _check_exclusions(self, applicable_clauses: List[Dict], medical_record: Dict) -> Optional[AdjudicationResult]:
        """Check if claim is excluded (highest priority rule)"""
        exclusions = []

        for clause in applicable_clauses:
            if clause.get('section', '').lower() == 'exclusions':
                exclusions.append(clause)

        if exclusions:
            excluded_components = []
            for excl in exclusions:
                # Check if exclusion applies based on medical data
                if self._exclusion_applies(excl, medical_record):
                    excluded_components.append(excl.get('raw_text', '')[:100])

            if excluded_components:
                return AdjudicationResult(
                    decision=Decision.DENIED,
                    reason=f"Claim denied due to policy exclusions: {', '.join(excluded_components)}",
                    covered_components=[],
                    excluded_components=excluded_components,
                    applicable_clauses=exclusions,
                    confidence_score=0.9
                )

        return None

    def _check_waiting_periods(self, applicable_clauses: List[Dict], patient_data: Dict) -> Optional[AdjudicationResult]:
        """Check waiting period violations"""
        medical_icd = patient_data.get('final_icd', '') or ''
        is_cancer = medical_icd.startswith(('C', 'D')) and len(medical_icd) >= 3

        for clause in applicable_clauses:
            rule_logic = clause.get('rule_logic', {})
            waiting_periods = rule_logic.get('waiting_periods', [])

            for waiting_period in waiting_periods:
                if isinstance(waiting_period, dict) and self._waiting_period_applies(waiting_period, patient_data):
                    return AdjudicationResult(
                        decision=Decision.DENIED,
                        reason=f"Claim denied due to waiting period violation: {waiting_period.get('condition', 'Unknown condition')}",
                        covered_components=[],
                        excluded_components=[clause.get('raw_text', '')[:100]],
                        applicable_clauses=[clause],
                        confidence_score=0.8
                    )

        return None

    def _check_limits(self, applicable_clauses: List[Dict], medical_record: Dict) -> Optional[AdjudicationResult]:
        """Check if claim exceeds policy limits - only for broadly applicable limits"""
        total_cost = self._extract_total_cost(medical_record)

        for clause in applicable_clauses:
            # Only check limits for general policy sub-limits section
            section = clause.get('section', '').lower()
            if 'sub-limit' not in section and 'limit' not in section:
                continue
                
            # Skip condition-specific limits unless they explicitly match the ICD
            clause_text = clause.get('raw_text', '').lower()
            
            # Skip condition-specific limits
            specific_conditions = ['cataract', 'mtmat', 'road ambulance', 'home care', 'icu', 'iccu', 'dialysis', 'chemotherapy']
            if any(cond in clause_text for cond in specific_conditions):
                continue
            
            rule_logic = clause.get('rule_logic', {})
            limits = rule_logic.get('limits', [])
            if not isinstance(limits, list):
                continue
            for limit in limits:
                if not isinstance(limit, dict):
                    continue
                if self._limit_exceeded(limit, total_cost, medical_record):
                    return AdjudicationResult(
                        decision=Decision.PARTIALLY_COVERED,
                        reason=f"Claim partially covered - exceeds policy limits: {limit.get('type', 'Unknown limit')}",
                        covered_components=[clause.get('raw_text', '')[:100]],
                        excluded_components=[],
                        applicable_clauses=[clause],
                        confidence_score=0.7
                    )

        return None

    def _check_coverage(self, applicable_clauses: List[Dict], medical_record: Dict) -> AdjudicationResult:
        """Check coverage conditions (lowest priority rule) - if we got here, claim is approved by default"""
        # Check for inconclusive diagnosis or pending further evaluation
        pathology = (medical_record.get('pathalogy_test_notes_and_findings', '') or 
                     medical_record.get('pathology_findings', '')).lower()
        recommendations = (medical_record.get('recommendations', '') or 
                          medical_record.get('recommendation', '')).lower()
        
        # Keywords indicating inconclusive or pending diagnosis
        inconclusive_keywords = ['inconclusive', 'non-typical', 'rule', 'pending', 'further correlation', 'further histopathological', 'unclear']
        is_inconclusive = any(kw in pathology for kw in inconclusive_keywords) or any(kw in recommendations for kw in inconclusive_keywords)
        
        procedures = medical_record.get('procedure_performed', [])
        medications = medical_record.get('medication_prescribed', []) or medical_record.get('medication_prescribed_with_dosage', [])
        
        # If diagnosis is inconclusive, requires manual review
        if is_inconclusive:
            return AdjudicationResult(
                decision=Decision.MANUAL_REVIEW,
                reason="Coverage unclear - pathology findings inconclusive; further evaluation required",
                covered_components=[],
                excluded_components=[],
                applicable_clauses=applicable_clauses,
                confidence_score=0.5
            )
        
        # If no procedures/medications and no clear diagnosis, requires manual review
        if not procedures and not medications:
            return AdjudicationResult(
                decision=Decision.MANUAL_REVIEW,
                reason="Coverage unclear - requires manual review of policy terms",
                covered_components=[],
                excluded_components=[],
                applicable_clauses=applicable_clauses,
                confidence_score=0.4
            )
        
        # Check for partial coverage scenario (claimed_amount > approved_amount)
        claimed_amount = medical_record.get('claimed_amount', 0)
        approved_amount = medical_record.get('approved_amount', 0)
        
        if procedures or medications:
            # If there's a gap between claimed and approved, it's partially covered
            if claimed_amount > 0 and approved_amount > 0 and claimed_amount > approved_amount:
                return AdjudicationResult(
                    decision=Decision.PARTIALLY_COVERED,
                    reason=f"Claim partially covered - approved Rs. {approved_amount}, claimed Rs. {claimed_amount}",
                    covered_components=[c.get('raw_text', '')[:100] for c in applicable_clauses if 'coverage' in c.get('section', '').lower() or 'benefits' in c.get('section', '').lower()],
                    excluded_components=[],
                    applicable_clauses=applicable_clauses,
                    confidence_score=0.75
                )
            
            # Otherwise, fully covered
            return AdjudicationResult(
                decision=Decision.APPROVED,
                reason="Claim approved - covered under policy terms",
                covered_components=[c.get('raw_text', '')[:100] for c in applicable_clauses if 'coverage' in c.get('section', '').lower() or 'benefits' in c.get('section', '').lower()],
                excluded_components=[],
                applicable_clauses=applicable_clauses,
                confidence_score=0.85
            )

    def _exclusion_applies(self, exclusion_clause: Dict, medical_record: Dict) -> bool:
        """Check if exclusion applies to the medical case"""
        exclusion_text = exclusion_clause.get('raw_text', '').lower()

        # Check for investigation/evaluation exclusion (Excl04)
        if 'investigation' in exclusion_text and 'evaluation' in exclusion_text:
            # Check if the medical record indicates only investigation without treatment
            procedures = medical_record.get('procedure_performed', [])
            medication = medical_record.get('medication_prescribed', []) or medical_record.get('medication_prescribed_with_dosage', [])
            if not procedures and not medication:
                return True

        # Check for rest cure/rehabilitation exclusion (Excl05)
        if 'rest cure' in exclusion_text or 'rehabilitation' in exclusion_text:
            if 'rest' in str(medical_record).lower() or 'rehabilitation' in str(medical_record).lower():
                return True

        # Check for cosmetic/plastic surgery exclusion
        if 'cosmetic' in exclusion_text or 'plastic surgery' in exclusion_text:
            if 'cosmetic' in str(medical_record).lower() or 'plastic' in str(medical_record).lower():
                return True

        # Check for pre-existing condition exclusion
        if 'pre-existing' in exclusion_text:
            if self._is_pre_existing(medical_record):
                return True

        # Check for self-inflicted injury exclusion
        if 'self-inflicted' in exclusion_text:
            if 'self-inflicted' in str(medical_record).lower():
                return True

        return False

    def _waiting_period_applies(self, waiting_period: Dict, patient_data: Dict) -> bool:
        """Check if waiting period applies"""
        condition = waiting_period.get('condition', '').lower()
        months_required = waiting_period.get('months', 0)
        months_elapsed = patient_data.get('months_since_policy_start', 0)

        # For cancer cases, don't apply general waiting periods
        medical_icd = patient_data.get('final_icd', '') or ''
        is_cancer = medical_icd.startswith(('C', 'D')) and len(medical_icd) >= 3
        if is_cancer and 'general' in condition:
            return False

        # Check for pre-existing condition
        if 'pre_existing' in condition and self._is_pre_existing(patient_data):
            # Check if policy has specific waiting period
            policy_waiting_period = patient_data.get('policy_waiting_period_months', months_required)
            if months_elapsed < policy_waiting_period:
                return True

        # Check for specific conditions (like hernia)
        if 'hernia' in condition and 'hernia' in str(patient_data).lower():
            if months_elapsed < months_required:
                return True

        # Check for general waiting periods only if months_elapsed is provided and less than required
        if 'general' in condition and months_elapsed > 0 and months_elapsed < months_required:
            return True

        return False

    def _limit_exceeded(self, limit: Dict, total_cost: float, medical_record: Dict) -> bool:
        """Check if claim exceeds policy limits"""
        limit_type = limit.get('type', '')
        if '|' in limit_type:
            # Handle multiple types
            limit_types = limit_type.split('|')
        else:
            limit_types = [limit_type]
        
        limit_value = limit.get('value', 0)
        # Convert string values to int/float
        if isinstance(limit_value, str):
            try:
                limit_value = float(limit_value)
            except ValueError:
                return False

        for lt in limit_types:
            if lt == 'fixed_amount' and total_cost > limit_value:
                return True
            if lt == 'percentage':
                percentage_of = limit.get('percentage_of', 'SI')
                if percentage_of == 'SI' and total_cost > limit_value:
                    return True

        return False

    def _coverage_applies(self, coverage_clause: Dict, medical_record: Dict) -> bool:
        """Check if coverage applies"""
        rule_logic = coverage_clause.get('rule_logic', {})
        coverage_conditions = rule_logic.get('coverage_conditions', [])

        for condition in coverage_conditions:
            condition_type = condition.get('type', '')

            if condition_type == 'treatment_type':
                required_treatments = condition.get('treatment_types', [])
                medical_treatments = medical_record.get('procedure_performed', []) + medical_record.get('medication_prescribed', [])
                if any(rt in str(medical_treatments) for rt in required_treatments):
                    return True

            if condition_type == 'hospitalization':
                requires_hosp = condition.get('requires_hospitalization', False)
                if requires_hosp and 'hospital' in str(medical_record).lower():
                    return True

        return True  # Default to covered if no specific conditions

    def _is_pre_existing(self, data: Dict) -> bool:
        """Check if condition is pre-existing"""
        medical_history = str(data.get('medical_history', '')).lower()
        if 'prior' in medical_history or 'previous' in medical_history:
            return True
        if 'history' in medical_history and 'no' not in medical_history:
            return True
        return False

    def _extract_total_cost(self, medical_record: Dict) -> float:
        """Extract total cost from medical record"""
        return medical_record.get('total_estimated_cost', 0) or medical_record.get('claimed_amount', 0)

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python main.py <medical_record.json>")
        print("Example: python main.py medical_record.json")
        return
    
    json_file = sys.argv[1]
    
    print("=== Claim Adjudication System ===\n")

    # Load policy data
    try:
        policy_data = load_policy_data()
        print(f"Loaded policy: {policy_data['policy_file']} with {policy_data['total_clauses']} clauses\n")
    except FileNotFoundError:
        print("❌ Error: parsed_policies.json not found. Run parse_policies.py first.")
        return

    # Initialize adjudicator
    adjudicator = ClaimAdjudicator()

    # Process the medical record
    print(f"Processing: {json_file}")
    print("=" * 50)
    try:
        # Process the medical record through full pipeline
        medical_record = process_medical_record(json_file)
        
        if not medical_record or medical_record.get('final_icd') is None:
            print(f"❌ Failed to process {json_file} - no valid medical record returned")
            return

        # Display medical processing results
        print(f"🔍 ICD: {medical_record.get('final_icd', 'Unknown')}")
        print(f"📊 Confidence: {medical_record.get('confidence', 'Unknown')}")
        print(f"🩺 Reasoning: {medical_record.get('reasoning', 'No reasoning')[:200]}...")

        # Run adjudication
        result = adjudicator.adjudicate_claim(medical_record, policy_data['clauses'])

        # Map result to expected format
        decision_map = {
            'approved': 'covered',
            'denied': 'not_covered',
            'partially_covered': 'partially_covered',
            'manual_review': 'unsure'
        }
        actual = decision_map.get(result.decision.value, 'unsure')

        # Display adjudication results
        print(f"\n🎯 Decision: {result.decision.value.upper()} ({actual})")
        print(f"💡 Reason: {result.reason}")
        print(f"🎚️ Confidence: {result.confidence_score:.1%}")

        if result.covered_components:
            print(f"✅ Covered Components ({len(result.covered_components)}):")
            for comp in result.covered_components[:5]:
                print(f"  • {comp[:100]}...")

        if result.excluded_components:
            print(f"❌ Excluded Components ({len(result.excluded_components)}):")
            for comp in result.excluded_components[:5]:
                print(f"  • {comp[:100]}...")

        print(f"📄 Applicable Clauses: {len(result.applicable_clauses)}")

        print("\n" + "="*50)
        print("✅ Processing completed successfully!")

    except Exception as e:
        print(f"❌ Error processing {json_file}: {str(e)}")
        return

if __name__ == "__main__":
    main()