from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import pdf2image
import google.generativeai as genai
import pdfplumber
#from mlflow_evaluator import log_ats_evaluation  # Import MLflow evaluation module
# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip() if text else "No text extracted from PDF."

# Function to process PDF and convert first page to image
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]

        # Convert image to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format="JPEG")
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

# Function to generate AI response
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

# Streamlit UI Configuration
st.set_page_config(page_title="ATS Resume Expert", layout="wide")

# Sidebar for navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)  # Placeholder icon
    st.title("ATS Resume Expert")
    st.markdown("Optimize your resume for ATS tracking and job matching.")

# Main Content
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>ATS Tracking System</h1>", unsafe_allow_html=True)
st.markdown("---")

# Input Fields
input_text = st.text_area("🔍 **Enter Job Description:**", height=150, key="input")
uploaded_file = st.file_uploader("📄 **Upload your resume (PDF)...**", type=["pdf"])

if uploaded_file:
    st.success("✅ PDF Uploaded Successfully!")

# Buttons with better alignment
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
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Provide a percentage match if the resume fits the job description. 
The output should include:
1️⃣ **Percentage match**  
2️⃣ **Keywords missing**  
3️⃣ **Final thoughts**  
"""

# Handling button clicks
if submit1 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)

    #extracted_resume_text = extract_text_from_pdf(uploaded_file)  # Extract text

    response = get_gemini_response(input_prompt1, pdf_content, input_text)

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
    response = get_gemini_response(input_prompt3, pdf_content, input_text)
    st.subheader("📊 ATS Match Percentage")
    st.write(response)

elif (submit1 or submit3) and not uploaded_file:
    st.warning("⚠️ Please upload a resume to proceed.")
