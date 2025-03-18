#  All functions except URL
import os
os.environ["PATH"] += os.pathsep + "/usr/bin"
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"

import shutil
import io
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI  # Use the new client-based API
import openai
import pandas as pd
import whisper
import concurrent.futures  # For asynchronous execution

# -------------------------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------------------------------------------------------
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OPENAI_API_KEY not found! Please set your API key in the .env file.")
    st.stop()

# -------------------------------------------------------------------------
# IMPORT CONFIGURATION VARIABLES
# -------------------------------------------------------------------------
from config import (
    headline,
    role1,
    prompt_article_template,
    role2,
    prompt2,
    role3,
    prompt3,
    role4,
    prompt4,
    role5,
    prompt5,
    fine_tuning,
    chatbot_mode,
)

# Set an approximate maximum characters threshold for the combined file content (as a proxy for token limit)
MAX_INPUT_FILE_CHARS = 500000


# -------------------------------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Set all text elements to 16px except the title, which is 64px*/
    * {
         font-size: 16px !important;
    }
    /* Center the title and set its font size to 64px */
    .app-title {
         text-align: center;
         font-size: 64px;
         font-weight: bold;
         margin-bottom: 1rem;
    }
    /* Style the delete button with a transparent background and red emoji text */
    div[data-testid="stSidebar"] button[id^="delete_"] {
        background-color: transparent;
        color: red;
        border: none;
        font-size: 16px;
        padding: 0;
    }
    /* Blinking red text for file processing */
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0; }
    }
    .blinking-line {
      font-size: 64px;
      color: red;
      text-align: center;
      animation: blink 1.5s infinite;
      margin-bottom: 1rem;
    }
    /* Blinking green text for generation process */
    .blinking-green {
      font-size: 64px;
      color: green;
      text-align: center;
      animation: blink 1.5s infinite;
      margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------------
# INIT OPENAI CLIENT
# -------------------------------------------------------------------------
client = OpenAI(api_key=openai_api_key)

# -------------------------------------------------------------------------
# TITLE (using the headline variable)
# -------------------------------------------------------------------------
st.markdown(f'<div class="app-title">{headline}</div>', unsafe_allow_html=True)

# (Placeholder for file-processing blinking message)
blinking_placeholder = st.empty()

# -------------------------------------------------------------------------
# FILE STORAGE SETUP
# -------------------------------------------------------------------------
TEMP_FOLDER = "temp_uploaded_files"
if os.path.exists(TEMP_FOLDER):
    shutil.rmtree(TEMP_FOLDER, ignore_errors=True)
os.makedirs(TEMP_FOLDER)

# -------------------------------------------------------------------------
# FILE UPLOAD FUNCTIONALITY
# -------------------------------------------------------------------------
st.sidebar.header("Upload Files")

uploaded_files = st.sidebar.file_uploader(
    "Choose files",
    type=["txt", "csv", "xlsx", "pptx", "pdf", "mp4", "mp3", "docx", "png", "jpg", "msg"],
    accept_multiple_files=True,
    key="file_uploader",
)

if uploaded_files:
    # Show blinking red line while reading/transcribing files
    blinking_placeholder.markdown(
        "<div style='font-size:64px; color:red; text-align:center; animation:blink 1.5s infinite; margin-bottom:1rem;'>"
        "Please wait for a few minutes while AI transcribes your file . . .</div>",
        unsafe_allow_html=True,
    )
    for file in uploaded_files:
        file_path = os.path.join(TEMP_FOLDER, file.name)
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(file.read())

st.sidebar.header("Uploaded Files")
saved_files = os.listdir(TEMP_FOLDER)
for file_name in saved_files:
    cols = st.sidebar.columns([1, 5])
    if cols[0].button("🗑️", key=f"delete_{file_name}"):
        os.remove(os.path.join(TEMP_FOLDER, file_name))
        st.rerun()
    cols[1].markdown(file_name)

# -------------------------------------------------------------------------
# LOAD WHISPER MODEL
# -------------------------------------------------------------------------
try:
    whisper_model = whisper.load_model("base")
except Exception as e:
    st.error(f"Error loading Whisper model: {e}")

# -------------------------------------------------------------------------
# PROCESS UPLOADED FILES
# -------------------------------------------------------------------------
attached_text_list = []
temp_counter = 1  # Counter for naming temporary prompt variables

for file_name in saved_files:
    file_path = os.path.join(TEMP_FOLDER, file_name)
    extension = file_name.split(".")[-1].lower()
    st.subheader(f"File: {file_name}")

    with open(file_path, "rb") as f:
        file_bytes = f.read()
    file_obj = io.BytesIO(file_bytes)

    text = ""
    if extension == "txt":
        text = file_obj.read().decode("utf-8")
        st.text_area("File content", text, height=200, key=f"txt_{file_name}")

    elif extension == "csv":
        file_obj.seek(0)
        df = pd.read_csv(file_obj)
        text = df.to_csv(index=False)
        st.dataframe(df, key=f"csv_{file_name}")

    elif extension == "xlsx":
        file_obj.seek(0)
        try:
            import openpyxl
        except ImportError:
            st.error("Missing optional dependency 'openpyxl'. Please install it using 'pip install openpyxl'.")
        else:
            df = pd.read_excel(file_obj, engine="openpyxl")
            text = df.to_csv(index=False)
            st.dataframe(df, key=f"xlsx_{file_name}")

    elif extension == "pptx":
        try:
            from pptx import Presentation
            file_obj.seek(0)
            prs = Presentation(file_obj)
            ppt_text = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        ppt_text.append(shape.text)
            text = "\n".join(ppt_text)
            st.text_area("Extracted text", text, height=200, key=f"pptx_{file_name}")
        except ImportError:
            st.error("Module 'python-pptx' is not installed. Please add it to requirements.txt")

    elif extension == "pdf":
        try:
            import PyPDF2
            file_obj.seek(0)
            pdf_reader = PyPDF2.PdfReader(file_obj)
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text() or "")
            text = "".join(text_parts)
            st.text_area("Extracted text", text, height=200, key=f"pdf_{file_name}")
        except ImportError:
            st.error("Module 'PyPDF2' is not installed. Please add it to requirements.txt")

    elif extension == "docx":
        try:
            from docx import Document
            file_obj.seek(0)
            doc = Document(file_obj)
            doc_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    doc_text.append(para.text)
            text = "\n".join(doc_text)
            st.text_area("Extracted text", text, height=200, key=f"docx_{file_name}")
        except ImportError:
            st.error("Module 'python-docx' is not installed. Please add it to requirements.txt")

    elif extension == "msg":
        try:
            import extract_msg
            file_obj.seek(0)
            msg = extract_msg.Message(file_obj)
            text = msg.body
            st.text_area("Extracted text", text, height=200, key=f"msg_{file_name}")
        except ImportError:
            st.error("Module 'extract_msg' is not installed. Please add it to requirements.txt")

    elif extension in ["png", "jpg"]:
        try:
            from PIL import Image
            import pytesseract
            file_obj.seek(0)
            image = Image.open(file_obj)
            text = pytesseract.image_to_string(image)
            st.image(image, caption="Uploaded image", use_container_width=True)
            st.text_area("Extracted text", text, height=200, key=f"{extension}_{file_name}")
        except ImportError:
            st.error("Module 'Pillow' or 'pytesseract' is not installed. Please add them to requirements.txt")

    elif extension == "mp4":
        file_obj.seek(0)
        st.video(file_obj)
        try:
            temp_video_path = os.path.join(TEMP_FOLDER, f"temp_{file_name}")
            with open(temp_video_path, "wb") as temp_f:
                temp_f.write(file_obj.read())
            result = whisper_model.transcribe(temp_video_path)
            text = result.get("text", "")
            st.text_area("Transcription", text, height=200, key=f"mp4_{file_name}")
            os.remove(temp_video_path)
        except Exception as e:
            st.error(f"Error transcribing video: {e}")

    elif extension == "mp3":
        file_obj.seek(0)
        st.audio(file_obj)
        try:
            temp_audio_path = os.path.join(TEMP_FOLDER, f"temp_{file_name}")
            with open(temp_audio_path, "wb") as temp_f:
                temp_f.write(file_obj.read())
            result = whisper_model.transcribe(temp_audio_path)
            text = result.get("text", "")
            st.text_area("Transcription", text, height=200, key=f"mp3_{file_name}")
            os.remove(temp_audio_path)
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")

    else:
        st.warning(f"Unsupported file type: {file_name}")

    if text:
        attached_text_list.append(text)
        globals()[f"prompt_article_temp{temp_counter}"] = text
        temp_counter += 1

