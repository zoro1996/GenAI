import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import time
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Load environment and API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to call Gemini model
def get_gemini_response(input_text, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, image[0], prompt])
    return response.text

# Prepare image for API
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
    else:
        raise FileNotFoundError("No file uploaded")

# Generate PDF from report text
def generate_pdf(report_text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    text_object = c.beginText(40, height - 50)
    text_object.setFont("Helvetica", 12)

    for line in report_text.split("\n"):
        text_object.textLine(line)

    c.drawText(text_object)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Streamlit Page Config
st.set_page_config(page_title="🍽️ Calories Advisor", page_icon="🥗", layout="centered")

# Sidebar with Info
with st.sidebar:
    st.title("🍎 Calories Advisor")
    st.markdown("""
        Upload a food image and get a detailed breakdown of:
        - Calories per item  
        - Nutrition balance  
        - Healthiness rating  
    """)
    st.info("Supports: JPG, JPEG, PNG")

# Main Header
st.title("🥦 Calories & Nutrition Checker")

# User Input + Image Upload
col1, col2 = st.columns(2)
with col1:
    user_input = st.text_input("🔍 Add your prompt (optional)", placeholder="e.g., Focus on sugar content")

with col2:
    uploaded = st.file_uploader("📷 Upload a food image", type=["jpg", "jpeg", "png"], key="file_uploader")

# Clear image if user clicks "X"
if "file_uploader" in st.session_state and st.session_state["file_uploader"] is None:
    if "uploaded_file" in st.session_state:
        del st.session_state["uploaded_file"]

# Save to session for consistent access
if uploaded:
    st.session_state["uploaded_file"] = uploaded

uploaded_file = st.session_state.get("uploaded_file", None)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="🍛 Your Uploaded Meal", use_container_width=True)

# Prompt Template
input_prompt = """
You are an expert nutritionist. Analyze the image to detect food items and calculate total calories. 
Give a detailed report in this format:

1. Item 1 - X calories  
2. Item 2 - Y calories  
...

Then summarize:
- Overall healthiness
- Macronutrient split: carbs, fats, proteins, fiber, sugar
- Suggestions (if any)
At the end of the report, write: '##HEALTHY##', '##UNHEALTHY##', or '##MODERATE##'
"""

# Submit button
if st.button("📊 Analyze Meal"):
    with st.spinner("Analyzing image and calculating nutrition..."):
        time.sleep(1.5)  # Fake load time
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, user_input)

    st.success("✅ Analysis Complete")
    st.subheader("📝 Nutritional Report")
    st.markdown(response)

    # Generate and offer PDF download
    pdf_file = generate_pdf(response)
    st.download_button(
        label="📄 Download Report as PDF",
        data=pdf_file,
        file_name="nutrition_report.pdf",
        mime="application/pdf"
    )

    # Optional extra feature
    with st.expander("💡 How to interpret this"):
        st.write("""
            - Try uploading different meal types  
            - Add extra questions like: "Is this suitable for diabetics?"  
            - Calorie values are approximate  
        """)

    if "##UNHEALTHY##" in response:
        health_status = "🔴 Healthiness: **Unhealthy**"
    elif "##HEALTHY##" in response:
        health_status = "🟢 Healthiness: **Healthy**"
    elif "##MODERATE##" in response:
        health_status = "🟡 Healthiness: **Moderate**"
    else:
        health_status = "⚠️ Healthiness: **Unknown**"

    st.markdown("### " + health_status)
