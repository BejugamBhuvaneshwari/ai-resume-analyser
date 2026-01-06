import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config (must be first Streamlit command)
st.set_page_config(
    page_title="AI Resume Critiquer",
    page_icon="📄🤖",
    layout="centered"
)

st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

# Get Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Groq API key not found. Please set GROQ_API_KEY in .env file.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# File uploader
uploaded_file = st.file_uploader(
    "Upload your resume (PDF or TXT)",
    type=["pdf", "txt"]
)

job_role = st.text_input(
    "Enter the job role you're targeting (optional)"
)

analyze = st.button("Analyze Resume")

# ---------- Helper Functions ----------

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore")

# ---------- Main Logic ----------

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("The uploaded file has no readable content.")
            st.stop()

        prompt = f"""
Please analyze the following resume and provide constructive feedback.

Focus on:
1. Content clarity and impact
2. Skills presentation
3. Experience descriptions
4. Improvements for {job_role if job_role else "general job applications"}

Resume Content:
{file_content}

Provide the feedback in a clear, structured format with actionable suggestions.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume reviewer with strong HR and recruitment experience."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )

        st.markdown("## 📊 Resume Analysis")
        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
