from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
import traceback
import json
import uuid
from datetime import datetime

from models import (
    get_db, get_audit_db, create_tables, User, Claim, AuditLog, ClaimDecision, DecisionEvidence,
    OTPRequest, Policy, UserPolicy, ClaimDocument,
    AutomobileClaim, AutomobileDocument, AutomobileClaimDecision, AutomobileDecisionEvidence
)
from auth import create_user, authenticate_user, create_access_token, verify_token, create_otp_request, verify_user_otp
from claim_processor import (
    validate_files, save_uploaded_files,
    process_health_claim_with_engine, create_health_claim_record,
    process_automobile_claim_with_engine, create_automobile_claim_record,
    save_automobile_claim_files
)
from config import SERVER_HOST, SERVER_PORT, SUPPORTED_FILE_TYPES

# Initialize database
create_tables()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Claim Automation API",
    description="Simple claim processing API for academic project",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Dependency to get current user
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# User registration
@app.post("/auth/signup")
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """User signup with OTP verification (simplified for academic project)"""
    existing = db.query(User).filter(
        (User.username == username) | (User.email == email) | (User.mobile == mobile)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = create_user(db, username, email, mobile, password)
    email_otp = create_otp_request(db, user.id, "email")
    sms_otp = create_otp_request(db, user.id, "sms")

    return {
        "message": "User created. Verify with OTPs.",
        "user_id": user.id,
        "email_otp": email_otp, 
        "sms_otp": sms_otp       
    }

# OTP verification
@app.post("/auth/verify")
async def verify_otp(
    user_id: str = Form(...),
    email_otp: str = Form(...),
    sms_otp: str = Form(...),
    db: Session = Depends(get_db)
):
    email_verified = verify_user_otp(db, user_id, email_otp, "email")
    sms_verified = verify_user_otp(db, user_id, sms_otp, "sms")

    if not (email_verified and sms_verified):
        raise HTTPException(status_code=400, detail="Invalid OTPs")

    return {"message": "Account verified successfully"}

# User login
@app.post("/auth/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }

# Submit health claim
@app.post("/health-claims/submit")
async def submit_health_claim(
    email: str = Form(...),
    policy_name: str = Form(...),
    admission_note: UploadFile = File(...),
    prescription: UploadFile = File(...),
    imaging_report: UploadFile = File(...),
    pathology_report: UploadFile = File(...),
    discharge_summary: UploadFile = File(...),
    bill: UploadFile = File(...),
    insurance: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"--- RECEIVED HEALTH CLAIM SUBMISSION ---")
    logger.info(f"User: {email}, Policy: {policy_name}")

    if current_user.email != email:
        raise HTTPException(status_code=403, detail="Can only submit claims for yourself")

    files = [admission_note, prescription, imaging_report, pathology_report, discharge_summary, bill, insurance]
    validation_errors = validate_files(files)
    if validation_errors:
        raise HTTPException(status_code=400, detail=validation_errors)

    try:
        logger.info("Saving uploaded files...")
        claim_id = f"HEALTH_CLAIM_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        documents = save_uploaded_files(files, claim_id)

        logger.info("Starting health claim processing...")
        try:
            processing_result = process_health_claim_with_engine(documents, policy_name)
        except ValueError as ve:
            processing_result = {
                "decision": "FAILED",
                "confidence": 0.0,
                "summary": str(ve), 
                "diagnosis": "",
                "decision_reasons": [],
                "applied_clauses": [],
                "ignored_exclusions": [],
                "audit_reference_id": f"AUD_{uuid.uuid4().hex[:6].upper()}"
            }

        claim = create_health_claim_record(db, claim_id, current_user.id, policy_name, documents, processing_result)

        result = {
            "claim_id": claim.id,
            "decision": processing_result["decision"],
            "confidence": processing_result["confidence"],
            "summary": processing_result["summary"],
            "diagnosis": processing_result["diagnosis"],
            "decision_reasons": processing_result["decision_reasons"],
            "applied_clauses": processing_result["applied_clauses"],
            "ignored_exclusions": processing_result["ignored_exclusions"],
            "audit_reference_id": processing_result["audit_reference_id"]
        }
        return result
        
    except Exception as e:
        logger.error(f"System Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Submit automobile claim
@app.post("/automobile-claims/submit")
async def submit_automobile_claim(
    email: str = Form(...),
    event_date: str = Form(...),
    event_time: str = Form(...),
    activity: str = Form(...),
    street: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    driver_name: str = Form(...),
    driver_age: int = Form(...),
    driver_gender: str = Form(...),
    licensed: bool = Form(...),
    experience_years: int = Form(...),
    under_influence: bool = Form(...),
    policy_name: str = Form(...),
    vehicle_image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"--- RECEIVED AUTOMOBILE CLAIM SUBMISSION ---")
    
    if current_user.email != email:
        raise HTTPException(status_code=403, detail="Can only submit claims for yourself")

    if driver_gender not in ["male", "female", "other"]:
        raise HTTPException(status_code=400, detail="Invalid driver gender")

    files = [vehicle_image]
    validation_errors = validate_files(files, 1)
    if validation_errors:
        raise HTTPException(status_code=400, detail=validation_errors)

    try:
        logger.info("Saving uploaded files...")
        claim_id = f"AUTO_CLAIM_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        documents = save_automobile_claim_files(files, claim_id)

        event_data = {
            "date": event_date,
            "time": event_time,
            "activity": activity,
            "location": {"street": street, "city": city, "state": state},
            "driver": {
                "name": driver_name,
                "age": driver_age,
                "gender": driver_gender,
                "licensed": licensed,
                "experience_years": experience_years,
                "under_influence": under_influence
            },
            "policy_name": policy_name
        }

        logger.info("Starting automobile claim processing...")
        processing_result = process_automobile_claim_with_engine(event_data, documents)
        
        vehicle_type = "car" 
        claim = create_automobile_claim_record(db, claim_id, current_user.id, vehicle_type, policy_name, documents, processing_result)

        policy_decision = processing_result.get("policy_decision", {})
        cost_estimation = processing_result.get("cost_estimation", {})
        image_result = processing_result.get("image_result")

        result = {
            "claim_id": claim.id,
            "decision": policy_decision.get("decision", "UNKNOWN"),
            "confidence": policy_decision.get("confidence", 0.0),
            "summary": policy_decision.get("reason", "Claim processed"),
            "estimated_cost": cost_estimation.get("total_estimated_cost", 0),
            "cost_breakdown": cost_estimation.get("cost_breakdown", []),
            "output_image_path": image_result.get("output_image_path") if image_result else None,
            "damage_analysis": image_result.get("damage_data") if image_result else None,
            "audit_reference_id": f"AUD_{uuid.uuid4().hex[:6].upper()}"
        }
        return result

    except Exception as e:
        logger.error(f"System Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/claims")
async def get_user_claims(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    claims = db.query(Claim).filter(Claim.user_id == current_user.id).all()
    result = []
    for claim in claims:
        user_policy = db.query(UserPolicy).filter(UserPolicy.id == claim.user_policy_id).first()
        policy = db.query(Policy).filter(Policy.id == user_policy.policy_id).first() if user_policy else None
        result.append({
            "claim_id": claim.id,
            "policy_name": policy.policy_name if policy else "Unknown",
            "claim_type": claim.claim_type,
            "claim_status": claim.claim_status,
            "created_at": claim.created_at,
            "decision": claim.decision.decision if claim.decision else None
        })
    return {"claims": result}

# --- IMPROVED DETAIL ROUTE ---
@app.get("/claims/{claim_id}")
async def get_claim_details(
    claim_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    audit_db: Session = Depends(get_audit_db)
):
    """Get detailed health claim information (Cleaned up)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim or claim.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Claim not found")

    policy_name = "Unknown"
    if claim.user_policy and claim.user_policy.policy:
        policy_name = claim.user_policy.policy.policy_name

    # Removed hardcoded Hospital info
    result = {
        "claim_id": claim.id,
        "policy_name": policy_name,
        "status": claim.claim_status,
        "created_at": claim.created_at,
        "confidence": 0.0
    }

    result["applied_clauses"] = []
    
    if claim.decision:
        result["confidence"] = claim.decision.confidence_score * 100
        result["decision"] = {
            "decision": claim.decision.decision,
            "reason": claim.decision.reason,
            "confidence": claim.decision.confidence_score * 100,
            # We pass this, but Frontend/Bot will hide it if N/A
            "diagnosis": {"icd_code": "N/A", "description": "See summary"}
        }

        if claim.decision.evidences:
            for evidence in claim.decision.evidences:
                result["applied_clauses"].append({
                    "clause_id": evidence.clause_id,
                    "clause_text": evidence.clause_text,
                    "policy_page": evidence.policy_page,
                    "match_type": evidence.rule_type
                })

    return result

# --- FIX: ADDED AUTOMOBILE CLAIMS LIST ROUTE ---
@app.get("/automobile-claims")
async def get_user_automobile_claims(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's automobile claim history"""
    claims = db.query(AutomobileClaim).filter(AutomobileClaim.user_id == current_user.id).all()

    result = []
    for claim in claims:
        result.append({
            "claim_id": claim.id,
            "policy_name": claim.policy_name,
            "vehicle_type": claim.vehicle_type,
            "status": claim.status,
            "confidence": claim.confidence*100 if claim.confidence else 0.0,
            "created_at": claim.created_at,
            "decision": claim.decision.decision if claim.decision else None,
            "estimated_cost": claim.decision.estimated_cost if claim.decision else None,
            "claim_type": "auto" # Add explicit type marker
        })

    return {"claims": result}

@app.get("/automobile-claims/{claim_id}")
async def get_automobile_claim_details(
    claim_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    audit_db: Session = Depends(get_audit_db)
):
    """Get detailed automobile claim information"""
    claim = db.query(AutomobileClaim).filter(AutomobileClaim.id == claim_id).first()
    if not claim or claim.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Claim not found")

    result = {
        "claim_id": claim.id,
        "policy_name": claim.policy_name,
        "vehicle_type": claim.vehicle_type,
        "status": claim.status,
        "created_at": claim.created_at,
        "output_image_path": claim.output_image_path, 
        "confidence": (claim.confidence or 0.0) * 100
    }

    result["applied_clauses"] = []

    if claim.decision:
        result["decision"] = {
            "decision": claim.decision.decision,
            "reason": claim.decision.reason,
            "confidence": (claim.decision.confidence or 0.0) * 100,
            "estimated_cost": claim.decision.estimated_cost,
            "approved_amount": claim.decision.approved_amount
        }

        if claim.decision.evidences:
            for evidence in claim.decision.evidences:
                result["applied_clauses"].append({
                    "clause_id": evidence.clause_id,
                    "clause_text": evidence.clause_text,
                    "policy_page": evidence.policy_page,
                    "match_type": evidence.match_type
                })
    return result

@app.get("/policies")
async def get_user_policies(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_policies = db.query(UserPolicy).filter(
        UserPolicy.user_id == current_user.id,
        UserPolicy.status == "active"
    ).all()

    result = []
    for user_policy in user_policies:
        policy = user_policy.policy 
        if policy:
            result.append({
                "policy_name": policy.policy_name,
                "coverage_amount": user_policy.sum_insured, 
            })
    return {"policies": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)