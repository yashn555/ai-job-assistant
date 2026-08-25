import os
import sys
import json
import unittest

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.models.schemas import ExtractedJob
from backend.services.llm_engine import (
    generate_email_content,
    detect_job_domain,
    personalize_explicit_subject,
    sanitize_text
)
from backend.services.parser_service import parse_job_text
from backend.services.resume_extractor_service import parse_resume_details
from backend.services.email_service import validate_email_send_request
from backend.routes.auth import hash_password, create_token, decode_token
from backend.models.models import User

class ComprehensiveModuleAndSecurityTestSuite(unittest.TestCase):

    def setUp(self):
        self.standard_profile = {
            "name": "Yash Nagar",
            "email": "yash.nagar@gmail.com",
            "phone": "+91-9876543210",
            "degree": "B.Tech in Computer Science",
            "college": "IIT Delhi",
            "graduation_year": "2026",
            "linkedin_url": "https://linkedin.com/in/yashnagar",
            "github_url": "https://github.com/yashn555",
            "portfolio_url": "https://yashnagar.dev",
            "skills": ["React.js", "Python", "FastAPI", "Docker", "Machine Learning", "SQL"],
            "projects": ["AI Job Assistant", "Smart Campus App"]
        }

    # ──────────────────────────────────────────────────────────
    # TEST SUITE 1: LLM Engine Domains & Customization
    # ──────────────────────────────────────────────────────────
    def test_all_10_llm_domains(self):
        test_cases = [
            ("DevOps Engineer", "Docker, Kubernetes, AWS, CI/CD", "DEVOPS_CLOUD"),
            ("QA Automation Tester", "Selenium, TestNG, STLC, Bug Reporting", "QA_TESTING"),
            ("HR Recruiter Intern", "Talent Acquisition, Screening, HR Operations", "HR_RECRUITMENT"),
            ("Business Development Executive", "Lead generation, Sales, Client interaction", "BUSINESS_MARKETING"),
            ("Data Analyst Intern", "SQL, Excel, PowerBI, Tableau, Data Cleaning", "DATA_ANALYTICS"),
            ("AI Engineer", "PyTorch, Transformers, LLMs, Computer Vision", "AI_ML"),
            ("React Frontend Developer", "React.js, TailwindCSS, State Management", "FRONTEND_MOBILE"),
            ("Backend API Developer", "FastAPI, PostgreSQL, Microservices, REST", "BACKEND_API"),
            ("AI Fullstack Developer", "React, Node, LangChain, OpenAI APIs", "AI_FRONTEND"),
            ("General Software Intern", "Problem Solving, C++, General coding", "GENERAL"),
        ]

        for role, skills_desc, expected_domain in test_cases:
            detected = detect_job_domain(role, skills_desc, skills_desc)
            self.assertEqual(detected, expected_domain, f"Failed domain classification for {role}")
            
            # Verify generated email contains company, role, and appropriate domain structure
            job = ExtractedJob(
                company_name="Apex Corp",
                role=role,
                skills=skills_desc,
                recipient_email="jobs@apexcorp.com"
            )
            email_out = generate_email_content(job, self.standard_profile)
            self.assertIn("Apex Corp", email_out["body"])
            self.assertIn(role, email_out["subject"])
            self.assertTrue(len(email_out["body"]) > 200)

    # ──────────────────────────────────────────────────────────
    # TEST SUITE 2: Explicit Subject Personalizer Variations
    # ──────────────────────────────────────────────────────────
    def test_explicit_subject_placeholders(self):
        cand_name = "Yash Nagar"
        role = "Frontend Developer Intern"

        templates_and_expectations = [
            ("SIP - Position - Name", f"SIP - {role} - {cand_name}"),
            ("Application for BDE Intern (Your Name)", f"Application for BDE Intern {cand_name}"),
            ("Resume: {Role} - {Name}", f"Resume: {role} - {cand_name}"),
            ("[Position] Application - [Candidate Name]", f"{role} Application - {cand_name}"),
            ("<Role> - <Your Name>", f"{role} - {cand_name}"),
            ("CV for Application Support Internship - Name", f"CV for Application Support Internship - {cand_name}"),
            ("Direct Job Application", "Direct Job Application"),
        ]

        for template, expected in templates_and_expectations:
            res = personalize_explicit_subject(template, cand_name, role)
            self.assertEqual(res, expected, f"Subject template failed for '{template}' -> Got '{res}', Expected '{expected}'")

    # ──────────────────────────────────────────────────────────
    # TEST SUITE 3: Edge Case Candidate Profiles
    # ──────────────────────────────────────────────────────────
    def test_profile_edge_cases(self):
        job = ExtractedJob(company_name="Global Inc", role="HR Intern", recipient_email="hr@global.com")

        # 1. Blank Profile (No degree, no college, no skills)
        blank_profile = {"name": "Jane Doe"}
        out = generate_email_content(job, blank_profile)
        self.assertIn("Jane Doe", out["body"])
        self.assertIn("proactive human resources candidate", out["body"])

        # 2. Non-CS MBA Profile
        mba_profile = {
            "name": "Alex Smith",
            "degree": "MBA in Human Resources",
            "college": "IIM Ahmedabad",
            "graduation_year": "2025"
        }
        out_mba = generate_email_content(job, mba_profile)
        self.assertIn("final-year MBA in Human Resources student at IIM Ahmedabad", out_mba["body"])

        # 3. Only College specified
        college_only_profile = {"name": "Bob", "college": "BITS Pilani"}
        out_col = generate_email_content(job, college_only_profile)
        self.assertIn("student at BITS Pilani", out_col["body"])

    # ──────────────────────────────────────────────────────────
    # TEST SUITE 4: Parser Robustness & Trailing Punctuation
    # ──────────────────────────────────────────────────────────
    def test_parser_with_noise_and_punctuation(self):
        messy_input = """
        🏢 Company: Technex Solutions.
        👤 Role: Backend Engineer!
        📍 Location: Remote
        📩 Send Resume to: careers@technex.io.
        📌 Subject: Application for [Position] - [Your Name]
        
        🚨 FREE REFERRAL ALERT 🚨
        Company: Nexa Corp
        Role: QA Analyst
        Email: hr@nexacorp.com,
        """

        jobs = parse_job_text(messy_input)
        self.assertEqual(len(jobs), 2)
        
        # Verify emails do NOT have trailing period or comma
        self.assertEqual(jobs[0].recipient_email, "careers@technex.io")
        self.assertEqual(jobs[1].recipient_email, "hr@nexacorp.com")
        
        # Verify explicit subject handled
        self.assertEqual(jobs[0].explicit_subject, "Application for [Position] - [Your Name]")

    # ──────────────────────────────────────────────────────────
    # TEST SUITE 5: Authentication & Security Tokens
    # ──────────────────────────────────────────────────────────
    def test_auth_and_token_tampering(self):
        fake_user = User(
            id=42,
            name="Secure User",
            email="secure@example.com",
            password_hash=hash_password("MyStrongPass123!"),
            app_password="abcd efgh ijkl mnop"
        )

        token = create_token(fake_user)
        self.assertTrue(token.startswith("token_"))

        # Decode valid token
        payload = decode_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["id"], 42)
        self.assertEqual(payload["email"], "secure@example.com")
        
        # Verify app password is NOT plaintext in token payload
        self.assertNotEqual(payload.get("app_pass"), "abcd efgh ijkl mnop")
        self.assertTrue(payload.get("app_pass").startswith("gAAAAA"))

        # Test tampered signature
        tampered_token = token[:-4] + "ffff"
        self.assertIsNone(decode_token(tampered_token))

        # Test corrupt token
        self.assertIsNone(decode_token("not_a_valid_token_structure"))

    def test_app_password_encryption_and_masking(self):
        from backend.services.crypto_service import encrypt_secret, decrypt_secret, mask_secret, is_masked
        
        raw_password = "abcd efgh ijkl mnop"
        
        # 1. Encryption test
        encrypted = encrypt_secret(raw_password)
        self.assertNotEqual(encrypted, raw_password)
        self.assertTrue(encrypted.startswith("gAAAAA"))
        
        # 2. Decryption test
        decrypted = decrypt_secret(encrypted)
        self.assertEqual(decrypted, raw_password)
        
        # 3. Masking test
        masked = mask_secret(encrypted)
        self.assertEqual(masked, "••••••••••••••••")
        self.assertTrue(is_masked(masked))
        self.assertTrue(is_masked("••••••••••••••••"))
        self.assertFalse(is_masked("new_real_password"))
        
        # 4. Decrypt on masked input returns empty string safely
        self.assertEqual(decrypt_secret(masked), "")
        
        # 5. Legacy plaintext unencrypted fallback test
        legacy_plain = "legacy_unencrypted_secret"
        self.assertEqual(decrypt_secret(legacy_plain), legacy_plain)

    # ──────────────────────────────────────────────────────────
    # TEST SUITE 6: Resume Extractor Service
    # ──────────────────────────────────────────────────────────
    def test_resume_details_extractor(self):
        resume_text = """
        Yash Nagapure
        Email: yash@example.com | Phone: +91 9876543210
        LinkedIn: linkedin.com/in/yashnagapure | GitHub: github.com/yashn555

        Education:
        B.Tech in Computer Science and Engineering
        IIT Delhi (2022 - 2026)

        Technical Skills:
        Python, React.js, FastAPI, Docker, SQL, Machine Learning

        Projects:
        • AI Job Application Assistant - Automated email delivery platform
        • Smart Campus Portal - IoT and Web dashboard
        """

        extracted = parse_resume_details(resume_text)
        self.assertEqual(extracted["name"], "Yash Nagapure")
        self.assertEqual(extracted["email"], "yash@example.com")
        self.assertIn("Python", extracted["skills"])
        self.assertIn("React.js", extracted["skills"])
        self.assertIn("2026", extracted["graduation_year"])
        self.assertTrue(len(extracted["projects"]) >= 1)

    # ──────────────────────────────────────────────────────────
    # TEST SUITE 7: Email Validation Safeguards
    # ──────────────────────────────────────────────────────────
    def test_email_validation_safeguards(self):
        # 1. Valid Request
        valid, msg = validate_email_send_request(
            recipient_email="recruiter@company.com",
            company_name="Company",
            role="Dev",
            subject="Application",
            body="Hello, I am applying..."
        )
        self.assertTrue(valid)

        # 2. Missing Email
        valid_no_email, _ = validate_email_send_request(
            recipient_email="",
            company_name="Company",
            role="Dev",
            subject="Application",
            body="Hello"
        )
        self.assertFalse(valid_no_email)

        # 3. Invalid Email Format
        valid_bad_email, _ = validate_email_send_request(
            recipient_email="invalid-email-string",
            company_name="Company",
            role="Dev",
            subject="Application",
            body="Hello"
        )
        self.assertFalse(valid_bad_email)


if __name__ == "__main__":
    print("==================================================================")
    print("   RUNNING COMPREHENSIVE ALL-MODULE & VULNERABILITY TEST SUITE    ")
    print("==================================================================")
    unittest.main(verbosity=2)
