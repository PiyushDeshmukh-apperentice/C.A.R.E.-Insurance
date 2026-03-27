import os
import uuid
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime
from sqlalchemy.orm import Session
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA256 hash of file content"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

from models import (
    Claim, ClaimDecision, DecisionEvidence, ClaimDocument, AuditLog, get_audit_db,
    AutomobileClaim, AutomobileDocument, AutomobileClaimDecision, AutomobileDecisionEvidence,
    UserPolicy, Policy
)
from config import UPLOAD_DIR, MAX_FILES_PER_CLAIM, SUPPORTED_FILE_TYPES
from health_claim_engine.main_workflow import ClaimAutomationWorkflow
from health_claim_engine.config import GROQ_API_KEY
import sys
sys.path.insert(0, str(project_root / "automobile_claim_engine"))
from claim_engine import process_automobile_claim

def validate_files(files: List, expected_count: int = MAX_FILES_PER_CLAIM) -> List[str]:
    """Validate uploaded files"""
    errors = []
    if len(files) != expected_count:
        errors.append(f"Exactly {expected_count} files required")
    for file in files:
        if not any(file.filename.endswith(ext) for ext in SUPPORTED_FILE_TYPES):
            errors.append(f"Unsupported file type: {file.filename}")
    return errors

def save_uploaded_files(files: List, claim_id: str) -> List[Dict[str, Any]]:
    """Save uploaded files with specific names and return document info"""
    # Create claim directory
    claim_dir = UPLOAD_DIR / claim_id
    claim_dir.mkdir(exist_ok=True)

    # Map file positions to specific names and document types
    file_mappings = [
        {"name": "admission note", "type": "discharge_summary"},
        {"name": "prescription", "type": "prescription"},
        {"name": "pathology report", "type": "lab_report"},
        {"name": "imaging report", "type": "imaging_report"},
        {"name": "discharge summary", "type": "discharge_summary"},
        {"name": "bill", "type": "bill"},
        {"name": "insurance document", "type": "bill"}
    ]

    if len(files) != len(file_mappings):
        raise ValueError(f"Expected {len(file_mappings)} files, got {len(files)}")

    documents = []
    for i, file in enumerate(files):
        mapping = file_mappings[i]
        file_name = mapping["name"]
        doc_type = mapping["type"]
        file_extension = Path(file.filename).suffix
        file_path = claim_dir / f"{file_name}{file_extension}"

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        file_hash = calculate_file_hash(str(file_path))

        documents.append({
            "type": doc_type,
            "path": str(file_path),
            "hash": file_hash,
            "original_name": file.filename
        })

    return documents

def save_automobile_claim_files(files: List, claim_id: str) -> List[Dict[str, Any]]:
    """Save automobile claim files (single vehicle image)"""
    claim_dir = UPLOAD_DIR / claim_id
    claim_dir.mkdir(exist_ok=True)

    if len(files) != 1:
        raise ValueError(f"Expected 1 file for automobile claim, got {len(files)}")

    documents = []
    file = files[0]

    file_extension = Path(file.filename).suffix
    file_path = claim_dir / f"vehicle_image{file_extension}"

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    file_hash = calculate_file_hash(str(file_path))

    documents.append({
        "type": file.filename.split('.')[-1].upper(),
        "path": str(file_path),
        "hash": file_hash,
        "original_name": file.filename
    })

    return documents

