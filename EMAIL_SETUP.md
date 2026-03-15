# Email OTP Verification Implementation Guide

## Overview
This document covers the complete Email OTP (One-Time Password) verification system for new user registration. Users receive a 6-digit OTP via email after registration and must verify it to activate their account.

> **Current Implementation Status:** ✅ Fully implemented and tested.
> - OTP expiry: **5 minutes** (configurable)
> - Resend limit: **3 per 15 minutes** (rate-limited with 429 response)
> - Primary endpoints: `/verify-otp` and `/resend-otp`
> - Legacy aliases: `/verify-email-otp` and `/resend-verification` (backward compat)

---

## 1. DATABASE SCHEMA CHANGES

### MySQL Table Modifications
The `users` table has the following OTP-related fields (migration already applied via `apply_db_migration_otp.py`):

```sql
-- Legacy fields (backward compat)
email_verified            BOOLEAN  DEFAULT FALSE
verification_token        VARCHAR(255) NULL
verification_token_expiry DATETIME NULL

-- New OTP fields (added by migration)
is_verified               BOOLEAN  DEFAULT FALSE
otp_code                  VARCHAR(10)  NULL
otp_expiry                DATETIME NULL
otp_resend_count          INT      DEFAULT 0
otp_resend_window_start   DATETIME NULL
```

**Both field sets are kept in sync on every write** for backward compatibility.

### Field Descriptions
- **is_verified** / **email_verified**: Both checked; user must verify before login
- **otp_code** / **verification_token**: Stores the active 6-digit OTP
- **otp_expiry** / **verification_token_expiry**: Expiry timestamp (5 minutes from generation)
- **otp_resend_count**: Number of resend requests in current window
- **otp_resend_window_start**: Start of the current 15-minute rate-limit window

---

## 2. FLASK BACKEND IMPLEMENTATION

### Backend Structure
```
backend/
├── email_service.py          # Email sending logic
├── routes/
│   └── auth_routes.py        # Register, verify-otp, resend-otp endpoints
├── config.py                 # Configuration including MAIL_* variables
├── app.py                    # Flask app initialization
└── .env                      # Environment variables (credentials)
```

### A. Email Service (`email_service.py`)

The `EmailService` class handles SMTP email sending:

```python
class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self, smtp_server, smtp_port, smtp_username, 
                 smtp_password, from_email, from_name):
        # Initialize SMTP connection parameters
    
    def send_email(self, to_email, subject, html_content, 
                   text_content=None) -> bool:
        """Send email via SMTP - base method"""
        # - Creates MIME multipart message
        # - Connects to SMTP server with TLS
        # - Sends message
        # - Returns True on success, False on failure
    
    def send_verification_otp_email(self, to_email, user_name, 
                                    otp_code) -> bool:
        """Send OTP verification email"""
        # - Creates HTML email with styled OTP display
        # - Shows 6-digit OTP in large 36px font
        # - Includes 24-hour expiry notice
        # - Plain text fallback for email clients
```

**Key Features:**
- MIME multipart messages (HTML + plain text)
- TLS encryption for SMTP
- HTML formatted OTP display
- Plain text fallback
- Comprehensive error logging

### B. Authentication Routes (`routes/auth_routes.py`)

#### 1. POST `/api/register` - New User Registration

> ⚠️ After registration, login is blocked until OTP is verified (returns HTTP 403).

**Request:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "role": "student"  // Optional: student, teacher, admin
}
```

**Backend Logic:**
```python
@auth_bp.post("/register")
def register():
    # 1. Validate required fields (name, email, password)
    # 2. Normalize and validate input
    # 3. Check if email already exists
    # 4. Generate 6-digit OTP: f"{secrets.randbelow(1000000):06d}"
    # 5. Set token expiry: datetime.utcnow() + timedelta(minutes=5)  # 5 minutes!
    # 6. Create user with email_verified=False, otp_resend_count=0
    # 7. Send OTP email if SMTP configured
    # 8. Return response with verification_otp (in dev/localhost only)