blinking_placeholder.empty()

attached_text = "\n".join(attached_text_list)

# -------------------------------------------------------------------------
# MAIN INTERFACE
# -------------------------------------------------------------------------
# Define output containers so they are always available.
article_container = st.empty()
title_container = st.empty()
subheading_container = st.empty()
slug_container = st.empty()
hashtags_container = st.empty()

# Place a horizontal rule above the top query section
st.markdown("---")

if chatbot_mode:
    if "input_counter" not in st.session_state:
        st.session_state.input_counter = 1

    if st.button("Add another query"):
        st.session_state.input_counter += 1

    queries = []

    for i in range(st.session_state.input_counter):
        st.markdown(f"#### Query Block #{i+1}")
        top_cols = st.columns([3, 1])
        with top_cols[0]:
            st.markdown("Enter your topic or query (up to 500 lines):")
        with top_cols[1]:
            generate_pressed = st.button("Generate", key=f"generate_top_{i}")
            if generate_pressed:
                st.session_state[f"query_generated_{i}"] = True

        query = st.text_area("", key=f"user_input_{i}", height=200)
        queries.append(query)

        bottom_cols = st.columns([3, 1])
        with bottom_cols[0]:
            st.markdown("Enter your topic or query (up to 500 lines):")
        with bottom_cols[1]:
            bottom_generate = st.button("Generate", key=f"generate_bottom_{i}")
            if bottom_generate:
                st.session_state[f"query_generated_{i}"] = True

        st.markdown("---")

    user_input = "\n".join(queries)
