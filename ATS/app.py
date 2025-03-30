from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import fitz  # PyMuPDF for PDF processing
import pdfplumber
import google.generativeai as genai
#import openai  # OpenAI API for responses
from openai import OpenAI

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
api_key = os.getenv("OPENAI_API_KEY")

#openai = OpenAI()

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip() if text else "No text extracted from PDF."

# Convert first page of PDF to image
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        pix = doc[0].get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# OpenAI API function
def get_openai_response(input_text, pdf_text, prompt):
    if not openai_api_key:
        st.error("⚠️ OpenAI API Key is required! Please enter your key in the sidebar.")
        return ""
    api_key = openai_api_key
    client = OpenAI(api_key=api_key)  # Initialize the client
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Job Description: {input_text}\nResume Content: {pdf_text}"}
        ],
        max_tokens=1024
    )
    return response.choices[0].message.content

# Google Gemini API function
def get_gemini_response(input_text, pdf_content, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Set generation config with longer timeouts
        generation_config = {
            "temperature": 0.7,
            "top_p": 1.0,
            "top_k": 32,
            "max_output_tokens": 2048,
        }
        
        # Call with safety settings and generation config
        response = model.generate_content(
            [input_text, pdf_content[0], prompt],
            generation_config=generation_config,
            safety_settings=[{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}]
        )
        return response.text
    except Exception as e:
        # Handle the error gracefully
        error_message = str(e)
        if "Deadline Exceeded" in error_message or "timeout" in error_message.lower():
            return "The request timed out. Your PDF might be too large or complex. Try using a simpler resume or the OpenAI model instead."
        else:
            return f"Error processing your request: {error_message}"

# Streamlit UI Configuration
st.set_page_config(page_title="ATS Resume Expert", layout="wide")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("ATS Resume Expert")
    st.markdown("Optimize your resume for ATS tracking and job matching.")
    
    # Dropdown to select model
    model_choice = st.selectbox("Choose AI Model", ["OpenAI GPT-4", "Google Gemini"])

    openai_api_key = None
    if model_choice == "OpenAI GPT-4":
        openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Main UI
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>ATS Tracking System</h1>", unsafe_allow_html=True)
st.markdown("---")

# Input Fields
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

# Handling button clicks
if submit1 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    extracted_resume_text = extract_text_from_pdf(uploaded_file)
    #extracted_resume_text = extract_text_from_pdf(uploaded_file)  # Extract text

    #response = get_gemini_response(input_prompt1, pdf_content, input_text)

    # Use selected AI model
    if model_choice == "OpenAI GPT-4":
        response = get_openai_response(input_text, extracted_resume_text, input_prompt1)
    else:
        response = get_gemini_response(input_text, pdf_content, input_prompt1)

     # Evaluate and log the response in MLflow
    #ats_match, coherence = log_ats_evaluation(input_text, extracted_resume_text, response)

    # st.subheader("📝 Resume Analysis")
    # st.write(response)
    # st.write(f"📊 **ATS Match Score:** {ats_match:.2f}%")
    # st.write(f"🔍 **Semantic Coherence:** {coherence:.2f}")

    st.subheader("📝 Resume Analysis")
    st.write(response)

elif submit3 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    extracted_resume_text = extract_text_from_pdf(uploaded_file)
    #response = get_gemini_response(input_prompt3, pdf_content, input_text)

    # Use selected AI model
    if model_choice == "OpenAI GPT-4":
        response = get_openai_response(input_text, extracted_resume_text, input_prompt3)
        print("response from openai")
    else:
        response = get_gemini_response(input_text, pdf_content, input_prompt3)
        print("response from gemini")

    st.subheader("📊 ATS Match Percentage")
    st.write(response)

elif (submit1 or submit3) and not uploaded_file:
    st.warning("⚠️ Please upload a resume to proceed.")