```

**Response (Success - 201):**
```json
{
    "message": "Registration successful. Check your email for OTP.",
    "email_verification_required": true,
    "user": {
        "id": 1,
        "email": "john@example.com",
        "email_verified": false,
        "role": "student"
    },
    "verification_otp": "123456"  // Only in dev/localhost mode
}
```

**Response (Error - 409):**
```json
{
    "error": "Email already registered"
}
```

#### 2. POST `/api/verify-otp` - Verify OTP and Activate Account

> Also accessible via legacy alias: `POST /api/verify-email-otp`

**Request:**
```json
{
    "email": "john@example.com",
    "otp": "123456"
}
```

**Backend Logic:**
```python
@auth_bp.post("/verify-otp")  # also registered as /verify-email-otp
def verify_email_otp():
    # 1. Get email and OTP from request
    # 2. Find user by email
    # 3. Validate OTP is not expired (check otp_expiry — 5 minutes)
    # 4. Compare provided OTP with stored otp_code
    # 5. If match: set is_verified=True + email_verified=True, clear OTP fields
    # 6. If expired: return 400 with error, prompt to resend
    # 7. Return appropriate success/error response
```

**Response (Success - 200):**
```json
{
    "message": "Email verified successfully. You can now login.",
    "email_verified": true
}
```

**Response (Error - 400):**
```json
{
    "error": "OTP is incorrect or expired",
    "message": "Please request a new OTP"
}
```

#### 3. POST `/api/resend-otp` - Request New OTP (Rate Limited)

> Also accessible via legacy alias: `POST /api/resend-verification`
> **Rate limit: 3 resend requests per 15-minute window. Returns HTTP 429 when exceeded.**

**Request:**
```json
{
    "email": "john@example.com"
}
```

**Backend Logic:**
```python
@auth_bp.post("/resend-otp")  # also registered as /resend-verification
def resend_verification():
    # 1. Find user by email
    # 2. Check if user is already verified (skip resend)
    # 3. _enforce_resend_limit(user) — 3 per 15-min window, resets on window expiry
    # 4. Generate new 6-digit OTP
    # 5. Update otp_code, otp_expiry (5 min), verification_token, otp_resend_count
    # 6. Send new OTP email
    # 7. Return response with verification_otp (in dev/localhost only)
```

**Response (Success - 200):**
```json
{
    "message": "New OTP has been sent to your email",
    "verification_otp": "654321"  // Only in dev/localhost mode
}
```

**Response (Rate Limited - 429):**
```json
{
    "error": "Too many resend requests. Try again after HH:MM:SS UTC"
}
```

### C. Configuration (`config.py`)

All config variables loaded from `backend/.env`:

```python
# Email SMTP Configuration
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
MAIL_USERNAME = os.getenv("MAIL_USERNAME")  # Required for real email delivery
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  # Required for real email delivery
MAIL_FROM_EMAIL = os.getenv("MAIL_FROM_EMAIL", "noreply@gamifiedlearning.com")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_FROM_EMAIL)
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Gamified Learning Platform")

# OTP Settings
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))           # Default: 5 min
OTP_RESEND_MAX_ATTEMPTS = int(os.getenv("OTP_RESEND_MAX_ATTEMPTS", "3")) # Default: 3 per window
OTP_RESEND_WINDOW_MINUTES = int(os.getenv("OTP_RESEND_WINDOW_MINUTES", "15"))  # Default: 15 min

# Email Verification Settings
EMAIL_VERIFICATION_REQUIRED = os.getenv("EMAIL_VERIFICATION_REQUIRED", "true").lower() == "true"
VERIFICATION_TOKEN_EXPIRY_HOURS = int(os.getenv("VERIFICATION_TOKEN_EXPIRY_HOURS", "24"))  # legacy

