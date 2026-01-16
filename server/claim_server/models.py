from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, CheckConstraint, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from config import DATABASE_URL, AUDIT_DATABASE_URL

# Database setup for app.db
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database setup for audit.db
audit_engine = create_engine(AUDIT_DATABASE_URL, connect_args={"check_same_thread": False})
AuditSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=audit_engine)
AuditBase = declarative_base()

# App Database Models

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # UUID
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    mobile = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    is_email_verified = Column(Boolean, default=False)
    is_mobile_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

    # Relationships
    policies = relationship("UserPolicy", back_populates="user")
    claims = relationship("Claim", back_populates="user")

class OTPRequest(Base):
    __tablename__ = "otp_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)

    otp_hash = Column(String, nullable=False)
    channel = Column(String, nullable=False)  # 'email' or 'sms'
    __table_args__ = (CheckConstraint("channel IN ('email', 'sms')"),)

    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, index=True)  # POLICY_HEALTH_001
    policy_name = Column(String, nullable=False)
    policy_type = Column(String, nullable=False)  # 'health' or 'auto'
    __table_args__ = (CheckConstraint("policy_type IN ('health', 'auto')"),)
    insurer = Column(String, nullable=False)

    document_path = Column(String, nullable=False)  # PDF location
    version = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user_policies = relationship("UserPolicy", back_populates="policy")

class UserPolicy(Base):
    __tablename__ = "user_policies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    policy_id = Column(String, ForeignKey("policies.id"), nullable=False)

    policy_number = Column(String, unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    sum_insured = Column(Integer, nullable=True)

    status = Column(String, nullable=True)  # 'active', 'expired', 'cancelled'
    __table_args__ = (CheckConstraint("status IN ('active', 'expired', 'cancelled')"),)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="policies")
    policy = relationship("Policy", back_populates="user_policies")
    claims = relationship("Claim", back_populates="user_policy")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_policy_id = Column(Integer, ForeignKey("user_policies.id"), nullable=True)

    claim_type = Column(String, nullable=True)  # 'cashless' or 'reimbursement'
    __table_args__ = (CheckConstraint("claim_type IN ('cashless', 'reimbursement')"),)
    claim_status = Column(String, nullable=True)  # 'submitted', 'processing', 'approved', 'rejected'
    __table_args__ = (CheckConstraint("claim_status IN ('submitted', 'processing', 'approved', 'rejected')"),)

    hospital_name = Column(String, nullable=True)
    admission_date = Column(Date, nullable=True)
    discharge_date = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="claims")
    user_policy = relationship("UserPolicy", back_populates="claims")
    documents = relationship("ClaimDocument", back_populates="claim")
    decision = relationship("ClaimDecision", back_populates="claim", uselist=False)

class ClaimDocument(Base):
    __tablename__ = "claim_documents"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)

    document_type = Column(String, nullable=True)  # 'bill', 'prescription', etc.
    __table_args__ = (CheckConstraint("document_type IN ('bill', 'prescription', 'lab_report', 'discharge_summary', 'imaging_report')"),)

    file_path = Column(String, nullable=False)
    extracted_json_path = Column(String, nullable=True)  # OCR + ML output
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    claim = relationship("Claim", back_populates="documents")

class ClaimDecision(Base):
    __tablename__ = "claim_decisions"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)

    decision = Column(String, nullable=True)  # 'approved', 'partially_approved', 'denied', 'unsure'
    __table_args__ = (CheckConstraint("decision IN ('approved', 'partially_approved', 'denied', 'unsure')"),)

    confidence_score = Column(Float, nullable=True)
    reason = Column(Text, nullable=True)  # Human-readable explanation

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    claim = relationship("Claim", back_populates="decision")
    evidences = relationship("DecisionEvidence", back_populates="decision")

class DecisionEvidence(Base):
    __tablename__ = "decision_evidences"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("claim_decisions.id"), nullable=False)

    clause_id = Column(String, nullable=True)
    clause_text = Column(Text, nullable=True)
    policy_page = Column(Integer, nullable=True)

    rule_type = Column(String, nullable=True)  # 'exclusion', 'waiting_period', 'coverage'
    explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    decision = relationship("ClaimDecision", back_populates="evidences")

# Automobile Claim Models

class AutomobileClaim(Base):
    __tablename__ = "automobile_claims"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    policy_name = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)  # 'car', 'bike', 'scooty'
    vehicle_category = Column(String, nullable=True)  # 'private', 'commercial', etc.
    vehicle_usage = Column(String, nullable=True)  # 'private', 'commercial', etc.
    status = Column(String, default="processing")  # 'processing', 'completed', 'failed'
    confidence = Column(Float, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    output_image_path = Column(String, nullable=True)  # Path to output image from damage analysis
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="automobile_claims")
    decision = relationship("AutomobileClaimDecision", back_populates="claim", uselist=False)
    documents = relationship("AutomobileDocument", back_populates="claim")

class AutomobileDocument(Base):
    __tablename__ = "automobile_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    claim_id = Column(String, ForeignKey("automobile_claims.id"), nullable=True)
    document_type = Column(String, nullable=False)  # 'accident_report', 'repair_estimate', 'police_report'
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="automobile_documents")
    claim = relationship("AutomobileClaim", back_populates="documents")

class AutomobileClaimDecision(Base):
    __tablename__ = "automobile_claim_decisions"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, ForeignKey("automobile_claims.id"), nullable=False)

    decision = Column(String, nullable=True)  # 'APPROVED', 'DENIED', 'PARTIALLY_APPROVED', 'PENDING_REVIEW'
    reason = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    approved_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    claim = relationship("AutomobileClaim", back_populates="decision")
    evidences = relationship("AutomobileDecisionEvidence", back_populates="decision")

class AutomobileDecisionEvidence(Base):
    __tablename__ = "automobile_decision_evidences"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String, ForeignKey("automobile_claims.id"), nullable=False)
    decision_id = Column(Integer, ForeignKey("automobile_claim_decisions.id"), nullable=True)

    clause_id = Column(String, nullable=True)
    clause_text = Column(Text, nullable=True)
    policy_page = Column(Integer, nullable=True)
    match_type = Column(String, nullable=True)  # 'coverage', 'exclusion'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    decision = relationship("AutomobileClaimDecision", back_populates="evidences")

# Update User model to include automobile relationships
User.automobile_claims = relationship("AutomobileClaim", back_populates="user")
User.automobile_documents = relationship("AutomobileDocument", back_populates="user")

# Audit Database Models

class AuditLog(AuditBase):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    actor_type = Column(String, nullable=True)  # 'user', 'system', 'admin'
    __table_args__ = (CheckConstraint("actor_type IN ('user', 'system', 'admin')"),)
    actor_id = Column(String, nullable=True)

    action = Column(String, nullable=True)  # 'login', 'upload', 'adjudicate'
    resource = Column(String, nullable=True)  # claim_id / policy_id
    outcome = Column(String, nullable=True)  # 'success' / 'failure'

    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)
    AuditBase.metadata.create_all(bind=audit_engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get audit DB session
def get_audit_db():
    db = AuditSessionLocal()
    try:
        yield db
    finally:
        db.close()