else:
    user_input = st.text_area("Enter your topic or query (up to 500 lines):", key="user_input_single", height=200)
    single_generate = st.button("Generate", key="single_generate")
    if single_generate and user_input.strip():
        st.write("Processing query:", user_input)

if chatbot_mode:
    generate_trigger = any(st.session_state.get(f"query_generated_{i}", False) for i in range(st.session_state.input_counter))
else:
    generate_trigger = single_generate

if generate_trigger:
    if user_input.strip() or attached_text.strip():
        if len(attached_text) > MAX_INPUT_FILE_CHARS:
            st.markdown(
                "<div style='font-size:64px; text-align:center;'>"
                "The total of the Input files is too large. Please remove some and try again"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            def generate_content(prompt_article):
                response_article = client.chat.completions.create(
                    model="o3-mini",
                    messages=[
                        {"role": "system", "content": role1},
                        {"role": "user", "content": prompt_article},
                    ],
                    max_completion_tokens=20000,
                )
                article = response_article.choices[0].message.content

                response_title = client.chat.completions.create(
                    model="o3-mini",
                    messages=[
                        {"role": "system", "content": role2},
                        {"role": "user", "content": f"{prompt2}\n\nContext:\n{prompt_article}\n\nTitle:"},
                    ],
                    max_completion_tokens=1000,
                )
                title = response_title.choices[0].message.content

                response_subheading = client.chat.completions.create(
                    model="o3-mini",
                    messages=[
                        {"role": "system", "content": role3},
                        {"role": "user", "content": f"{prompt3}\n\nContext:\n{prompt_article}\n\nSub-Heading:"},
                    ],
                    max_completion_tokens=1000,
                )
                subheading = response_subheading.choices[0].message.content

                response_slug = client.chat.completions.create(
                    model="o3-mini",
                    messages=[
                        {"role": "system", "content": role4a},
                        {"role": "user", "content": f"{prompt4}\n\nContext:\n{prompt_article}\n\nSocial Media Post:"},
                    ],
                    max_completion_tokens=1500,
                )
                slug = response_slug.choices[0].message.content

                response_hashtags = client.chat.completions.create(
                    model="o3-mini",
                    messages=[
                        {"role": "system", "content": role5},
                        {"role": "user", "content": f"{prompt5}\n\nContext:\n{prompt_article}\n\nHashtags:"},
                    ],
                    max_completion_tokens=1000,
                )
                hashtags = response_hashtags.choices[0].message.content

                return article, title, subheading, slug, hashtags

            gen_placeholder = st.empty()
            gen_placeholder.markdown(
                "<div style='font-size:128px; color:green; text-align:center; animation:blink 1.5s infinite; margin-bottom:1rem;'>"
                "Generating content...</div>",
                unsafe_allow_html=True,
            )
            file_context = f"\nAttached file content:\n{attached_text}" if attached_text.strip() else ""
            prompt_article = prompt_article_template.format(file_context=file_context, topic=user_input) + fine_tuning

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(generate_content, prompt_article)
                article, title, subheading, slug, hashtags = future.result()

            article_container.markdown("### Opinion Journalism Article (800 words)\n\n" + article)
            title_container.markdown("### Title\n\n" + title)
            subheading_container.markdown("### Sub-heading\n\n" + subheading)
            slug_container.markdown("### Social Media Post\n\n" + slug)
            hashtags_container.markdown("### 10 Hashtags\n\n" + hashtags)

            from docx import Document
            doc = Document()
            doc.add_heading("Opinion Journalism Article (800 words)", level=3)
            doc.add_paragraph(article)
            doc.add_heading("Title", level=3)
            doc.add_paragraph(title)
            doc.add_heading("Sub-heading", level=3)
            doc.add_paragraph(subheading)
            doc.add_heading("Social Media Post", level=3)
            doc.add_paragraph(slug)
            doc.add_heading("10 Hashtags", level=3)
            doc.add_paragraph(hashtags)
            doc_io = io.BytesIO()
            doc.save(doc_io)
            doc_io.seek(0)
            st.download_button("Download DOCX", data=doc_io, file_name="results.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            df = pd.DataFrame({
                "Section": ["Opinion Journalism Article", "Title", "Sub-heading", "Social Media Post", "10 Hashtags"],
                "Content": [article, title, subheading, slug, hashtags]
            })
            excel_io = io.BytesIO()
            with pd.ExcelWriter(excel_io, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Results")
            excel_io.seek(0)
            st.download_button("Download XLSX", data=excel_io, file_name="results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            from pptx import Presentation
            from pptx.util import Inches
            prs = Presentation()
            def add_slide(prs, title_text, content_text):
                slide = prs.slides.add_slide(prs.slide_layouts[5])
                txBox = slide.shapes.add_textbox(Inches(1), Inches(0.5), Inches(8), Inches(1))
                tf = txBox.text_frame
                tf.text = title_text
                txBox2 = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(4))
                tf2 = txBox2.text_frame
                tf2.text = content_text
            add_slide(prs, "Opinion Journalism Article (800 words)", article)
            add_slide(prs, "Title", title)
            add_slide(prs, "Sub-heading", subheading)
            add_slide(prs, "Social Media Post", slug)
            add_slide(prs, "10 Hashtags", hashtags)
            ppt_io = io.BytesIO()
            prs.save(ppt_io)
            ppt_io.seek(0)
            st.download_button("Download PPTX", data=ppt_io, file_name="results.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")

            gen_placeholder.empty()
    else:
        st.warning("Please enter a valid topic or query, or attach a file.")