def process_automobile_claim_with_engine(claim_data: Dict[str, Any], documents: List[Dict[str, Any]], vehicle_type: str) -> Dict[str, Any]:
    """Process automobile claim using automobile claim engine"""
    print("🔄 STARTING process_automobile_claim_with_engine")
    try:
        automobile_engine_path = Path(__file__).parent.parent / "automobile_claim_engine"
        sys.path.insert(0, str(automobile_engine_path))
        from claim_engine import process_automobile_claim

        # Get vehicle image path from documents
        vehicle_image_path = None
        if documents and len(documents) > 0:
            vehicle_image_path = documents[0].get("path")
        
        print(f"📷 Vehicle image path: {vehicle_image_path}")
        
        # Process with image path
        result_claim_data, result, image_result = process_automobile_claim(
            claim_data, 
            claim_data.get("driver"), 
            vehicle_type,
            image_path=vehicle_image_path
        )

        # Build response with image information
        response = {
            "policy_decision": result["policy_decision"],
            "cost_estimation": result["cost_estimation"],
            "image_result": None
        }
        
        # Add image result if available
        if image_result:
            response["image_result"] = {
                "output_image_path": image_result.get("output_image_path"),
                "damage_data": image_result.get("damage_data")
            }
            print(f"✅ Image processed: {image_result.get('output_image_path')}")
        
        return response

    except Exception as e:
        import traceback
        print(f"AUTOMOBILE CLAIM PROCESSING ERROR: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")

        return {
            "policy_decision": {
                "decision": "FAILED", 
                "confidence": 0.0, 
                "reason": f"Processing failed: {str(e)}"
            },
            "cost_estimation": {"total_estimated_cost": 0, "cost_breakdown": []},
            "image_result": None
        }

def process_health_claim_with_engine(documents: List[Dict[str, Any]], policy_name: str) -> Dict[str, Any]:
    """Process health claim using health claim engine"""
    print("🔄 STARTING process_health_claim_with_engine")
    try:
        temp_dir = project_root / "temp" / f"temp_claim_{uuid.uuid4().hex[:8]}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        for doc in documents:
            src_path = Path(doc["path"])
            dst_path = temp_dir / src_path.name
            import shutil
            shutil.copy2(src_path, dst_path)

        policy_path = None
        policy_dir = project_root / "health_claim_engine" / "data"

        if policy_dir.exists():
            pdf_files = list(policy_dir.glob("*.pdf"))
            for pdf_file in pdf_files:
                if policy_name.lower() in pdf_file.name.lower():
                    policy_path = str(pdf_file)
                    break

        if not policy_path:
            available = [f.name for f in policy_dir.glob("*.pdf")] if policy_dir.exists() else []
            raise ValueError(f"Policy '{policy_name}' not found. Available: {available}")

        original_cwd = os.getcwd()
        os.chdir(project_root)

        try:
            workflow = ClaimAutomationWorkflow(GROQ_API_KEY)
            workflow.run_workflow(str(temp_dir), policy_path)
        finally:
            os.chdir(original_cwd)

        output_dir = project_root / "health_claim_engine" / "output"

        if output_dir.exists():
            result_files = list(output_dir.glob("adjudication_result_*.json"))
            if result_files:
                latest_result = max(result_files, key=lambda p: p.stat().st_mtime)
                with open(latest_result, 'r') as f:
                    result_data = json.load(f)

                import shutil
                shutil.rmtree(temp_dir)

                adjudication = result_data.get("adjudication", {})
                medical_record = result_data.get("medical_record", {})

                decision_map = {
                    "approved": "APPROVED",
                    "denied": "DENIED",
                    "partially_covered": "PARTIALLY_APPROVED",
                    "manual_review": "PENDING_REVIEW"
                }
                decision = decision_map.get(adjudication.get("decision", "manual_review"), "PENDING_REVIEW")

                diagnosis = None
                if medical_record.get("final_icd"):
                    diagnosis = {
                        "icd_code": medical_record["final_icd"],
                        "description": medical_record.get("icd_description", "Diagnosis identified")
                    }

                decision_reasons = []
                if adjudication.get("reason"):
                    decision_type = "coverage" if decision == "APPROVED" else "exclusion" if decision == "DENIED" else "review"
                    decision_reasons.append({
                        "type": decision_type,
                        "description": adjudication["reason"]
                    })

                applied_clauses = []
                covered = adjudication.get("covered_components", [])
                excluded = adjudication.get("excluded_components", [])

                for component in covered:
                    applied_clauses.append({
                        "clause_id": "COV01",
                        "policy_page": 1,
                        "text": f"Coverage for {component}"
                    })

                for component in excluded:
                    applied_clauses.append({
                        "clause_id": "EXCL01",
                        "policy_page": 1,
                        "text": f"Exclusion for {component}"
                    })

                if not applied_clauses:
                    if decision == "APPROVED":
                        applied_clauses.append({"clause_id": "GEN01", "policy_page": 1, "text": "General coverage"})
                    elif decision == "DENIED":
                        applied_clauses.append({"clause_id": "EXCL01", "policy_page": 1, "text": "Policy exclusions"})
                    else:
                        applied_clauses.append({"clause_id": "REV01", "policy_page": 1, "text": "Manual review required"})

                return {
                    "decision": decision,
                    "confidence": adjudication.get("confidence_score", 0.5),
                    "summary": adjudication.get("reason", "Claim processed"),
                    "diagnosis": diagnosis,
                    "decision_reasons": decision_reasons,
                    "applied_clauses": applied_clauses,
                    "ignored_exclusions": [],
                    "audit_reference_id": f"AUD_{uuid.uuid4().hex[:6].upper()}"
                }

        raise Exception("No result generated")

    except Exception as e:
        try:
            if 'temp_dir' in locals() and temp_dir.exists():
                import shutil
                shutil.rmtree(temp_dir)
        except:
            pass
        
        import traceback
        print(f"HEALTH CLAIM PROCESSING ERROR: {str(e)}")
        return {
            "decision": "FAILED",
            "confidence": 0.0,
            "summary": f"Processing failed: {str(e)}",
            "diagnosis": None,
            "decision_reasons": [],
            "applied_clauses": [],
            "ignored_exclusions": [],
            "audit_reference_id": f"AUD_{uuid.uuid4().hex[:6].upper()}"
        }

