import streamlit as st
import shutil
found_ffmpeg = shutil.which("ffmpeg")
if found_ffmpeg is None:
    st.error("ffmpeg not found in PATH. Please install ffmpeg or ensure it’s in PATH.")
else:
    st.write(f"Found ffmpeg at: {found_ffmpeg}")
