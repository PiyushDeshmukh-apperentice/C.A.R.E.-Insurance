import requests
import sys

# CONFIGURATION
BASE_URL = "http://localhost:8000"

# We use a NEW user to avoid conflicts with the broken 'test@example.com'
USERNAME = "bot"
EMAIL = "rahul@gmail.com"  
MOBILE = "1234567890"
PASSWORD = "Rahul123#"

def register_and_verify():
    print(f"🔄 Connecting to {BASE_URL}...")

    # 1. SIGNUP
    print(f"\n1️⃣  Registering {EMAIL}...")
    signup_payload = {
        "username": USERNAME,
        "email": EMAIL,
        "mobile": MOBILE,
        "password": PASSWORD
    }
    
    try:
        r_signup = requests.post(f"{BASE_URL}/auth/signup", data=signup_payload)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Is 'main.py' running?")
        return

    if r_signup.status_code == 400 and "User already exists" in r_signup.text:
        print("⚠️  User already exists. Trying to login directly...")
    elif r_signup.status_code != 200:
        print(f"❌ Signup Failed: {r_signup.text}")
        return
    else:
        # Signup Successful - Capture Data
        data = r_signup.json()
        user_id = data.get("user_id")
        email_otp = data.get("email_otp") # Server returns these for testing!
        sms_otp = data.get("sms_otp")
        
        print(f"✅ Signup successful! (ID: {user_id})")
        print(f"   Received OTPs: Email={email_otp}, SMS={sms_otp}")

        # 2. VERIFY (The API requires this step)
        print(f"\n2️⃣  Verifying Account...")
        verify_payload = {
            "user_id": user_id,
            "email_otp": email_otp,
            "sms_otp": sms_otp
        }
        r_verify = requests.post(f"{BASE_URL}/auth/verify", data=verify_payload)
        
        if r_verify.status_code == 200:
            print("✅ Verification successful!")
        else:
            print(f"❌ Verification Failed: {r_verify.text}")
            return

    # 3. TEST LOGIN
    print(f"\n3️⃣  Testing Login...")
    login_payload = {
        "username": EMAIL, # Sending both to be safe
        "email": EMAIL,
        "password": PASSWORD
    }
    r_login = requests.post(f"{BASE_URL}/auth/login", data=login_payload)
    
    if r_login.status_code == 200:
        token = r_login.json().get("access_token")
        print("✅ LOGIN SUCCESSFUL!")
        print("-" * 40)
        print(f"USER:     {EMAIL}")
        print(f"PASS:     {PASSWORD}")
        print(f"TOKEN:    {token[:15]}...")
        print("-" * 40)
        print("👉 NOW: Update your Telegram Bot to use THESE credentials.")
    else:
        print(f"❌ Login Failed: {r_login.status_code} - {r_login.text}")

if __name__ == "__main__":
    register_and_verify()