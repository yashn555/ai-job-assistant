import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.parser_service import parse_job_text
from backend.services.nemotron_service import generate_template_email

def test_haystack_parsing():
    print("==================================================")
    print("      TESTING USER HAYSTACK ANALYTICS INPUT       ")
    print("==================================================")

    messy_input = """🎉 Attention Aspiring Professionals! 🚨 FREE JOB ALERT 🏢 Company: HaystackAnalytics 👤 Role: Data Analyst Intern 📍 Location: Mumbai 🎓 Batch: 2024 / 2025 / 2026 💰 Stipend: ₹25,000 – ₹30,000/month ⚙️ Skills: • MS Excel & Google Sheets • Data Cleaning & Reporting • Statistics / Business Analytics • SQL & Data Analysis 📩 Send your resume to: careers@haystackanalytics.in"""

    jobs = parse_job_text(messy_input, fallback_to_llm=False)

    print(f"\nParsed {len(jobs)} job(s):")
    j = jobs[0]
    print(f"- Company: '{j.company_name}'")
    print(f"- Role: '{j.role}'")
    print(f"- Experience: '{j.experience}'")
    print(f"- Location: '{j.location}'")
    print(f"- Email: '{j.recipient_email}'")

    assert j.company_name == "HaystackAnalytics"
    assert j.role == "Data Analyst Intern"
    assert j.recipient_email == "careers@haystackanalytics.in"
    print("\n[SUCCESS] Deterministic Field Extraction 100% Clean!")

    profile = {
        "name": "Yash Nagapure",
        "email": "yashnagapure25@gmail.com",
        "degree": "B.Tech Computer Science Engineering",
        "college": "AISSMS IOIT, Pune",
        "graduation_year": "2027",
        "linkedin_url": "https://linkedin.com/in/yashnagapure",
        "github_url": "https://github.com/yashnagapure",
        "portfolio_url": "https://yashnagapure.dev",
        "skills": ["SQL", "Python", "Data Analysis", "React.js", "Node.js"],
        "projects": ["DocuForge AI", "Travel-Friend"]
    }

    email_body = generate_template_email(j, profile)
    print("\nGenerated Clean Email Body:")
    print("--------------------------------------------------")
    print(email_body)
    print("--------------------------------------------------")

    assert "HaystackAnalytics" in email_body
    assert "Data Analyst Intern" in email_body
    assert "Unknown Company" not in email_body
    assert "FREE JOB ALERT" not in email_body
    assert "Best regards,\nYash Nagapure" in email_body
    assert "LinkedIn: https://linkedin.com/in/yashnagapure" in email_body
    assert "GitHub: https://github.com/yashnagapure" in email_body
    assert "Portfolio: https://yashnagapure.dev" in email_body
    print("\n[SUCCESS] Generated Email & Signature 100% Verified Clean!")

if __name__ == "__main__":
    test_haystack_parsing()
