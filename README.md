# C.A.R.E: Claim Automation and Recognition Engine

![Project Status](https://img.shields.io/badge/Status-Active%20Development-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-green)
![React](https://img.shields.io/badge/React-18.2%2B-61dafb)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Project Overview

**C.A.R.E** is an intelligent, end-to-end claim processing automation system designed to revolutionize insurance claim settlement for both **automobile** and **health insurance** sectors. By leveraging deep learning models, optical character recognition (OCR), and large language models, C.A.R.E intelligently extracts, validates, and adjudicates insurance claims while significantly reducing manual intervention.

### ✨ What Makes C.A.R.E Special?

- **Dual Claim Processing**: Handles both vehicle damage and health insurance claims
- **AI-Powered Decision Making**: Uses Groq-powered LLMs for intelligent claim adjudication
- **Computer Vision**: CNN-based severity assessment for vehicle damage
- **Document Intelligence**: Automated extraction of critical information using OCR
- **Multi-Channel Access**: Web interface + Telegram bot for user convenience
- **Enterprise-Ready**: JWT authentication, audit trails, comprehensive logging

---

## 🚀 Quick Start Guide

### Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.9+** (for backend)
- **Node.js 16+** (for frontend)
- **npm 8+** or **yarn**
- **Git** (for version control)
- A valid **Groq API key** (for LLM functionality)
- A valid **Telegram Bot Token** (for bot features)

### Installation Instructions

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd C.A.R.E
```

#### Step 2: Backend Setup

##### Create Python Virtual Environment

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

##### Install Backend Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

**Important Dependencies Explained:**
- `fastapi` (0.104.1): High-performance web framework for building APIs
- `torch` (2.1.2) & `torchvision`: Deep learning libraries for CNN models
- `python-doctr` (0.7.0): OCR engine for document processing
- `groq` (0.4.2): Integration with Groq's LLM API
- `sqlalchemy` (2.0.23): Database ORM for data persistence
- `python-telegram-bot` (20.6): Telegram bot framework

##### Create Environment Configuration

Create a `.env` file in the `server` directory:

```env
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///./insurance_claims.db
# For production, use: DATABASE_URL=postgresql://user:password@localhost/dbname

# Authentication & Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# File Upload Configuration
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=50  # in MB
SUPPORTED_FILE_TYPES=jpg,jpeg,png,pdf,docx,txt
```

##### Start Backend Server

```bash
# Ensure you're in the server directory with venv activated
cd claim_server  # Navigate to API server directory
python main.py

# Or use uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc Documentation**: `http://localhost:8000/redoc`

#### Step 3: Frontend Setup

##### Install Frontend Dependencies

```bash
# Navigate to client directory
cd ../client

# Install all required packages
npm install
# or
yarn install
```

##### Create Frontend Configuration

Create a `.env` file in the `client` directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=InsureGuard Pro
```

##### Start Development Server

```bash
# Start the development server
npm start
# or
yarn start
```

The application will be available at `http://localhost:5173`

#### Step 4: (Optional) Telegram Bot Setup

To enable the Telegram bot functionality:

1. Create a bot on Telegram via **BotFather**
2. Get your bot token and add it to `.env`
3. Run the bot server:

```bash
cd server/bot
python telegram_bot.py
```

---

## 📁 Directory Structure & Explanation

### Project Root Structure

```
C.A.R.E/
├── client/                 # React frontend application
├── server/                 # Python backend and processing engines
├── ABSTRACT.md            # Project abstract and overview
└── README.md              # This file
```

### Backend Directory Structure (`server/`)

```
server/
├── requirements.txt       # Python package dependencies
│
├── claim_server/          # Main FastAPI application
│   ├── main.py           # Entry point; API endpoints definition
│   ├── models.py         # SQLAlchemy database models
│   ├── auth.py           # JWT authentication and authorization
│   ├── claim_processor.py # File validation and claim processing
│   └── dashboard.py      # Dashboard API endpoints
│
├── automobile_claim_engine/  # Vehicle damage claim processing
│   ├── claim_engine.py       # Main processing orchestrator
│   ├── claim_input.py        # Input data structure builder
│   ├── cost_estimator.py     # Parts cost calculation
│   ├── evaluator.py          # Policy compliance checking
│   ├── overlay.py            # Damage visualization overlay
│   ├── predict_cnn_severity.py  # CNN model for damage severity
│   ├── processing/
│   │   └── image_processor.py   # Image preprocessing and analysis
│   └── data/
│       ├── policy.json                    # Automobile policy rules
│       ├── car_parts_cost_master.csv     # Car parts pricing
│       ├── bike_parts_cost_master.csv    # Bike parts pricing
│       └── scooty_parts_cost_master.csv  # Scooty parts pricing
│
├── health_claim_engine/   # Health insurance claim processing
│   ├── main_workflow.py   # Main processing workflow
│   ├── adjudication/
│   │   └── adjudicator.py # AI-driven decision making
│   ├── medical/
│   │   ├── extraction_agent.py    # Extract medical data
│   │   ├── decision_agent.py      # Make adjudication decisions
│   │   ├── processor.py           # Medical data processing
│   │   └── retrieval_engine.py    # Policy retrieval
│   ├── ocr/
│   │   └── extractor.py   # Document OCR extraction
│   └── policy/
│       ├── policy_parser.py       # Parse policy documents
│       ├── processor.py           # Process policy data
│       └── parsed_policies.json   # Parsed policy database
│
└── bot/                   # Telegram bot integration
    ├── telegram_bot.py    # Bot event handlers
    ├── api_client.py      # API communication
    ├── state_manager.py   # User state management
    └── documents.py       # Document handling for bot
```

#### Backend Component Explanations

**`claim_server/main.py`** - The Central Hub
- Defines all REST API endpoints for claim submission, authentication, and tracking
- Handles file uploads and route requests to appropriate engines
- Manages user authentication via JWT tokens

**`automobile_claim_engine/`** - Vehicle Damage Processing
- `claim_engine.py`: Orchestrates the entire claim processing pipeline
- `predict_cnn_severity.py`: Uses CNN model to classify damage severity (Minor, Major, Total Loss)
- `cost_estimator.py`: Queries parts cost databases to estimate repair costs
- `evaluator.py`: Validates claim against policy terms and conditions

**`health_claim_engine/`** - Health Claim Processing
- `extraction_agent.py`: Extracts information from medical documents
- `decision_agent.py`: Uses Groq LLM to make claim adjudication decisions
- `adjudicator.py`: Applies policy rules and creates final decisions

### Frontend Directory Structure (`client/`)

```
client/
├── package.json           # Node.js dependencies and scripts
├── vite.config.js         # Vite build configuration
├── tailwind.config.js     # Tailwind CSS configuration
│
├── public/                # Static public assets
│   └── images/           # Logo and image assets
│
└── src/                   # React source code
    ├── main.jsx           # React DOM entry point
    ├── App.jsx            # Root component
    ├── Routes.jsx         # Route configuration
    │
    ├── pages/             # Page-level components
    │   ├── Homepage/
    │   │   ├── Index.jsx
    │   │   ├── HeroSection.jsx          # Landing hero banner
    │   │   ├── BenefitsSection.jsx      # Product benefits
    │   │   ├── WhyChooseUsSection.jsx   # Why choose C.A.R.E
    │   │   └── ArticlesSection.jsx      # Blog/info articles
    │   └── Profile.jsx    # User profile and claims dashboard
    │
    ├── components/        # Reusable components
    │   ├── LoginModal.jsx          # Authentication modal
    │   ├── Toast.jsx              # Notification component
    │   │
    │   ├── ClaimSubmission/       # Claim form components
    │   │   ├── ClaimTypeSelector.jsx    # Choose health/vehicle
    │   │   ├── HealthClaimForm.jsx      # Health claim form
    │   │   ├── VehicleClaimForm.jsx     # Vehicle claim form
    │   │   └── steps/               # Multi-step form components
    │   │       ├── ClaimTypeStep.jsx
    │   │       ├── ImageUploadStep.jsx
    │   │       ├── DocumentUploadStep.jsx
    │   │       ├── VehicleDetailsStep.jsx
    │   │       ├── DriverDetailsStep.jsx
    │   │       ├── IncidentDetailsStep.jsx
    │   │       ├── ReviewStep.jsx
    │   │       ├── VehicleReviewStep.jsx
    │   │       └── SuccessStep.jsx
    │   │
    │   ├── common/                # Common layout components
    │   │   ├── Header.jsx         # Navigation header
    │   │   └── Footer.jsx         # Footer
    │   │
    │   ├── ProfileScreen/         # Profile page components
    │   │   ├── ProfileHeader.jsx
    │   │   ├── ProfileNavbar.jsx
    │   │   ├── ActivePolicies.jsx
    │   │   ├── PolicyCard.jsx
    │   │   ├── ClaimStatus.jsx
    │   │   └── ActionButtons.jsx
    │   │
    │   └── ui/                    # Basic UI components
    │       ├── Button.jsx
    │       └── EditText.jsx
    │
    ├── services/          # API and data services
    │   ├── apiService.js          # HTTP requests to backend
    │   ├── authService.js         # Authentication logic
    │   └── dataService.js         # Local data management
    │
    ├── hooks/             # Custom React hooks
    │   └── useReveal.js   # Animation/reveal hook
    │
    ├── data/              # Static/mock data
    │   ├── users.json
    │   ├── policies.json
    │   └── otps.json
    │
    └── styles/            # Global styles
        ├── index.css
        └── tailwind.css
```

#### Frontend Component Explanations

**`pages/Homepage/`** - Landing Experience
- Shows product overview, benefits, and call-to-action for claim submission
- Educates users about C.A.R.E capabilities

**`components/ClaimSubmission/`** - Multi-Step Claim Process
- Guides users through structured claim submission workflow
- Handles image uploads, document collection, and form validation
- Separate flows for health vs. vehicle claims

**`components/ProfileScreen/`** - User Dashboard
- Displays active policies and claims status
- Allows users to track claim progress
- Shows policy details and coverage information

**`services/apiService.js`** - API Communication Layer
- Handles all HTTP requests to the backend
- Manages request/response transformation
- Includes error handling and retry logic

---

## 🔄 System Workflow

### Automobile Claim Processing Flow

```
1. USER SUBMISSION
   └─> User uploads vehicle damage images + incident details
   └─> Frontend validates and sends to backend

2. BACKEND VALIDATION
   └─> Verify user authentication (JWT)
   └─> Validate file types and sizes
   └─> Extract metadata from uploads

3. CLAIM ENGINE PROCESSING
   ├─> CNN Model: Analyze damage severity (Minor/Major/Total)
   ├─> Image Overlay: Generate damage visualization
   ├─> Cost Estimation: Calculate repair costs from parts database
   └─> Policy Evaluation: Check policy coverage and limits

4. ADJUDICATION
   └─> Generate decision (APPROVED/PARTIALLY_APPROVED/REJECTED)
   └─> Create audit trail with evidence

5. USER NOTIFICATION
   └─> Store claim record in database
   └─> Return decision to frontend
   └─> User can track claim status in dashboard
```

### Health Claim Processing Flow

```
1. USER SUBMISSION
   └─> User uploads medical documents + claim details
   └─> Frontend validates and sends to backend

2. DOCUMENT PROCESSING
   ├─> OCR Extraction: Extract text from medical documents
   ├─> Medical NLP: Parse medical terminology and procedures
   └─> Information Extraction: Isolate relevant claim data

3. POLICY MATCHING
   └─> Parse policy document
   └─> Match claim details against policy coverage
   └─> Identify applicable deductibles and limits

4. AI ADJUDICATION
   └─> Groq LLM: Analyze claim against policy
   └─> Decision Engine: Generate adjudication decision
   └─> Evidence Collection: Compile decision reasoning

5. DECISION OUTPUT
   └─> Store claim and decision in database
   └─> Return result to frontend
   └─> Send notifications to user
```

### User Journey (Frontend)

```
Landing Page (Homepage)
    ↓
[User clicks "Submit Claim"]
    ↓
Login/OTP Authentication
    ↓
Claim Type Selection (Health vs Vehicle)
    ↓
Multi-Step Form
    ├─> Step 1: Document/Image Upload
    ├─> Step 2: Incident Details
    ├─> Step 3: Policy Selection
    ├─> Step 4: Review Information
    └─> Step 5: Submit
    ↓
Processing (with status updates)
    ↓
Decision Notification
    ↓
Profile Dashboard (View Claim Status)
```

---

## 🔐 Authentication & Security

### How Authentication Works

1. **User Registration/Login**
   - User registers with email/phone
   - OTP sent via SMS or email
   - OTP verified, JWT token issued
   - Token stored in browser local storage

2. **Token Management**
   - Every API request includes `Authorization: Bearer <token>`
   - Backend validates token signature and expiry
   - Token automatically refreshed before expiry (if implemented)

3. **Password Security**
   - Passwords hashed using `bcrypt` (NOT stored in plaintext)
   - Sensitive data encrypted in database
   - API never exposes authentication credentials

### Protected Endpoints

```
Public Endpoints:
  - POST /auth/register        # User registration
  - POST /auth/login           # User login
  - POST /auth/verify-otp      # OTP verification

Protected Endpoints (Require JWT):
  - GET  /users/profile        # Get user profile
  - POST /claims/health         # Submit health claim
  - POST /claims/automobile     # Submit vehicle claim
  - GET  /claims/status/{id}    # Get claim status
  - GET  /dashboard/stats       # Get dashboard statistics
```

---

## 📊 Database Schema

### Key Database Models

```
┌─────────────────────────────────────────────────────┐
│ User (User account information)                     │
├─────────────────────────────────────────────────────┤
│ id (PK)          │ UUID primary key               │
│ email            │ Unique email address           │
│ phone            │ Phone number                   │
│ password_hash    │ Bcrypt hashed password         │
│ full_name        │ User's full name               │
│ is_verified      │ Email/phone verification status│
│ created_at       │ Account creation timestamp     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Claim (Insurance claim records)                     │
├─────────────────────────────────────────────────────┤
│ id (PK)          │ UUID primary key               │
│ user_id (FK)     │ Reference to User              │
│ claim_type       │ 'health' or 'automobile'       │
│ status           │ SUBMITTED/PROCESSING/DECIDED   │
│ amount_claimed   │ Amount claimed by user         │
│ created_at       │ Submission timestamp           │
│ decided_at       │ Decision timestamp             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ClaimDecision (Adjudication outcomes)               │
├─────────────────────────────────────────────────────┤
│ id (PK)          │ UUID primary key               │
│ claim_id (FK)    │ Reference to Claim             │
│ decision         │ APPROVED/REJECTED/PARTIAL      │
│ amount_approved  │ Amount approved for payment    │
│ reasoning        │ LLM reasoning for decision     │
│ created_at       │ Decision timestamp             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ AuditLog (Claim processing audit trail)             │
├─────────────────────────────────────────────────────┤
│ id (PK)          │ UUID primary key               │
│ claim_id (FK)    │ Reference to Claim             │
│ action           │ Processing step performed      │
│ timestamp        │ When action occurred           │
│ metadata         │ Additional action details      │
└─────────────────────────────────────────────────────┘
```

---

## 🛠️ Key Technologies & Why They're Used

### Backend Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| **FastAPI** | 0.104.1 | High-speed async web framework for API endpoints |
| **PyTorch** | 2.1.2 | Deep learning framework for CNN models |
| **python-doctr** | 0.7.0 | OCR engine for extracting text from documents |
| **Groq SDK** | 0.4.2 | Access to high-speed LLM for claim adjudication |
| **SQLAlchemy** | 2.0.23 | Database ORM for type-safe queries |
| **python-telegram-bot** | 20.6 | Telegram bot framework for multi-channel access |
| **bcrypt** | 4.1.2 | Cryptographic hashing for password security |

### Frontend Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| **React** | 18.2.0 | UI library for building interactive interfaces |
| **Vite** | Latest | Fast build tool for development and production |
| **React Router** | Latest | Client-side routing for multi-page experience |
| **Tailwind CSS** | Latest | Utility-first CSS for responsive design |
| **Recharts** | Latest | Charts library for data visualization |

---

## 🚀 Running in Production

### Backend Production Deployment

```bash
# Use production-grade ASGI server
pip install gunicorn

# Start with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker claim_server.main:app --bind 0.0.0.0:8000
```

### Environment Variables for Production

```env
# Security - CHANGE THESE!
SECRET_KEY=generate-a-long-random-string-using-openssl
ENVIRONMENT=production

# Database - Use PostgreSQL, not SQLite
DATABASE_URL=postgresql://username:password@db-host:5432/insurance_db

# CORS - Restrict to your domain only
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Frontend Production Build

```bash
# Create optimized production build
npm run build

# Output will be in the 'dist/' directory
# Deploy to Netlify, Vercel, or your web server
```

---

## 📝 API Documentation

### Authentication Endpoints

```
POST /auth/register
├─ Body: { email, phone, password, full_name }
└─ Returns: { user_id, message }

POST /auth/login
├─ Body: { email, password }
└─ Returns: { access_token, token_type, user }

POST /auth/verify-otp
├─ Body: { email, otp }
└─ Returns: { access_token, token_type }
```

### Claim Submission Endpoints

```
POST /claims/health
├─ Headers: Authorization: Bearer <token>
├─ Body: FormData with documents, health details
└─ Returns: { claim_id, status, decision }

POST /claims/automobile
├─ Headers: Authorization: Bearer <token>
├─ Body: FormData with images, vehicle, incident details
└─ Returns: { claim_id, status, damage_assessment, cost_estimate }

GET /claims/status/{claim_id}
├─ Headers: Authorization: Bearer <token>
└─ Returns: { claim_id, status, decision, decision_date }
```

For full API documentation, start the server and visit: `http://localhost:8000/docs`

---

## 🔧 Configuration Guide

### Backend Configuration

The `config.py` file contains important settings:

```python
# API Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# File Upload Settings
UPLOAD_DIR = Path("./uploads")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
SUPPORTED_FILE_TYPES = ["jpg", "jpeg", "png", "pdf", "docx", "txt"]

# JWT Settings
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### Frontend Configuration

Edit `client/vite.config.js` to customize build:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'  // API proxy
    }
  }
})
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

**Issue: "Module not found" errors in backend**
```bash
# Solution: Ensure virtual environment is activated and requirements installed
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

**Issue: Frontend can't reach backend API**
```
Solution: Verify backend is running on correct port (8000)
Check VITE_API_BASE_URL in client/.env matches backend URL
Check CORS settings in claim_server/main.py
```

**Issue: "GROQ_API_KEY not found" error**
```
Solution: Add GROQ_API_KEY to server/.env file
Get key from https://console.groq.com/
```

**Issue: Database errors on first run**
```bash
Solution: The database will auto-create with SQLAlchemy
If issues persist, delete the .db file and restart
rm insurance_claims.db
```

---

## 📚 Project Structure Summary

```
C.A.R.E/
├── 📄 README.md                      (This file)
├── 📄 ABSTRACT.md                    (Project abstract)
├── 📁 client/                        (React Frontend - Port 5173)
│   └── Handles: UI, user interactions, claim forms, dashboard
├── 📁 server/                        (Python Backend - Port 8000)
│   ├── claim_server/                 (FastAPI application)
│   ├── automobile_claim_engine/      (Vehicle damage processing)
│   ├── health_claim_engine/          (Health claim processing)
│   └── bot/                          (Telegram bot)
```

---

## 🤝 Contributors

To contribute to this project:

- [Prasanna Patwardhan](https://github.com/prasannapp100)
- [Yash Kulkarni](https://github.com/YashKulkarni7996)
- [Piyush Deshmukh](https://github.com/PiyushDeshmukh-apperentice)
- [Rahul Dewani](https://github.com/Rahul-Dewani)
- [Yugandhar Chawale](https://github.com/yugandhar)
- [Sakshi Khutwad](https://github.com/Sakshi-Khutwad)

---

## 📄 License

This project is licensed under the MIT License

---