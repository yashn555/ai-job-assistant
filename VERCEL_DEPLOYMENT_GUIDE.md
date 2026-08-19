# 🚀 Vercel Deployment Guide - AI Job Application Assistant

This guide provides clear, step-by-step instructions to deploy your personal **AI Job Application Assistant** to **Vercel** so you can easily access and send job applications directly from your **mobile phone** or any web browser!

---

## 🔒 Safety & Local Integrity Guarantee
> All deployment files (`vercel.json`, `api/index.py`, `requirements.txt`) have been added independently.
> Your existing local working system (`http://localhost:5173` and `http://localhost:8000`) is **100% untouched and active**.

---

## 📋 Prerequisites
1. A free **GitHub** account ([github.com](https://github.com)).
2. A free **Vercel** account ([vercel.com](https://vercel.com)) connected to your GitHub account.
3. Git installed on your computer.

---

## 🎯 Step-by-Step Deployment Instructions

### Method A: Deploying via GitHub & Vercel Dashboard (Recommended & Easiest)

#### Step 1: Push Project to GitHub
Open PowerShell or Terminal in your project folder (`d:\JOB SEND`) and run:

```bash
# 1. Initialize Git repository (if not already done)
git init

# 2. Add files
git add .

# 3. Create initial commit
git commit -m "Deploy AI Job Application Assistant to Vercel"

# 4. Link your remote GitHub repository
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ai-job-assistant.git

# 5. Push code
git branch -M main
git push -u origin main
```

---

#### Step 2: Import Project into Vercel
1. Go to [vercel.com/new](https://vercel.com/new).
2. Click **Import Repository** and select your `ai-job-assistant` GitHub repository.
3. Under **Framework Preset**, Vercel will automatically detect `Other` or `Vite`. Set Root Directory as `./` (leave default).

---

#### Step 3: Configure Environment Variables on Vercel
Before clicking **Deploy**, expand the **Environment Variables** section on Vercel and add the following keys:

| Key | Value |
|---|---|
| `NVIDIA_API_KEY` | `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` |
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `yashnagapure25@gmail.com` |
| `SMTP_PASSWORD` | `awmtyyfozljwmbvu` |
| `SENDER_EMAIL` | `yashnagapure25@gmail.com` |

---

#### Step 4: Click Deploy!
1. Click **Deploy**.
2. Vercel will build your React frontend and deploy FastAPI Python serverless functions in ~1 minute.
3. You will receive your live domain URL (e.g. `https://ai-job-assistant-yash.vercel.app`).

---

### Method B: Deploying via Vercel CLI (Alternative)

If you prefer deploying directly from PowerShell without GitHub:

```bash
# 1. Install Vercel CLI globally
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy project
vercel --prod
```

During CLI prompt:
- Set Environment Variables when prompted or add them via Vercel Dashboard Settings -> Environment Variables.

---

## 📱 Mobile Usage
Once deployed, open your live Vercel URL on your mobile browser (Safari, Chrome, etc.):
1. **Bookmark to Home Screen**: On iOS/Android, select "Add to Home Screen" to use it like a native mobile app!
2. **Paste & Send**: Copy job alerts from WhatsApp/LinkedIn/Telegram on your phone, paste into the app, and tap **"Generate & Send"**!