# Application URL
APP_URL = os.getenv("APP_URL", "http://localhost:3000")
```

---

## 3. FRONTEND IMPLEMENTATION (REACT)

### Setup Dependencies

```bash
npm install axios react-router-dom
```

### A. OTP Verification Page (`VerifyEmailOTP.jsx`)

**Location:** `frontend/src/pages/VerifyEmailOTP.jsx`

**Features:**
- Email input field (prefilled from registration)
- 6-digit OTP input (numeric only, max 6 characters)
- Real-time form validation
- Loading/success/error states
- Auto-redirect to login on success
- Resend OTP and back-to-login options

**Component Logic:**
```jsx
// 1. Accept email & otp from location.state (passed from Register page)
// 2. Form submission sends POST /api/verify-email-otp
// 3. On success: Show success message, redirect to login after 1.4s
// 4. On error: Show error message with resend/back options
// 5. Handle loading state with spinner
```

**Styling:** `VerifyEmailOTP.css` includes:
- Centered form container
- Input field styling
- Loading spinner animation
- Success/error message styling
- Responsive mobile layout

### B. Registration Page Modified (`Register.jsx`)

**Changes to support OTP flow:**
```jsx
// After successful registration:
// 1. Show "Check Your Email For OTP!" message
// 2. Display user's email address
// 3. In dev/localhost mode: Show fallback OTP in yellow alert
// 4. Action buttons:
//    - "Enter OTP" → navigates to /verify-otp with email in state
//    - "Resend OTP" → navigates to /resend-otp
//    - "Go to Login" → navigates to /login/student
```

### C. Resend Verification Page (`ResendVerification.jsx`)

**Features:**
- Email input field to request new OTP
- Displays fallback OTP in green box (dev/localhost only)
- Direct link to OTP verification page with email and OTP
- Email remains prefilled after resend

### D. UI Integration

**Router Configuration (`App.js`):**
```jsx
{/* Primary routes */}
<Route path="/verify-otp" element={<VerifyOTP />} />
<Route path="/resend-otp" element={<ResendVerification />} />
{/* Legacy aliases (backward compat) */}
<Route path="/verify-email-otp" element={<VerifyEmailOTP />} />
<Route path="/resend-verification" element={<ResendVerification />} />
```

**Navigation Flow:**
```
Register Page
    ↓ (After successful registration)
/verify-otp  (VerifyOTP page — enter 6-digit OTP)
    ↓ (OTP correct, not expired)
Login Page (on success)
    ↑
/resend-otp  (ResendVerification page — request new OTP, rate limited)
```

---

## 4. ENVIRONMENT CONFIGURATION

### Backend `.env` File

`backend/.env` current template (fill in your Gmail credentials):

```bash
# ===== DATABASE =====
DB_USER=gamified_user
DB_PASSWORD=gamified_pass
DB_HOST=localhost
DB_PORT=3306
DB_NAME=gamified_learning

# ===== EMAIL CONFIGURATION (Gmail SMTP) =====
# ⚠️  Replace these placeholders to enable real email delivery:
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com          # ← your Gmail address
MAIL_PASSWORD=your-16-char-app-password     # ← Gmail App Password (NOT account password)
MAIL_FROM_EMAIL=your-email@gmail.com
MAIL_DEFAULT_SENDER=your-email@gmail.com
MAIL_FROM_NAME=Gamified Learning Platform

# ===== APPLICATION SETTINGS =====
APP_URL=http://localhost:3000
FLASK_ENV=development

# ===== OTP SETTINGS =====
EMAIL_VERIFICATION_REQUIRED=true
OTP_EXPIRY_MINUTES=5
OTP_RESEND_MAX_ATTEMPTS=3
OTP_RESEND_WINDOW_MINUTES=15
VERIFICATION_TOKEN_EXPIRY_HOURS=24

# ===== LEGACY USER AUTO-VERIFICATION =====
AUTO_VERIFY_LEGACY_USERS=true
LEGACY_VERIFICATION_CUTOFF=2026-03-12
```

### Gmail Setup Instructions

**Step 1: Enable 2-Factor Authentication**
- Go to: https://myaccount.google.com/security
- Click "2-Step Verification"
- Follow the setup steps

**Step 2: Create App Password**
- Go to: https://myaccount.google.com/apppasswords
- Select "Mail" and "Windows Computer" (or your OS)
- Google generates a 16-character password
- Copy this password to MAIL_PASSWORD in .env

**Step 3: Configure Backend**
- Add MAIL_USERNAME: your-email@gmail.com
- Add MAIL_PASSWORD: your-16-character-app-password
- Restart Flask backend

### Alternative Email Providers

**Outlook/Office 365:**
```bash
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

**Yahoo Mail:**
```bash
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USERNAME=your-email@yahoo.com
MAIL_PASSWORD=your-app-specific-password
```

