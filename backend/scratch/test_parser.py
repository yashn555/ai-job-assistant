import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.parser_service import parse_job_text

def test_single_job():
    print("=== Test 1: Single Job Parsing (Pratham International) ===")
    sample_input = """
Company: Pratham International
Role: AI Automation
Experience: Fresher
work@prathamintinternational.in
"""
    jobs = parse_job_text(sample_input, fallback_to_llm=False)
    print(f"Detected {len(jobs)} job(s):")
    for j in jobs:
        print(f"- Company: {j.company_name}")
        print(f"  Role: {j.role}")
        print(f"  Experience: {j.experience}")
        print(f"  Email: {j.recipient_email}")
    
    assert len(jobs) == 1
    assert jobs[0].company_name == "Pratham International"
    assert jobs[0].role == "AI Automation"
    assert jobs[0].recipient_email == "work@prathamintinternational.in"
    print("Test 1 PASSED!\n")

def test_multi_job():
    print("=== Test 2: Multi-Job Parsing (ABC, XYZ, PQR) ===")
    sample_input = """
Company: ABC Technologies
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
jobs@pqr.com
"""
    jobs = parse_job_text(sample_input, fallback_to_llm=False)
    print(f"Detected {len(jobs)} job(s):")
    for idx, j in enumerate(jobs, 1):
        print(f"Job {idx}:")
        print(f"  Company: {j.company_name}")
        print(f"  Role: {j.role}")
        print(f"  Exp: {j.experience}")
        print(f"  Email: {j.recipient_email}")

    assert len(jobs) == 3
    assert jobs[0].recipient_email == "hr@abc.com"
    assert jobs[1].recipient_email == "careers@xyz.ai"
    assert jobs[2].recipient_email == "jobs@pqr.com"
    print("Test 2 PASSED!\n")

if __name__ == "__main__":
    test_single_job()
    test_multi_job()