def create_health_claim_record(db: Session, claim_id: str, user_id: str, policy_name: str,
                              documents: List[Dict[str, Any]], processing_result: Dict[str, Any]) -> Claim:
    """Create health claim record in database"""

    user_policy = db.query(UserPolicy).join(Policy).filter(
        UserPolicy.user_id == user_id,
        Policy.policy_name == policy_name
    ).first()

    if not user_policy:
        logger.warning(f"No policy found for user {user_id} with name: {policy_name}, creating dummy policy")
        policy = db.query(Policy).filter(Policy.policy_name == policy_name).first()
        if not policy:
            policy = Policy(
                id=f"POLICY_{uuid.uuid4().hex[:8].upper()}",
                policy_name=policy_name,
                policy_type="health",
                insurer="Test Insurer",
                document_path=f"{policy_name}.pdf"
            )
            db.add(policy)
            db.flush()

        user_policy = UserPolicy(
            user_id=user_id,
            policy_id=policy.id,
            policy_number=f"TEST_{uuid.uuid4().hex[:6].upper()}",
            start_date=datetime.now().date(),
            end_date=(datetime.now().date().replace(year=datetime.now().year + 1)),
            sum_insured=500000,
            status="active"
        )
        db.add(user_policy)
        db.flush()

    # Ensure decision string matches DB constraint (lowercase)
    decision_str = processing_result.get("decision", "unsure").lower()
    if decision_str not in ['approved', 'partially_approved', 'denied', 'unsure']:
        decision_str = 'unsure'

    claim = Claim(
        id=claim_id,
        user_id=user_id,
        user_policy_id=user_policy.id,
        claim_type="health",
        claim_status=decision_str if decision_str in ['approved', 'rejected'] else "processing",
        created_at=datetime.utcnow()
    )
    db.add(claim)

    decision = ClaimDecision(
        claim_id=claim_id,
        decision=decision_str,
        reason=processing_result.get("summary", ""),
        confidence_score=processing_result.get("confidence", 0.0)
    )
    db.add(decision)
    db.flush()

    for clause in processing_result.get("applied_clauses", []):
        evidence = DecisionEvidence(
            decision_id=decision.id,
            clause_id=clause.get("clause_id", ""),
            clause_text=clause.get("text", ""),
            policy_page=clause.get("policy_page"),
            rule_type="coverage"
        )
        db.add(evidence)

    for doc in documents:
        doc_record = ClaimDocument(
            claim_id=claim_id,
            document_type=doc["type"].lower(),
            file_path=doc["path"]
        )
        db.add(doc_record)

    audit_db = next(get_audit_db())
    audit_entry = AuditLog(
        actor_type="user",
        actor_id=user_id,
        action="health_claim_submitted",
        resource=f"health_claim:{claim_id}",
        outcome="success"
    )
    audit_db.add(audit_entry)
    audit_db.commit()

    db.commit()
    db.refresh(claim)
    return claim

