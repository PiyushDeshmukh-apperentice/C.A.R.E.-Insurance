from datetime import datetime, timedelta
from typing import Optional
import uuid
import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models import User, OTPRequest, AuditLog, AuditSessionLocal
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, OTP_EXPIRY_MINUTES

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

def generate_otp() -> str:
    """Generate a simple 6-digit OTP for academic purposes"""
    import random
    return str(random.randint(100000, 999999))

def hash_otp(otp: str) -> str:
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()

def verify_otp(otp: str, hashed_otp: str) -> bool:
    return bcrypt.checkpw(otp.encode(), hashed_otp.encode())

def create_user(db: Session, username: str, email: str, mobile: str, password: str) -> User:
    """Create a new user account"""
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)

    user = User(
        id=user_id,
        username=username,
        email=email,
        mobile=mobile,
        password_hash=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # TODO: Add audit logging back when database sessions are properly configured
    # Log user creation to audit database
    # audit_db = AuditSessionLocal()
    # try:
    #     log_entry = AuditLog(
    #         actor_type="system",
    #         actor_id="auth_service",
    #         action="user_created",
    #         resource=f"user:{user_id}",
    #         outcome="success"
    #     )
    #     audit_db.add(log_entry)
    #     audit_db.commit()
    # finally:
    #     audit_db.close()

    return user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user credentials"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # TODO: Add audit logging back when database sessions are properly configured
    # Log login to audit database
    # audit_db = AuditSessionLocal()
    # try:
    #     log_entry = AuditLog(
    #         actor_type="user",
    #         actor_id=str(user.id),
    #         action="login",
    #         resource=f"user:{user.id}",
    #         outcome="success"
    #     )
    #     audit_db.add(log_entry)
    #     audit_db.commit()
    # finally:
    #     audit_db.close()

    return user

def create_otp_request(db: Session, user_id: str, channel: str) -> str:
    """Create OTP request for user verification"""
    otp = generate_otp()
    hashed_otp = hash_otp(otp)
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)

    otp_record = OTPRequest(
        user_id=user_id,
        otp_hash=hashed_otp,
        channel=channel,
        expires_at=expires_at
    )

    db.add(otp_record)
    db.commit()

    return otp  # In production, send via SMS/email instead of returning

def verify_user_otp(db: Session, user_id: str, otp: str, channel: str) -> bool:
    """Verify OTP for user"""
    otp_record = db.query(OTPRequest).filter(
        OTPRequest.user_id == user_id,
        OTPRequest.channel == channel,
        OTPRequest.is_used == False,
        OTPRequest.expires_at > datetime.utcnow()
    ).first()

    if not otp_record or not verify_otp(otp, otp_record.otp_hash):
        return False

    # Mark as verified
    otp_record.is_used = True
    db.commit()

    return True