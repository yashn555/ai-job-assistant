"""
Full pipeline test: Parser + LLM Engine with REAL job postings.
Tests that every job gets a DIFFERENT, unique email — not the same template.
"""
import sys
import os

# Set up paths so backend packages resolve cleanly
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from backend.services.parser_service import parse_job_text
from backend.services.llm_engine import generate_email_content, detect_job_domain

# ──────────────────────────────────────────────────────────
# The REAL job postings from the user's WhatsApp messages
# ──────────────────────────────────────────────────────────
RAW_INPUT = r"""
[19/08, 5:16 pm] +91 92176 36496: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: Alt DRX
👤 Role: Software Intern
🎓 Batch: 2025 / 2026 / 2027
⭐ What You'll Get:
• Real Ownership From Week One
• Hands-On Learning
• Daily Code Review Sessions
• Path to Full-Time Growth Within the Platform Team
📩 Send your resume to: sachin@altdrx.com
[19/08, 6:36 pm] +91 92176 36496: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: Superbank
👤 Role: QA Digital Collection Intern
🎓 Batch: 2025 / 2026 / 2027
🎓 Eligibility:
• Active University Students – 5th Semester or Above
• Final-Year Students
• Fresh Graduates – Maximum 1 Year Since Graduation
• Available for 3–6 Months
⚙️ Requirements:
• Good English Communication
• Strong Writing Skills
• Independent & Team Working Ability
📩 Send your resume to: hiring@superbank.id
📌 Subject: SIP - Position - Name
[20/08, 8:54 am] +91 83687 39751: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: PhonePlus+
👤 Role: Marketing & Growth Intern
📍 Location: Dwarka, New Delhi
🎓 Batch: 2025 / 2026 / 2027
🎓 Who Should Apply:
• Delhi-Based Candidates
• Experience with Instagram & WhatsApp Marketing
• Students from Any Stream
• Energetic & Self-Motivated Candidates
⭐ Benefits:
• Real Startup Experience
• Internship Certificate
• Performance-Based Incentives
• Flexible, Mostly Work From Home Hours
📩 Send your resume to: support@phoneplus.in
[20/08, 8:54 am] +91 83687 39751: 🚨🔥 FREE HIRING ALERT 🔥🚨
🏢 Company: Collegehai
👤 Role: Operations / Data Analyst Intern
📍 Location: Work From Office
🎓 Batch: 2025 / 2026 / 2027
💰 Stipend: ₹10,000/month
⚙️ Requirements:
• MS Excel
• Data Analysis
• Client Communication
• Willingness to Learn
• Ownership Mindset
🔗 Apply: https://docs.google.com/forms/d/e/1FAIpQLScVxEQC-8Jd2SWtIisJG70GjeKwc45SciwpOJxirrhAanVIEA/viewform
[20/08, 10:01 am] +91 83687 39751: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: Zeroharm Sciences
👤 Role: E-commerce Intern
📍 Location: Hitech City, Hyderabad
🎓 Batch: 2025 / 2026 / 2027
💰 Stipend: ₹25,000/month
⏳ Duration: 3–6 Months
📅 Working Days: Monday–Saturday
👥 Positions: 3
⚙️ Responsibilities:
• Product Listings, Images, Descriptions & Pricing
• Orders, Returns & Inventory
• Customer Queries
• E-commerce Performance Monitoring
• Promotional Campaigns
• Digital Marketing
• Competitor & Market Research
• Excel / Google Sheets Reporting
🎓 Eligibility:
• Marketing / Business / E-commerce or Related Degree
• Good Communication & Organizational Skills
• Basic Excel / Google Sheets Knowledge
📩 Send your resume to: Slesha.g@zeroharm.in
[20/08, 12:03 pm] +91 83687 39751: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: MOL IT India Pvt. Ltd.
👤 Role: Application Support Intern
📍 Location: Kolkata (5 Days WFO)
🎓 Batch: 2025 / 2026 / 2027
⏳ Duration: 6 Months
🎓 Eligibility:
• B.Tech / BE / BCA / MCA
• B.Sc / M.Sc in Computer Science
• Local Kolkata Candidates Only
• Face-to-Face Interview
⚙️ Skills:
• SQL
• Python
• Good Communication Skills
📩 Send your resume to: rimli.de@molgroup.com
📌 Subject: CV for Application Support Internship
[20/08, 4:50 pm] +91 92176 36496: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: Preesoft
👤 Role: Business Development Intern
📍 Location: Johar Town, Lahore
🎓 Batch: 2025 / 2026 / 2027
🕐 Working Hours: 5:00 PM – 12:00 AM
⚙️ Skills:
• Business Development
• LinkedIn
• Social Media Platforms
• Job Portals
• Communication
• Client Interaction
🎓 Eligibility: Freshers to 6 Months Relevant Experience
📩 Send your resume to: shoaibhassan@preesoft.com
[20/08, 5:58 pm] +91 92176 36496: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: Krishpar Technologies
👤 Role: Frontend Developer Intern – React.js
🎓 Batch: 2025 / 2026 / 2027
📍 Location: Not Specified
🎓 Eligibility:
• B.E. / B.Tech – CSE / IT
• Final-Year Students
• Freshers
⚙️ Skills:
• React.js
• HTML / CSS / JavaScript
• React Website Development
• AI / ML Tools
• Frontend Development
📩 Send your resume to: udhayasiga@krishpar.com
[21/08, 9:29 am] +91 83687 39751: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: Z-First
👤 Role: HR Intern
📍 Location: Gurgaon
🎓 Batch: 2025 / 2026 / 2027
⏳ Duration: 3 Months
⚡ Immediate Joining
⚙️ Skills:
• Recruitment
• HR Processes
• Communication & Interpersonal Skills
• MS Office
• Google Workspace
🎓 Eligibility: MBA / PGDM / Bachelor's Degree in HR or Related Field
📩 Send your resume to: careers@zielfintech.com
[21/08, 3:26 pm] +91 83687 39751: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: Inventurs Cube LLP
👤 Role: QA Intern
📍 Location: Indore
🎓 Batch: 2026 / 2027
💰 Stipend: ₹15,000 – ₹25,000/month
⚙️ Skills:
• Manual Testing & STLC
• Test Case Writing
• Bug Reporting & Defect Tracking
• Automation Testing
📩 Send your resume to: hr@inventurs.com
[21/08, 5:57 pm] +91 83687 39751: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: Gloify
👤 Role: DevOps Intern
📍 Location: Bengaluru (On-Site)
🎓 Batch: 2025 / 2026 / 2027
💰 Stipend: ₹20,000/month
⚡️ Immediate Joining
⚙️ Skills:
• DevOps Basics
• Linux, Git & Docker
• CI/CD Pipelines
• AWS / Azure / GCP (Preferred)
• Shell / Bash / Python Scripting (Preferred)
🎓 Eligibility: Students or Recent Graduates with Basic DevOps Knowledge, Ready to Join Immediately, and Willing to Work from the Bengaluru Office.
📩 Send your resume to: recruit@gloify.com
[21/08, 9:00 pm] +91 83687 39751: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: ScholarAstra Research Pvt. Ltd.
👤 Role: Business Development Intern
📍 Location: Work From Home
🎓 Batch: 2025 / 2026 / 2027
⚙️ Skills:
• Business Development
• Client Handling
• Follow-Ups
• Communication
• Sales Mindset
🎓 Eligibility: Freshers Welcome
📩 Send your resume to: hr@scholarastra.com
📌 Subject: Application for BDE Intern (Your Name)
[21/08, 9:56 pm] +91 92176 36496: 🚨🔥 FREE REFERRAL ALERT 🔥🚨
🏢 Company: Black Mass Energies
👤 Role: Recruiting Intern
📍 Location: Bengaluru (On-site)
🎓 Batch: 2025 / 2026 / 2027
⏳ Duration: 3 Months
🏢 Work Mode: Work From Office
⚙️ Requirements:
• Fast Learner
• Ownership Mindset
• Startup Environment
• Willingness to Work on Real-World Problems
📩 Send your resume to: shashank@blackmassenergies.in
"""