**SendGrid:**
```bash
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

**AWS SES:**
```bash
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_USERNAME=your-ses-smtp-username
MAIL_PASSWORD=your-ses-smtp-password
```

---

## 5. API REQUEST EXAMPLES

### Example 1: Register New User with curl

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "SecurePass123!",
    "role": "student"
  }'
```

**Expected Response:**
```json
{
    "message": "Registration successful. Check your email for OTP.",
    "email_verification_required": true,
    "user": {
        "id": 5,
        "email": "jane@example.com",
        "email_verified": false,
        "role": "student"
    },
    "verification_otp": "456789"
}
```

### Example 2: Verify OTP with curl

```bash
# Primary endpoint:
curl -X POST http://localhost:5000/api/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "otp": "456789"
  }'
# (Also works via legacy: /api/verify-email-otp)
```

**Expected Response:**
```json
{
    "message": "Email verified successfully. You can now login.",
    "email_verified": true
}
```

### Example 3: Resend OTP with curl

```bash
# Primary endpoint (rate-limited: 3 per 15 min):
curl -X POST http://localhost:5000/api/resend-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com"
  }'
# (Also works via legacy: /api/resend-verification)
```

**Expected Response (200):**
```json
{
    "message": "New OTP has been sent to your email",
    "verification_otp": "789123"
}
```

**Rate limit exceeded (429):**
```json
{
    "error": "Too many resend requests. Try again after 14:35:22 UTC"
}
```

### Example 4: Python Script (Complete Flow)

```python
import requests
import time

BASE_URL = "http://localhost:5000"

# Step 1: Register new user
print("=== Step 1: Register User ===")
register_data = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123!",
    "role": "student"
}
response = requests.post(f"{BASE_URL}/api/register", json=register_data)
print(f"Status: {response.status_code}")
reg_response = response.json()
print(f"Message: {reg_response.get('message')}")
otp = reg_response.get("verification_otp")
print(f"Fallback OTP (dev mode): {otp}")

# Step 2: Verify OTP
print("\n=== Step 2: Verify OTP ===")
verify_data = {
    "email": "test@example.com",
    "otp": otp
}
response = requests.post(f"{BASE_URL}/api/verify-otp", json=verify_data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Step 3: Login (should succeed now)
print("\n=== Step 3: Login ===")
login_data = {
    "email": "test@example.com",
    "password": "TestPass123!"
}
response = requests.post(f"{BASE_URL}/api/login", json=login_data)
print(f"Status: {response.status_code}")
login_response = response.json()
if response.status_code == 200:
    print(f"✓ Login successful!")
    print(f"Token: {login_response.get('access_token')[:20]}...")
else:
    print(f"✗ Login failed: {login_response.get('error')}")
```

**Run the script:**
```bash
cd backend
python your_script.py
```

### Example 5: JavaScript/React (Frontend Usage)

```javascript
import axios from "axios";

// Step 1: Register
async function registerUser(name, email, password, role = "student") {
    try {
        const response = await axios.post("/api/register", {
            name,
            email,
            password,
            role,
        });
        console.log("Registration successful:", response.data);
        // Redirect to OTP verification page
        // navigate("/verify-email-otp", { 
        //     state: { email, otp: response.data.verification_otp } 
        // });
        return response.data;
    } catch (error) {
        console.error("Registration failed:", error.response?.data);
        throw error;
    }
}

// Step 2: Verify OTP
async function verifyOTP(email, otp) {
    try {
        const response = await axios.post("/api/verify-email-otp", {
            email,
            otp,
        });
        console.log("OTP verified:", response.data);
        // Redirect to login
        // navigate("/login/student");
        return response.data;
    } catch (error) {
        console.error("OTP verification failed:", error.response?.data);
        throw error;
    }
}

// Step 2: Verify OTP
async function verifyOTP(email, otp) {
    try {
        const response = await axios.post("/api/verify-otp", { email, otp });
        console.log("OTP verified:", response.data);
        return response.data;
    } catch (error) {
        console.error("OTP verification failed:", error.response?.data);
        throw error;
    }
}

// Step 3: Resend OTP (rate-limited)
async function resendOTP(email) {
    try {
        const response = await axios.post("/api/resend-otp", { email });
        console.log("OTP resent:", response.data);
        return response.data;
    } catch (error) {
        if (error.response?.status === 429) {
            console.error("Rate limited:", error.response.data.error);
        } else {
            console.error("Resend failed:", error.response?.data);
        }
        throw error;
    }
}
```

