import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# App config
st.set_page_config(page_title="YouTube Notes Generator", layout="centered")
st.title("🎬 YouTube Transcript to 📋 Detailed Notes")
st.markdown("Convert any YouTube video into clean, structured notes with the power of AI!")

# Session state for history
if "history" not in st.session_state:
    st.session_state["history"] = []

# Sidebar: Summary history
st.sidebar.title("🗂️ Summary History")
if st.session_state["history"]:
    for idx, entry in enumerate(st.session_state["history"]):
        if st.sidebar.button(f"📄 Summary {idx + 1}"):
            st.markdown(f"## 📌 Summary {idx + 1}:\n")
            st.write(entry["summary"])
            st.caption(f"🌍 Language: {entry['language']} | 📋 Format: {entry['format']}")

# Sidebar: Options
summary_format = st.sidebar.selectbox("📋 Summary Format", ["Detailed", "Brief"])
selected_language = st.sidebar.selectbox("🌍 Output Language", ["English", "Spanish", "French", "German", "Hindi"])

# Prompt templates
def get_prompt(format_type, language):
    tone_instruction = "a concise, high-level summary" if "Brief" in format_type else "a thorough, detailed breakdown"

    return f"""
You are a professional YouTube video summarizer.

Your task is to generate {tone_instruction} in bullet points.
Focus only on the most important takeaways, and eliminate any filler or repetition.
Respond in {language}.
Make sure the summary tone matches the requested format: {format_type}.

Transcript:
"""



# Transcript extractor
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1].split("&")[0]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        return None

# Chunking for large inputs
def chunk_text(text, chunk_size=4000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Generate summary using Gemini
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    chunks = chunk_text(transcript_text)
    full_summary = ""
    for i, chunk in enumerate(chunks):
        response = model.generate_content(prompt + chunk)
        full_summary += f"\n{response.text.strip()}"
    return full_summary.strip()

# Main input
youtube_link = st.text_input("🔗 Enter YouTube Video Link")

# Display thumbnail
if youtube_link and "youtube.com/watch" in youtube_link:
    try:
        video_id = youtube_link.split("=")[1].split("&")[0]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width =True)
    except:
        st.warning("Could not extract video thumbnail.")

# Process
if st.button("📄 Get Detailed Notes"):
    with st.spinner("Fetching transcript and generating notes..."):
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            try:
                prompt = get_prompt(summary_format, selected_language)
                summary = generate_gemini_content(transcript_text, prompt)
                st.success("✅ Notes generated successfully!")

                st.markdown("## 📌 Generated Summary:")
                st.write(summary)

                # Word count
                word_count = len(summary.split())
                st.caption(f"📝 Word count: {word_count} | 🌍 Language: {selected_language}")

                # Save to session state
                st.session_state["history"].append({
                    "summary": summary,
                    "language": selected_language,
                    "format": summary_format,
                })

                # Download options
                st.download_button("💾 Download as TXT", data=summary, file_name="youtube_notes.txt")
                st.download_button("📥 Download as Markdown", data=f"## YouTube Summary\n\n{summary}",
                                   file_name="youtube_notes.md", mime="text/markdown")
                html_summary = summary.replace('\n', '<br>')
                st.download_button(
    "🌐 Download as HTML",
    data=f"<html><body><h2>YouTube Summary</h2><p>{html_summary}</p></body></html>",
    file_name="youtube_notes.html",
    mime="text/html"
)

            except Exception as e:
                st.error("❌ An error occurred while generating notes.")
                st.exception(e)
        else:
            st.warning("⚠️ Could not retrieve transcript. The video might not have captions or is restricted.")