# Candidate profile for testing
candidate = {
    "name": "Yash Nagar",
    "email": "yash.nagar@gmail.com",
    "phone": "+91-9876543210",
    "degree": "B.Tech in Computer Science",
    "college": "IIT Delhi",
    "graduation_year": "2026",
    "linkedin_url": "https://linkedin.com/in/yashnagar",
    "github_url": "https://github.com/yashn555",
    "portfolio_url": "https://yashnagar.dev",
    "skills": ["React.js", "Python", "Node.js", "Machine Learning", "FastAPI", "TensorFlow", "SQL", "Docker", "TypeScript", "Redux"],
    "projects": ["AI Job Application Assistant", "Smart Campus App"],
}

def main():
    # ──────────────────────────────────────────────────────────
    # STEP 1: Parse all jobs
    # ──────────────────────────────────────────────────────────
    SEP = "=" * 90
    THIN = "-" * 70
    print(SEP)
    print("  STEP 1: PARSING JOB POSTINGS")
    print(SEP)

    parsed_jobs = parse_job_text(RAW_INPUT)
    print(f"\n  Total jobs parsed: {len(parsed_jobs)}\n")

    for i, job in enumerate(parsed_jobs, 1):
        subj_info = f" | Subject: {job.explicit_subject}" if job.explicit_subject else ""
        print(f"  [{i:2d}] {job.company_name:30s} | {job.role:40s} | {job.recipient_email or 'NO EMAIL'}{subj_info}")

    # ──────────────────────────────────────────────────────────
    # STEP 2: Generate emails for each parsed job
    # ──────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 2: GENERATING EMAILS FOR EACH JOB")
    print(SEP)

    results = []
    for i, job in enumerate(parsed_jobs, 1):
        email_result = generate_email_content(job, candidate)
        domain = detect_job_domain(job.role, job.job_description or "", job.skills or "")
        results.append({
            "index": i,
            "company": job.company_name,
            "role": job.role,
            "email_to": job.recipient_email,
            "domain": domain,
            "subject": email_result["subject"],
            "body": email_result["body"],
            "explicit_subject": job.explicit_subject,
        })

    # Print each email
    for r in results:
        print(f"\n{THIN}")
        print(f"  [{r['index']:2d}] {r['company']} -- {r['role']}")
        print(f"      Domain: {r['domain']} | To: {r['email_to']}")
        if r['explicit_subject']:
            print(f"      Explicit Subject: {r['explicit_subject']}")
        print(f"{THIN}")
        print(f"  SUBJECT: {r['subject']}")
        print(f"\n  BODY (first 400 chars):")
        for line in r['body'][:400].split('\n'):
            print(f"    {line}")
        print()

    # ──────────────────────────────────────────────────────────
    # STEP 3: UNIQUENESS ANALYSIS
    # ──────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 3: UNIQUENESS ANALYSIS")
    print(SEP)

    all_bodies = [r['body'] for r in results]
    all_subjects = [r['subject'] for r in results]
    total = len(all_bodies)
    unique_bodies = len(set(all_bodies))
    unique_subjects = len(set(all_subjects))

    print(f"\n  Total emails:          {total}")
    print(f"  Unique bodies:         {unique_bodies}")
    print(f"  Unique subjects:       {unique_subjects}")

    if unique_bodies == total:
        print(f"\n  [PASS] ALL {total} email bodies are UNIQUE!")
    else:
        print(f"\n  [WARN] Only {unique_bodies}/{total} unique bodies. Finding duplicates...")
        from collections import Counter
        body_counts = Counter(all_bodies)
        for body, count in body_counts.items():
            if count > 1:
                dupes = [r for r in results if r['body'] == body]
                print(f"\n  DUPLICATE BODY found {count} times:")
                for d in dupes:
                    print(f"    - [{d['index']}] {d['company']} | {d['role']} | Domain: {d['domain']}")

    if unique_subjects == total:
        print(f"  [PASS] ALL {total} subjects are UNIQUE!")
    else:
        print(f"  [WARN] Only {unique_subjects}/{total} unique subjects. Finding duplicates...")
        from collections import Counter
        subj_counts = Counter(all_subjects)
        for subj, count in subj_counts.items():
            if count > 1:
                dupes = [r for r in results if r['subject'] == subj]
                print(f"\n  DUPLICATE SUBJECT: \"{subj}\" ({count} times):")
                for d in dupes:
                    print(f"    - [{d['index']}] {d['company']} | {d['role']}")

    # ──────────────────────────────────────────────────────────
    # STEP 4: TEMPLATE PATTERN ANALYSIS
    # ──────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  STEP 4: TEMPLATE PATTERN ANALYSIS (Are body_para2 / body_para3 different?)")
    print(SEP)

    print(f"\n  Checking second paragraph variation across all emails:\n")
    for r in results:
        lines = r['body'].split('\n\n')
        para2 = lines[2] if len(lines) > 2 else "(not found)"
        preview = para2[:120].replace('\n', ' ')
        print(f"  [{r['index']:2d}] {r['company']:25s} | {r['domain']:16s} | {preview}...")

    para2_list = []
    for r in results:
        lines = r['body'].split('\n\n')
        para2 = lines[2] if len(lines) > 2 else ""
        para2_list.append(para2)

    unique_para2 = len(set(para2_list))
    print(f"\n  Unique 2nd paragraphs: {unique_para2}/{total}")
    if unique_para2 < total:
        print(f"  NOTE: Some jobs share the same domain so their paragraph templates are similar,")
        print(f"        but the SKILL LIST and COMPANY NAME still differ, making the full body unique.")

    print(f"\n{SEP}")
    print("  TEST COMPLETE")
    print(SEP)

if __name__ == "__main__":
    main()