---

## 6. SECURITY FEATURES

### OTP Security
1. **Random Generation**: Uses `secrets.randbelow(1000000)` for cryptographically secure randomness
2. **Format**: 6-digit numeric OTP (000000 - 999999), zero-padded (`f"{n:06d}"`)
3. **Expiry**: **5 minutes** (configurable via `OTP_EXPIRY_MINUTES`)
4. **One-time Use**: OTP cleared from DB after successful verification
5. **Login Blocking**: Unverified users receive HTTP 403 on login attempt
6. **Resend Rate Limiting**: Max 3 resend attempts per 15-minute window; HTTP 429 on excess
7. **Dual-Field Sync**: New fields (`is_verified`, `otp_code`) and legacy fields kept in sync

### Password Security
- Passwords hashed using `werkzeug.security.generate_password_hash()`
- Salted hashes prevent rainbow table attacks
- Never store plain-text passwords

### Email Security
- SMTP uses TLS encryption (port 587)
- Credentials stored in environment variables (.env), never in code
- App Passwords used for Gmail (not account password)
- Email addresses normalized (lowercase) to prevent duplication

### Production Recommendations
1. Use professional email service (SendGrid, Mailgun, AWS SES)
2. Configure SPF, DKIM, DMARC records
3. Monitor email delivery and bounce rates
4. Implement rate limiting on resend-otp endpoint
5. Use longer OTP expiry in production (adjustable via config)
6. Monitor failed verification attempts
7. Consider implementing progressive delays for failed OTP attempts

---

## 7. TESTING CHECKLIST

### Automated Tests (all passed ✅)
- [x] **Register New User**: User created with `email_verified=false`, `is_verified=false`
- [x] **OTP Sent**: Email sent via SMTP if configured; fallback OTP in dev mode response
- [x] **Login Before Verification**: Unverified user gets HTTP 403 ✅
- [x] **Verify OTP**: `POST /api/verify-otp` → 200, sets `is_verified=true` ✅
- [x] **Login After Verification**: Verified user gets JWT token ✅
- [x] **Resend Rate Limit**: 4th resend in window gets HTTP 429 ✅

### Manual Tests (to run)
- [ ] **Email Delivery**: Set real Gmail credentials, register, check inbox for OTP
- [ ] **Expired OTP**: Wait 5+ minutes, try old OTP, should get expiry error
- [ ] **Wrong OTP**: Enter incorrect code, should return error  
- [ ] **Resend OTP**: Request new OTP, verify new one works (old invalidated)
- [ ] **Duplicate Registration**: Same email twice → 409 error
- [ ] **Case Insensitivity**: Register with `User@EXAMPLE.COM`, verify works

---

## 8. TROUBLESHOOTING

### OTP not being sent
**Issue**: Email verification enabled but no emails received
**Solutions**:
```bash
# 1. Check MAIL_* variables in .env
# 2. Verify Gmail App Password (not regular password)
# 3. Check backend logs for "MAIL_USERNAME/MAIL_PASSWORD not configured"
# 4. Restart Flask backend after .env changes
# 5. Test with: python -c "import os; from config import Config; ..."
```

### "Email already registered" error
**Issue**: Cannot register with email that appears new
**Solution**: 
```sql
-- Check if email exists in database
SELECT id, email, email_verified FROM users WHERE email = 'test@example.com';
-- Delete old user if needed: DELETE FROM users WHERE id = X;
```

### OTP expired immediately
**Issue**: OTP says expired when just generated
**Solution**: Check server time synchronization with database server

### SMTP Connection Refused
**Issue**: "Connection refused" when sending email
**Solutions**:
1. Verify MAIL_SERVER and MAIL_PORT correct
2. Check firewall allows outbound port 587
3. Test with: `telnet smtp.gmail.com 587`
4. Ensure 2FA enabled for Gmail account

### Development Mode Fallback OTP
To see OTP in response (dev testing):
```bash
# In .env:
FLASK_ENV=development  # or set ENV=development
APP_URL=http://localhost:3000  # must include "localhost"

# Then response will include:
# "verification_otp": "123456"
```

---

