import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.models.schemas import ExtractedJob
from backend.services.nemotron_service import generate_email_content

def test_email_generation():
    print("=== Testing Email Generation Logic ===")
    job = ExtractedJob(
        company_name="Pratham International",
        role="AI Automation",
        experience="Fresher",
        recipient_email="work@prathamintinternational.in",
        job_description="Looking for AI Automation intern with Python and web skills.",
        explicit_subject=None
    )

    profile = {
        "name": "Yash Nagapure",
        "degree": "B.Tech Computer Science Engineering",
        "college": "AISSMS IOIT, Pune",
        "graduation_year": "2027",
        "skills": ["Java", "Python", "React.js", "Node.js", "SQL", "REST APIs"],
        "projects": ["DocuForge AI", "Travel-Friend"]
    }

    res = generate_email_content(job, profile)
    print("Generated Subject:")
    print(res["subject"])
    print("\nGenerated Body:")
    print(res["body"])

    assert "Pratham International" in res["body"]
    assert "Yash Nagapure" in res["body"]
    assert "AI Automation" in res["body"]
    assert res["subject"] == "Application for AI Automation – Fresher | Yash Nagapure"
    print("\nEmail Generation Test PASSED!")

if __name__ == "__main__":
    test_email_generation()
