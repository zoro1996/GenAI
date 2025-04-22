# 🌟 GenAI Projects

This repository contains a collection of **Generative AI-based mini-projects** focused on solving real-world problems using modern machine learning techniques.

---

## 🧠 ATS Resume Expert

An AI-powered resume analyzer built with Streamlit. Upload your resume and a job description to instantly receive a professional evaluation, keyword match, and percentage fit using OpenAI GPT-4 or Google Gemini.

### 🧰 Features
- 📄 **Resume Upload**: Accepts resumes in PDF format  
- 📝 **Job Description Input**: Paste the job description directly into the app  
- 🤖 **AI Evaluation**:  
  - Choose between OpenAI GPT-4 or Google Gemini  
  - JSON-style structured analysis (Gemini only)  
- 📊 **ATS Match Report**:  
  - Percentage match against job description  
  - Missing keywords  
  - Summary of strengths and weaknesses  
- 📈 **Professional Insights**:  
  - Tailored evaluation for technical roles (AI, ML, Data Science, Software Engineering, etc.)

### 💡 Sample Use Cases
- Resume optimization for tech roles  
- Preparing for job applications  
- Identifying skills gaps and keyword mismatches  
- Getting recruiter-style feedback instantly

### 🚀 Tech Stack
- **Frontend/UI**: Streamlit  
- **AI Models**: OpenAI GPT-4, Google Gemini 1.5 Pro & Flash  
- **PDF Handling**: PyPDF2, pdfplumber, fitz (PyMuPDF), PIL  
- **Environment Management**: `dotenv`


## 🥗 Calorie Advisor
A smart nutrition analyzer built with Streamlit and powered by Google Gemini AI. Upload an image of your meal, and instantly get a breakdown of calories, nutritional balance, and a healthiness rating.

### 🧰 Features
- 📷 **Image Upload**: Supports JPG, JPEG, PNG formats
- 🧠 **AI-Powered Analysis**: Uses Gemini to analyze food images
- 📊 **Nutrition Breakdown**:
  - Per-item calorie estimates
  - Macronutrient split (carbs, fats, proteins, fiber, sugar)
  - Overall healthiness score
- 📝 **Detailed Report**: Download the analysis as a PDF
- 🔍 **Custom Prompts**: Ask the AI to focus on specific concerns (e.g., sugar content, diabetic suitability)

### 💡 Sample Use Cases
- Diet planning
- Health-conscious meal reviews
- Quick nutritional feedback on food pics
- Guidance for fitness and medical goals

### 🚀 Tech Stack
- **Frontend/UI**: Streamlit
- **AI Model**: Google Gemini 1.5 Flash
- **Extras**: ReportLab (PDF generation), PIL (image processing), `dotenv` for API management


## 🔹 YouTube Transcript Summarizer
A Streamlit web app that transforms any YouTube video into clean, structured notes using Google’s Gemini model.

### 🛠️ Features
- 🎥 **Input**: YouTube video link
- 📋 **Output**: AI-generated summary in detailed or brief format, available in multiple languages
- 🌐 **Languages Supported**: English, Spanish, French, German, Hindi
- 💾 **Download Options**: TXT, Markdown, HTML
- ✅ **Automatically extracts transcripts from YouTube videos**
- 🧠 **Uses Gemini Pro to summarize content in bullet points**
- 🌍 **Lets users choose output format and language**
- 💾 **Allows summary downloads in multiple formats**
- 📚 **Keeps summary history in session**

### 💡 Sample Use Cases
- Creating notes from educational videos
- Summarizing tutorials or lectures
- Multilingual recap of talks

### 🚀 Tech Stack
- **Frontend/UI**: Streamlit
- **AI Model**: Google Gemini
- **Backend**: YouTube Transcript API, Python

