import streamlit as st
import os
import io
import matplotlib.pyplot as plt
import core_utils

from core_utils import (
    TEMP_FOLDER,
    create_temp_folder,
    delete_file,
    list_files,
    initialize_openai_client,
    headline,
    chatbot_mode,
    prompt_article_template,
    fine_tuning,
    MAX_INPUT_FILE_CHARS,
)

from data_processing import (
    process_txt,
    process_csv,
    process_xlsx,
    process_pptx,
    process_pdf,
    process_docx,
    process_image,
    transcribe_audio_video,
    download_media,
)

from ui_graphics import (
    setup_custom_css,
    blinking_message,
    display_extracted_text,
    display_extracted_text,
    display_extracted_text,
    display_extracted_text,
    draw_data_graph,
    display_extracted_text,
    display_extracted_text,
)

# Load Whisper explicitly here:
import whisper
try:
    whisper_model = whisper.load_model("base")
except Exception as e:
    st.error(f"Error loading Whisper model: {e}")


# ------------------ Initial Setup & UI ----------------------
setup_custom_css()
st.markdown(f'<div class="app-title">{core_utils.headline}</div>', unsafe_allow_html=True)

draw_data_graph()

# ------------------ File Upload & Sidebar ----------------------
uploaded_files = st.sidebar.file_uploader(
    "Choose files",
    type=["txt", "csv", "xlsx", "pptx", "pdf", "mp4", "mp3", "docx", "png", "jpg", "msg", "htm", "html"],
    accept_multiple_files=True,
)

core_utils.ensure_temp_folder_exists()

if uploaded_files:
    ui_graphics.show_blinking_message("Transcribing files, please wait...", color="red")
    for file in uploaded_files:
        file_path = os.path.join(TEMP_FOLDER, file.name)
        if not os.path.exists(file_path):
            with open(file_path, "wb") as f:
                f.write(file.read())
    st.rerun()

st.sidebar.header("Uploaded Files")
# saved_files = os.listdir(core_utils.TEMP_FOLDER)
saved_files = list_files(TEMP_FOLDER)

for file_name in saved_files:
    cols = st.sidebar.columns([1, 5])
    if cols[0].button("🗑️", key=f"delete_{file_name}"):
        core_utils.delete_file(file_name)
        st.rerun()
    cols[1].markdown(file_name)

# ------------------ Media Download (YT-DLP) ----------------------
st.sidebar.markdown("---")
st.sidebar.header("Media Download")
video_url = st.sidebar.text_input("Enter the video URL:")
file_name = st.sidebar.text_input("Enter desired file name (without extension):")
format_choice = st.sidebar.selectbox("Select format:", ["MP3 (Audio-only)", "MP4 (Video)"])

if st.sidebar.button("Download Media"):
    if not video_url or not file_name:
        st.sidebar.error("Please provide both the video URL and file name.")
    else:
        with st.spinner("Downloading media..."):
            success, message = download_media(video_url, file_name, format_choice, TEMP_FOLDER)
            if success:
                st.sidebar.success(message)
                st.rerun()
            else:
                st.sidebar.error(f"Download failed: {message}")

# ------------------ File Processing ----------------------
attached_text_list = []
attached_text_list.append(text)
saved_files = core_utils.list_files(TEMP_FOLDER)

for file_name in saved_files:
    file_path = os.path.join(TEMP_FOLDER, file_name)
    extension = file_name.split(".")[-1].lower()

    st.subheader(f"File: {file_name}")

    with open(file_path, "rb") as f:
        file_bytes = f.read()
    file_obj = io.BytesIO(file_bytes)

    text = ""
    df = None

    if extension == "txt":
        text = process_txt(file_bytes)
        st.text_area("Content", text, height=200)
    elif extension == "csv":
        text, df = process_csv(file_obj)
        st.dataframe(df)
    elif extension == "xlsx":
        text, df = process_xlsx(file_obj)
        st.dataframe(df)
    elif extension == "pptx":
        text = process_pptx(file_obj)
        st.text_area("Content", text, height=200)
    elif extension == "pdf":
        text = process_pdf(file_obj)
        st.text_area("Content", text, height=200)
    elif extension == "docx":
        text = process_docx(file_obj)
        st.text_area("Content", text, height=200)
    elif extension in ["png", "jpg"]:
        text = process_image(file_obj)
        st.image(file_obj, caption=file_name, use_container_width=True)
        st.text_area("Extracted Text", text, height=200)
    elif extension in ["mp3", "mp4"]:
        st.audio(file_bytes) if extension == "mp3" else st.video(file_bytes)
        text = transcribe_audio_video(whisper_model, file_path)
        st.text_area("Transcription", text, height=200)
    else:
        st.warning(f"Unsupported file type: {file_name}")

    if text:
        core_utils.attached_text_list.append(text)

attached_text = "\n".join(core_utils.attached_text_list)

# ------------------ Prompt and OpenAI Processing ----------------------
user_input = st.text_area("Enter your topic or query:", height=200)
if st.button("Generate"):
    total_length = len(attached_text)
    if total_length > MAX_INPUT_FILE_CHARS:
        st.error("Attached file contents exceed the allowed limit. Please reduce file sizes.")
    else:
        with st.spinner("Generating content..."):
            results = core_utils.generate_content_from_openai(client, user_input, attached_text)
            ui_graphics.display_results(results=results)

