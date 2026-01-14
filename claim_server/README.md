# Claim Automation API Server

Simple FastAPI server for claim processing with authentication and audit logging.

## Features

- ✅ User registration with OTP verification
- ✅ JWT-based authentication
- ✅ Claim submission with file upload
- ✅ Explainable AI decisions with clause references
- ✅ HIPAA-aware audit logging
- ✅ SQLite database with proper schema

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Server
```bash
python main.py
```

Server starts at: http://localhost:8000
API docs at: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/verify` - OTP verification
- `POST /auth/login` - User login

### Claims
- `POST /claims/submit` - Submit claim with 7 files
- `GET /claims` - Get user's claims
- `GET /claims/{claim_id}` - Get claim details

### Health
- `GET /health` - Health check

## Usage Examples

### 1. Register User
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -F "username=testuser" \
  -F "email=test@example.com" \
  -F "mobile=1234567890" \
  -F "password=mypassword"
```

### 2. Verify OTP (use OTPs from signup response)
```bash
curl -X POST "http://localhost:8000/auth/verify" \
  -F "user_id=<user_id>" \
  -F "email_otp=<email_otp>" \
  -F "sms_otp=<sms_otp>"
```

### 3. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -F "username=testuser" \
  -F "password=mypassword"
```

### 4. Submit Claim (requires authentication)
```bash
curl -X POST "http://localhost:8000/claims/submit" \
  -H "Authorization: Bearer <token>" \
  -F "username=testuser" \
  -F "policy_name=CIS ASP" \
  -F "files=@discharge.pdf" \
  -F "files=@pathology.pdf" \
  -F "files=@imaging.pdf" \
  -F "files=@bills.pdf" \
  -F "files=@prescription.pdf" \
  -F "files=@lab.pdf" \
  -F "files=@notes.pdf"
```

## Database Schema

- `users` - User accounts
- `user_profiles` - PHI data (separate for HIPAA)
- `user_otps` - OTP verification
- `claims` - Claim records
- `claim_decisions` - AI decisions
- `decision_evidences` - Clause references
- `medical_documents` - File metadata
- `system_logs` - System events
- `audit_logs` - PHI access logs

## Security Features

- Password hashing with bcrypt
- JWT tokens with expiration
- OTP verification for signup
- Audit logging for all PHI access
- File type validation
- User isolation (users only see their claims)

## Integration with Claim Engine

The server integrates with your existing `claim_automation` engine through the `claim_processor.py` module. Currently uses mock responses - update `process_claim_with_engine()` to call your actual engine.

## Configuration

Edit `config.py` for:
- Server host/port
- Database URL
- JWT settings
- File upload limits
- OTP expiry time