## 9. CONFIGURATION REFERENCE

| Variable | Default | Description |
|----------|---------|-------------|
| MAIL_SERVER | smtp.gmail.com | SMTP server address |
| MAIL_PORT | 587 | SMTP port (usually 587 for TLS) |
| MAIL_USERNAME | - | Email account for sending (required) |
| MAIL_PASSWORD | - | SMTP password/app-password (required) |
| MAIL_FROM_EMAIL | noreply@gamifiedlearning.com | Sender email address |
| MAIL_FROM_NAME | Gamified Learning Platform | Sender display name |
| APP_URL | http://localhost:3000 | Frontend application URL |
| EMAIL_VERIFICATION_REQUIRED | true | Enforce email verification |
| OTP_EXPIRY_MINUTES | 5 | OTP expiry time in minutes |
| OTP_RESEND_MAX_ATTEMPTS | 3 | Max resend requests per window |
| OTP_RESEND_WINDOW_MINUTES | 15 | Rate-limit window in minutes |
| VERIFICATION_TOKEN_EXPIRY_HOURS | 24 | Legacy field sync (hours) |

---

## 10. FILE STRUCTURE SUMMARY

```
GAMIFIED_LEARNING/
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Register.jsx                 # Registration form (→ /verify-otp after register)
│       │   ├── VerifyEmailOTP.jsx           # OTP entry page (calls /api/verify-otp)
│       │   ├── VerifyOTP.jsx               # Re-export of VerifyEmailOTP for /verify-otp route
│       │   ├── ResendVerification.jsx       # Resend OTP page (calls /api/resend-otp)
│       │   └── VerifyEmailOTP.css           # OTP page styling
│       └── App.js                          # Router: /verify-otp, /resend-otp + legacy aliases
│
├── backend/
│   ├── email_service.py                    # EmailService class (5-min expiry, TLS toggle)
│   ├── routes/
│   │   └── auth_routes.py                  # register, /verify-otp, /resend-otp + helpers
│   ├── models.py                           # User model with 5 new OTP columns
│   ├── config.py                           # OTP_EXPIRY_MINUTES, resend limits, MAIL_* keys
│   ├── app.py                              # Flask init; auto-verifies legacy users
│   ├── .env                                # Credentials (⚠️ fill in MAIL_USERNAME/PASSWORD)
│   ├── apply_db_migration_otp.py           # One-time DB migration (already run ✅)
│   ├── sql/otp_schema_update.sql           # SQL reference for migration
│   └── requirements.txt                    # Flask-Mail==0.10.0 included
│
└── EMAIL_SETUP.md                          # This file
```

---

## Quick Start Checklist

1. **Backend Setup** ✅ Done
   - [x] DB migration applied (`apply_db_migration_otp.py` ran successfully)
   - [x] `pip install -r requirements.txt` (Flask-Mail included)
   - [x] Backend running on port 5000
   - [ ] ⚠️ **Set real Gmail credentials in `backend/.env`** (only remaining step for email delivery)

2. **Frontend Setup** ✅ Done
   - [x] `VerifyEmailOTP.jsx` and `VerifyOTP.jsx` exist in `frontend/src/pages/`
   - [x] Routes `/verify-otp` and `/resend-otp` added to `App.js`
   - [x] Frontend running on port 3000

3. **Testing** ✅ Automated tests passed
   - [x] register → 201, `is_verified=false`
   - [x] login before verify → 403
   - [x] verify OTP → 200
   - [x] login after verify → 200 with JWT
   - [x] resend ×3 → 200; resend ×4 → 429
   - [ ] Manual: register with real email, check inbox for OTP

4. **Enable Real Email Delivery** (1 step remaining)
   ```bash
   # Edit backend/.env:
   MAIL_USERNAME=your-actual@gmail.com
   MAIL_PASSWORD=your-16-char-app-password
   MAIL_FROM_EMAIL=your-actual@gmail.com
   MAIL_DEFAULT_SENDER=your-actual@gmail.com
   # Then restart: python app.py
   ```

5. **Production Deployment**
   - [ ] Configure professional email service (SendGrid, AWS SES)
   - [ ] Set `FLASK_ENV=production`
   - [ ] Update `APP_URL` to production domain
   - [ ] Enable monitoring for email delivery
