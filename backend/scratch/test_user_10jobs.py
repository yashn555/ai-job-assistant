import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.parser_service import parse_job_text

def test_10_jobs():
    sample_text = """
🎉 Attention Aspiring Professionals!
🚨 FREE JOB ALERT

🏢 Company: HaystackAnalytics
👤 Role: Data Analyst Intern
📍 Location: Mumbai
🎓 Batch: 2024 / 2025 / 2026
💰 Stipend: ₹25,000 – ₹30,000/month

⚙️ Skills:
• MS Excel & Google Sheets
• Data Cleaning & Reporting
• Statistics / Business Analytics
• SQL & Data Analysis

📩 Send your resume to: careers@haystackanalytics.in


🌟 Calling All Future Achievers!
🚨 FREE JOB ALERT – Opportunity Just Dropped!

🏢 Company: Rectitude Consulting Services
👤 Role: Frontend Angular Intern
📍 Location: Pune
🎓 Batch: 2024 / 2025 / 2026
💰 Stipend: ₹12,000 – ₹22,000/month

⚙️ Skills:
• Angular
• HTML, CSS, JavaScript
• Communication Skills
• Frontend Basics

📩 Send your resume: recruitment@rectitudecs.com


🎉 Attention Aspiring Professionals!
🚨 FREE JOB ALERT

🏢 Company: E-Solutions
👤 Role: Research Analyst
📍 Location: Noida
🎓 Batch: 2024 & Earlier
💰 Salary: ₹30,000 – ₹50,000/month

⚙️ Skills:
• Research & Analytical Skills
• Written & Verbal English
• US Federal & State Contracting (Preferred)
• Documentation & Reporting

📩 Send your resume to: vikas.s@e-solutionsinc.com



🚨🔥 FREE REFERRAL ALERT 🔥🚨

🏢 Company: Ctruh
👤 Role: Business Analyst Intern
📍 Location: Bengaluru
🎓 Batch: 2025 / 2026 / 2027
💰 Stipend: ₹30,000/month

🏆 PPO Opportunity

⚙️ Skills:
• SQL, Data Analysis & Visualization
• Stakeholder Management
• Market & Product Research
• Business Analysis

📩 Send your resume to: sushmita@ctruh.com


🚨🔥 FREE REFERRAL ALERT 🔥🚨

🏢 Company: Mpiric Software
👤 Role: Junior HR Executive
📍 Location: Ahmedabad
🎓 Batch: 2025 / 2026 / 2027
💰 Salary: ₹3 – ₹5 LPA

⚙️ Skills:
• Recruitment
• HR Operations
• Communication
• Coordination

📩 Send your resume to: hr@mpiricsoftware.com


🚨🔥 FREE HIRING ALERT 🔥🚨

🏢 Company: Dhan
👤 Role: Event Operations Intern
📍 Location: Pan-India
⏳ Duration: 6 Months
🏆 Possible PPO

⭐ Benefits:
• Pan-India Travel Opportunities
• On-Ground Ownership
• Brand / Community / Content Exposure
• Partnerships & Growth Exposure

🎓 Preference:
• Event Management Background
• Interest in Finance / Markets / FinTech

📩 Send your profile to: rahul.deshpande@dhan.co



🚨🔥 FREE REFERRAL ALERT 🔥🚨

🏢 Company: Unyfy
👤 Role: Software Engineer Intern
📍 Location: Bengaluru / Remote
🎓 Batch: 2026 / 2027
💰 Stipend: ₹35,000 – ₹55,000/month

⚙️ Skills:
• React
• Node.js
• Python
• Problem Solving

📩 Send your resume to: ajay.kumar@unyfy.ai



🚨🔥 FREE REFERRAL ALERT 🔥🚨

🏢 Company: Transket
👤 Role: Full Stack Developer Intern
📍 Location: Remote
🎓 Batch: 2025 / 2026 / 2027
💰 Stipend: ₹20,000 – ₹25,000/month

⚙️ Skills:
• Python & Django
• React & TypeScript
• Redux & Tailwind CSS
• REST APIs & PostgreSQL
• Docker & Linux
• Git

📩 Send your resume to: sharmila.balaji@transket.ai


🚨🔥 FREE REFERRAL ALERT 🔥🚨

🏢 Company: House of Hiranandani
👤 Role: AI Intern
📍 Location: Mumbai
🎓 Batch: 2025 / 2026 / 2027
💰 Stipend: ₹20,000/month

🎓 Eligibility: Final-Year BE/B.Tech in AI / CS (AI/ML) / Data Science

⚙️ Skills:
• Python / TypeScript
• SQL / MongoDB
• AI Agents & Prompt Engineering
• Zapier / Make
• REST APIs
• AWS / Azure / GCP

📩 Send your resume to: jalasthi.chawan@houseofhiranandani.com



🚨🔥 FREE REFERRAL ALERT 🔥🚨

🏢 Company: SecureRoot Risk Advisory LLP
👤 Role: Full Stack Development Intern
📍 Location: Kanpur Nagar / Greater Noida West (On-Site)
🎓 Eligibility: Freshers / Recent Graduates

⚙️ Skills:
• HTML / CSS / JavaScript
• React / Next.js / Angular
• Backend Development & APIs
• MongoDB / Supabase
• WordPress
• Git & Hosting / Deployment

📩 Send your resume + portfolio to: info@secureroot.co
"""

    jobs = parse_job_text(sample_text, fallback_to_llm=False)
    print(f"Detected {len(jobs)} jobs:")
    for idx, j in enumerate(jobs, 1):
        print(f"{idx}. Company: '{j.company_name}' | Role: '{j.role}' | Email: '{j.recipient_email}'")

    assert len(jobs) == 10
    assert jobs[0].company_name == "HaystackAnalytics"
    assert jobs[0].recipient_email == "careers@haystackanalytics.in"
    assert jobs[1].company_name == "Rectitude Consulting Services"
    assert jobs[1].recipient_email == "recruitment@rectitudecs.com"
    assert jobs[9].company_name == "SecureRoot Risk Advisory LLP"
    assert jobs[9].recipient_email == "info@secureroot.co"
    print("\n[SUCCESS] 10/10 Multi-Job Batch Parsing PASSED Perfectly!")

if __name__ == "__main__":
    test_10_jobs()
