import requests

API_BASE = "http://localhost:8000"

def login(email, password):
   # Strictly sending 'email' and 'password' as Form Data
    r = requests.post(
        f"{API_BASE}/auth/login",
        data={"email": email, "password": password}
    )
    
    if r.status_code != 200:
        # I added this print so you can see WHY it fails in your terminal
        print(f"❌ Login Failed: {r.status_code} - {r.text}")
        return None
        
    return r.json()["access_token"]

def submit_health_claim(email, token, policy_name, files):
    headers = {"Authorization": f"Bearer {token}"}

    multipart_files = []
    for name, file_path in files.items():
        multipart_files.append(
            (name, (f"{name}.pdf", open(file_path, "rb")))
        )

    r = requests.post(
        f"{API_BASE}/health-claims/submit",
        headers=headers,
        data={"email": email, "policy_name": policy_name},
        files=multipart_files
    )

    # Close file handles
    for _, (_, f) in multipart_files:
        f.close()

    if r.status_code != 200:
        raise Exception(f"API Error {r.status_code}: {r.text}")

    return r.json()

def submit_automobile_claim(email, token, claim_data, files):
    headers = {"Authorization": f"Bearer {token}"}

    multipart_files = []
    for name, file_path in files.items():
        multipart_files.append(
            (name, (f"{name}.jpg", open(file_path, "rb")))  # Use jpg extension for images
        )

    # Prepare form data matching API expectations
    form_data = {
        "email": email,
        "event_date": claim_data["event_date"],
        "event_time": claim_data["event_time"],
        "activity": claim_data["activity"],
        "street": claim_data["street"],
        "city": claim_data["city"],
        "state": claim_data["state"],
        "driver_name": claim_data["driver_name"],
        "driver_age": claim_data["driver_age"],
        "driver_gender": claim_data["driver_gender"],
        "licensed": str(claim_data["licensed"]).lower(),
        "experience_years": claim_data["experience_years"],
        "under_influence": str(claim_data["under_influence"]).lower(),
        "policy_name": claim_data["policy_name"]
    }

    r = requests.post(
        f"{API_BASE}/automobile-claims/submit",
        headers=headers,
        data=form_data,
        files=multipart_files
    )

    # Close file handles
    for _, (_, f) in multipart_files:
        f.close()

    if r.status_code != 200:
        raise Exception(f"API Error {r.status_code}: {r.text}")

    return r.json()

def get_claim_history(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get health claims
    r_health = requests.get(f"{API_BASE}/claims", headers=headers)
    health_claims = r_health.json()["claims"] if r_health.status_code == 200 else []
    
    # Get automobile claims  
    r_auto = requests.get(f"{API_BASE}/automobile-claims", headers=headers)
    auto_claims = r_auto.json()["claims"] if r_auto.status_code == 200 else []
    
    # Combine and mark types
    all_claims = []
    for claim in health_claims:
        claim["claim_type"] = "health"
        all_claims.append(claim)
    for claim in auto_claims:
        claim["claim_type"] = "automobile" 
        all_claims.append(claim)
    
    return {"claims": all_claims}

def get_policies(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{API_BASE}/policies", headers=headers)
    if r.status_code != 200:
        raise Exception(f"API Error {r.status_code}: {r.text}")
    return r.json()

def get_claim_details(token, claim_id, claim_type="health"):
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = "/automobile-claims" if claim_type == "automobile" else "/claims"
    r = requests.get(f"{API_BASE}{endpoint}/{claim_id}", headers=headers)
    if r.status_code != 200:
        raise Exception(f"API Error {r.status_code}: {r.text}")
    return r.json()
