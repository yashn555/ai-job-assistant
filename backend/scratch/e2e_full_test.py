import requests
import time

BASE_URL = "http://localhost:8000/api"

def run_full_e2e_test():
    print("==================================================")
    print("    AI JOB APPLICATION ASSISTANT E2E TEST SUITE   ")
    print("==================================================")

    # 1. Healthcheck
    res = requests.get(f"{BASE_URL}/health")
    print(f"\n1. API Healthcheck Status: {res.status_code}")
    assert res.status_code == 200
    print(f"   Response: {res.json()}")

    # 2. Test Single Job Parsing (Acceptance Test 1: Pratham International)
    print("\n2. Testing Single Job Parsing (Pratham International)...")
    single_input = """Company: Pratham International
Role: AI Automation
Experience: Fresher
work@prathamintinternational.in"""

    res = requests.post(f"{BASE_URL}/jobs/parse", json={"text": single_input})
    assert res.status_code == 200
    jobs = res.json()
    print(f"   Parsed {len(jobs)} job(s).")
    pratham_app = jobs[0]
    print(f"   - Company: {pratham_app['company_name']}")
    print(f"   - Role: {pratham_app['role']}")
    print(f"   - Experience: {pratham_app['experience']}")
    print(f"   - Email: {pratham_app['recipient_email']}")
    print(f"   - Status: {pratham_app['status']}")

    assert pratham_app['company_name'] == "Pratham International"
    assert pratham_app['role'] == "AI Automation"
    assert pratham_app['recipient_email'] == "work@prathamintinternational.in"
    print("   [SUCCESS] Single job parsed accurately!")

    # 3. Test Email Generation for Pratham International
    print("\n3. Testing Nemotron Personalized Email Generation...")
    res = requests.post(f"{BASE_URL}/jobs/generate-email", json={"application_id": pratham_app['id']})
    assert res.status_code == 200
    gen_app = res.json()
    print(f"   - Generated Subject: {gen_app['generated_subject']}")
    print(f"   - Status: {gen_app['status']}")
    print(f"   - Body Snippet:\n{gen_app['generated_email'][:250]}...")
    assert "Pratham International" in gen_app['generated_email']
    assert "Yash Nagapure" in gen_app['generated_email']
    print("   [SUCCESS] Nemotron Email generated successfully!")

    # 4. Test Multi-Job Parsing (Acceptance Test 2: ABC, XYZ, PQR)
    print("\n4. Testing Multi-Job Parsing (ABC Technologies, XYZ AI Labs, PQR Systems)...")
    multi_input = """Company: ABC Technologies
Role: Software Developer Intern
Experience: Fresher
hr@abc.com

Company: XYZ AI Labs
Role: AI/ML Intern
Experience: 0-1 Years
careers@xyz.ai

Company: PQR Systems
Role: Backend Developer
Experience: Fresher
jobs@pqr.com"""

    res = requests.post(f"{BASE_URL}/jobs/parse", json={"text": multi_input})
    assert res.status_code == 200
    multi_jobs = res.json()
    print(f"   Parsed {len(multi_jobs)} job(s) independently:")
    for idx, j in enumerate(multi_jobs, 1):
        print(f"   Job {idx}: {j['company_name']} | Role: {j['role']} | Email: {j['recipient_email']}")
    assert len(multi_jobs) >= 3
    print("   [SUCCESS] Multi-job batch parsing passed!")

    # 5. Test Candidate Profile & Settings Retrieval
    print("\n5. Testing Profile & Settings APIs...")
    res = requests.get(f"{BASE_URL}/settings/profile")
    assert res.status_code == 200
    profile = res.json()
    print(f"   Candidate Profile: {profile['name']} ({profile['degree']} - {profile['college']} {profile['graduation_year']})")

    res = requests.get(f"{BASE_URL}/settings/app")
    assert res.status_code == 200
    settings = res.json()
    print(f"   App Settings: Active Resume = '{settings['active_resume']}', Auto-Send = {settings['auto_send']}")

    # 6. Test Email Validation Protection (Missing Recipient)
    print("\n6. Testing Email Validation Safeguards...")
    res = requests.post(f"{BASE_URL}/jobs/parse", json={"text": "Company: Secret Firm\nRole: Dev\nExperience: Fresher"})
    no_email_app = res.json()[0]
    res_send = requests.post(f"{BASE_URL}/applications/{no_email_app['id']}/send")
    print(f"   Send attempt on missing email returned status: {res_send.status_code}")
    assert res_send.status_code == 400
    print(f"   Validation Error: {res_send.json()['detail']}")
    print("   [SUCCESS] Missing email validation safeguard verified!")

    print("\n==================================================")
    print("   ALL E2E INTEGRATION TESTS PASSED SUCCESSFULLY! ")
    print("==================================================")

if __name__ == "__main__":
    run_full_e2e_test()