def create_automobile_claim_record(db: Session, claim_id: str, user_id: str, vehicle_type: str, policy_name: str,
                                  documents: List[Dict[str, Any]], processing_result: Dict[str, Any]) -> AutomobileClaim:
    """Create automobile claim record in database"""

    policy_decision = processing_result.get("policy_decision", {})
    cost_estimation = processing_result.get("cost_estimation", {})
    image_result = processing_result.get("image_result")

    # Extract output image path
    output_image_path = None
    if image_result and image_result.get("output_image_path"):
        output_image_path = image_result["output_image_path"]
        print(f"💾 Saving output image path to database: {output_image_path}")

    claim = AutomobileClaim(
        id=claim_id,
        user_id=user_id,
        policy_name=policy_name,
        vehicle_type=vehicle_type,
        vehicle_category="private",
        vehicle_usage="private",
        status="completed",
        confidence=policy_decision.get("confidence", 0.0),
        processed_at=datetime.utcnow(),
        output_image_path=output_image_path  # Store output image path
    )
    db.add(claim)

    decision = AutomobileClaimDecision(
        claim_id=claim_id,
        decision=policy_decision.get("decision", "UNKNOWN"),
        reason=policy_decision.get("reason", ""),
        confidence=policy_decision.get("confidence", 0.0),
        estimated_cost=cost_estimation.get("total_estimated_cost"),
        approved_amount=cost_estimation.get("total_estimated_cost") if policy_decision.get("decision") == "APPROVED" else 0
    )
    db.add(decision)
    db.flush() # CRITICAL: Flush to get decision.id for evidence linking

    # Add cost breakdown as evidences
    for item in cost_estimation.get("cost_breakdown", []):
        evidence = AutomobileDecisionEvidence(
            claim_id=claim_id,
            decision_id=decision.id, # FIXED: Linked to decision
            clause_id="COST01",
            clause_text=f"Cost for {item.get('part', 'part')}: {item.get('estimated_cost', 0)}",
            policy_page=1,
            match_type="coverage"
        )
        db.add(evidence)

    # Add damage data as evidence if available
    if image_result and image_result.get("damage_data"):
        damage_data = image_result["damage_data"]
        evidence = AutomobileDecisionEvidence(
            claim_id=claim_id,
            decision_id=decision.id,
            clause_id="DMG01",
            clause_text=f"Damage type: {damage_data.get('type', 'unknown')}. Damaged parts: {len(damage_data.get('damaged_parts', []))}",
            policy_page=1,
            match_type="coverage"
        )
        db.add(evidence)

    for doc in documents:
        doc_record = AutomobileDocument(
            user_id=user_id,
            claim_id=claim_id, # FIXED: Linked to claim
            document_type=doc["type"],
            file_path=doc["path"],
            file_hash=doc["hash"]
        )
        db.add(doc_record)

    audit_entry = AuditLog(
        actor_type="user",
        actor_id=user_id,
        action="automobile_claim_submitted",
        resource=f"automobile_claim:{claim_id}",
        outcome="success"
    )
    audit_db = next(get_audit_db())
    audit_db.add(audit_entry)
    audit_db.commit()

    db.commit()
    db.refresh(claim)
    return claim