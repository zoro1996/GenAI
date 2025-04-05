from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
import json
from PIL import Image
import fitz
import pdfplumber
import PyPDF2 as pdf
import google.generativeai as genai
from openai import OpenAI

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
openai_api_key = os.getenv("OPENAI_API_KEY")

# PDF text extraction using PyPDF2 for Gemini JSON-style
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# PDF image generation for Gemini
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pix = doc[0].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [{
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# PDF text extraction using pdfplumber for OpenAI & Gemini Flash
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip() if text else "No text extracted from PDF."

# OpenAI response
def get_openai_response(input_text, pdf_text, prompt):
    if not openai_api_key:
        st.error("⚠️ OpenAI API Key is required! Please enter your key in the sidebar.")
        return ""
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Job Description: {input_text}\nResume Content: {pdf_text}"}
        ],
        max_tokens=1024
    )
    return response.choices[0].message.content

# Gemini Flash for normal mode
def get_gemini_response(input_text, pdf_content, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        generation_config = {
            "temperature": 0.7,
            "top_p": 1.0,
            "top_k": 32,
            "max_output_tokens": 2048,
        }
        response = model.generate_content(
            [input_text, pdf_content[0], prompt],
            generation_config=generation_config,
            safety_settings=[{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}]
        )
        return response.text
    except Exception as e:
        if "Deadline Exceeded" in str(e) or "timeout" in str(e).lower():
            return "The request timed out. Try using a simpler resume or OpenAI instead."
        else:
            return f"Error: {str(e)}"

# Gemini JSON-style evaluation
def get_gemini_json_response(prompt):
    model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest')
    response = model.generate_content(prompt)
    try:
        parsed = json.loads(response.text)
        return json.dumps(parsed, indent=4)
    except Exception:
        return response.text

# JSON-style prompt template
json_prompt_template = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech fields like AI, ML, software engineering, data science,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and provide the best assistance for improving resumes.
Assign a percentage Match based on the JD, and list the missing keywords with high accuracy.

resume: {resume_text}
description: {job_description}

I want the response in one single string having the structure:
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# Streamlit UI Setup
st.set_page_config(page_title="ATS Resume Expert", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>ATS Tracking System</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("ATS Resume Expert")
    st.markdown("Optimize your resume for ATS tracking and job matching.")
    model_choice = st.selectbox("Choose AI Model", ["OpenAI GPT-4", "Google Gemini"])
    evaluation_mode = st.radio("Select Evaluation Mode", ["Standard", "JSON Summary (Gemini Only)"])

    if model_choice == "OpenAI GPT-4":
        openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Input
input_text = st.text_area("🔍 **Enter Job Description:**", height=150, key="input")
uploaded_file = st.file_uploader("📄 **Upload your resume (PDF)...**", type=["pdf"])
if uploaded_file:
    st.success("✅ PDF Uploaded Successfully!")

# Buttons
col1, col2 = st.columns([1, 1])
with col1:
    submit1 = st.button("📑 Analyze Resume")
with col2:
    submit3 = st.button("📊 Percentage Match")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of ATS functionality.
Your task is to evaluate the resume against the provided job description. Provide a percentage match if the resume fits the job description.
The output should include:
1️⃣ **Percentage match**  
2️⃣ **Keywords missing**  
3️⃣ **Final thoughts**  
"""

# Logic
if (submit1 or submit3) and not uploaded_file:
    st.warning("⚠️ Please upload a resume to proceed.")

if uploaded_file:
    if evaluation_mode == "JSON Summary (Gemini Only)":
        resume_text = input_pdf_text(uploaded_file)
        final_prompt = json_prompt_template.format(resume_text=resume_text, job_description=input_text)
        response = get_gemini_json_response(final_prompt)
        st.subheader("📄 Gemini JSON Summary")
        st.text_area("Response", value=response, height=400)
    elif submit1:
        pdf_content = input_pdf_setup(uploaded_file)
        extracted_resume_text = extract_text_from_pdf(uploaded_file)

        if model_choice == "OpenAI GPT-4":
            response = get_openai_response(input_text, extracted_resume_text, input_prompt1)
        else:
            response = get_gemini_response(input_text, pdf_content, input_prompt1)

        st.subheader("📝 Resume Analysis")
        st.write(response)

    elif submit3:
        pdf_content = input_pdf_setup(uploaded_file)
        extracted_resume_text = extract_text_from_pdf(uploaded_file)

        if model_choice == "OpenAI GPT-4":
            response = get_openai_response(input_text, extracted_resume_text, input_prompt3)
        else:
            response = get_gemini_response(input_text, pdf_content, input_prompt3)

        st.subheader("📊 ATS Match Percentage")
        st.write(response)
