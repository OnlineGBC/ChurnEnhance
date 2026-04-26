#!/usr/bin/env python3
"""
Create a 2-3 minute YouTube walkthrough video of CustomerChurn AI.

Captures screenshots from the live Flask app, generates TTS narration
via OpenAI API, and assembles everything into an MP4 video.
"""

import os
import time
import pathlib
from dotenv import load_dotenv

load_dotenv()

# Fix Windows line-ending \r in .env values
if os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"].strip()

# ── Paths ────────────────────────────────────────────────────────────────
BASE_DIR = pathlib.Path(__file__).parent
VIDEO_DIR = BASE_DIR / "video"
SCREENSHOTS_DIR = VIDEO_DIR / "screenshots"
AUDIO_DIR = VIDEO_DIR / "audio"
OUTPUT_FILE = VIDEO_DIR / "CustomerChurnAI_Walkthrough.mp4"

for d in [VIDEO_DIR, SCREENSHOTS_DIR, AUDIO_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Configuration ────────────────────────────────────────────────────────
APP_BASE_URL = "http://localhost:8503"
CUSTOMER_NO = "1108018"  # Top-scored customer for detail view

# Each segment: (filename, url_or_None, narration_text)
# url_or_None = None means generate a title/outro card with Pillow
SEGMENTS = [
    (
        "title",
        None,
        "Welcome to CustomerChurn AI — a multi-agent system for Laborie "
        "Medical Technologies that predicts customer churn, diagnoses root "
        "causes, and identifies market expansion opportunities."
    ),
    (
        "dashboard",
        "/",
        "This is the main dashboard. At a glance, you can see the total "
        "customer count, red and yellow flag customers at risk of churning, "
        "and the number of AI agent runs completed. Below, recent agent runs "
        "show which AI crews have been executed and their status."
    ),
    (
        "upload",
        "/upload",
        "The Upload Data page lets you import customer transaction data. "
        "You can upload a CSV file directly, or load an existing file from "
        "the server. Threshold settings let you define what constitutes a "
        "yellow or red flag based on days of inactivity."
    ),
    (
        "sales_flags",
        "/flags/sales",
        "Sales Flags identifies customers at risk based on sales inactivity. "
        "Yellow flags indicate moderate inactivity, while red flags signal "
        "extended periods without transactions. You can adjust thresholds and "
        "download the flagged customer lists as CSV files."
    ),
    (
        "product_flags",
        "/flags/product",
        "Product Flags works similarly but at the product level, showing "
        "which specific customer-product combinations have gone inactive. "
        "This helps pinpoint which product lines are losing traction with "
        "individual customers."
    ),
    (
        "retention",
        "/retention",
        "The Retention AI dashboard is powered by a crew of AI agents. The "
        "churn risk scores table shows each customer's risk score, risk level, "
        "diagnosis, and confidence — all in one unified view. Customer names "
        "are displayed alongside customer numbers for easy identification. "
        "Below, the intervention queue lists recommended actions assigned to "
        "team members."
    ),
    (
        "customer_detail",
        f"/retention/{CUSTOMER_NO}",
        "Clicking on any customer number opens a detailed view. Here you can "
        "see the customer's profile information, their AI-generated churn "
        "risk assessment with contributing factors, the diagnosed failure "
        "mode, and their recent transaction history."
    ),
    (
        "market_access",
        "/market-access",
        "The Market Access AI dashboard helps identify growth opportunities. "
        "AI-generated Ideal Customer Profiles define target segments, while "
        "segment scores rank opportunities by estimated lifetime value and "
        "recommended sales channels."
    ),
    (
        "chat",
        "/chat",
        "The Chat interface lets you ask questions in natural language. For "
        "example, you can ask why a specific customer is at risk, or request "
        "growth opportunities in a particular region. The AI orchestrator "
        "routes your question to the appropriate agent crew."
    ),
    (
        "outro",
        None,
        "CustomerChurn AI — powered by LangGraph agents, Flask, and "
        "PostgreSQL. Select your preferred LLM model from the top navigation "
        "bar. Thank you for watching."
    ),
]


# ── Step 1: Generate title/outro cards with Pillow ──────────────────────
def create_title_card(filename, lines, subtitle=None):
    """Create a branded title or outro card image."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), color=(74, 117, 112))  # brand-teal-deeper

    draw = ImageDraw.Draw(img)

    # Try to get a decent font
    font_large = None
    font_small = None
    for font_path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        if os.path.exists(font_path):
            font_large = ImageFont.truetype(font_path, 64)
            font_small = ImageFont.truetype(font_path, 36)
            break
    if font_large is None:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Draw main lines centered
    y = H // 2 - len(lines) * 45
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), line, fill="white", font=font_large)
        y += 90

    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=font_small)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y + 30), subtitle, fill=(250, 243, 224), font=font_small)

    out_path = SCREENSHOTS_DIR / filename
    img.save(out_path)
    print(f"  Created card: {out_path}")
    return out_path


# ── Step 2: Capture screenshots with Selenium ───────────────────────────
def capture_screenshots():
    """Capture screenshots from the live Flask app."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    print("\n📸 Capturing screenshots...")

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--force-device-scale-factor=1")
    opts.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1920, 1080)

    screenshot_paths = []

    for name, url, _narration in SEGMENTS:
        if url is None:
            # Will be generated as a card
            if name == "title":
                path = create_title_card(
                    f"{name}.png",
                    ["CustomerChurn AI", "Multi-Agent Churn Analysis"],
                    "Laborie Medical Technologies"
                )
            else:
                path = create_title_card(
                    f"{name}.png",
                    ["CustomerChurn AI"],
                    "Powered by LangGraph  |  Flask  |  PostgreSQL"
                )
            screenshot_paths.append(path)
        else:
            full_url = APP_BASE_URL + url
            print(f"  Navigating to {full_url} ...")
            driver.get(full_url)
            time.sleep(3)  # Let page render fully

            # Scroll to show content, then back to top for clean screenshot
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
            time.sleep(0.5)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)

            out_path = SCREENSHOTS_DIR / f"{name}.png"
            driver.save_screenshot(str(out_path))
            print(f"  Saved: {out_path}")
            screenshot_paths.append(out_path)

    driver.quit()
    return screenshot_paths


# ── Step 3: Generate TTS audio via OpenAI ────────────────────────────────
def generate_narration():
    """Generate TTS audio for each segment using OpenAI API."""
    from openai import OpenAI

    print("\n🎙️  Generating narration audio...")

    client = OpenAI()
    audio_paths = []

    for name, _url, narration in SEGMENTS:
        out_path = AUDIO_DIR / f"{name}.mp3"

        if out_path.exists():
            print(f"  Skipping (cached): {out_path}")
            audio_paths.append(out_path)
            continue

        print(f"  Generating TTS for '{name}' ...")
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",
            input=narration,
        )
        response.stream_to_file(str(out_path))
        print(f"  Saved: {out_path}")
        audio_paths.append(out_path)

    return audio_paths


# ── Step 4: Assemble video with moviepy ──────────────────────────────────
def assemble_video(screenshot_paths, audio_paths):
    """Combine screenshots and audio into a final MP4 video."""
    from moviepy import (
        ImageClip,
        AudioFileClip,
        concatenate_videoclips,
    )

    print("\n🎬 Assembling video...")

    clips = []
    for i, (img_path, audio_path) in enumerate(zip(screenshot_paths, audio_paths)):
        audio_clip = AudioFileClip(str(audio_path))
        duration = audio_clip.duration + 1.0  # Add 1s padding after narration

        img_clip = (
            ImageClip(str(img_path))
            .resized((1920, 1080))
            .with_duration(duration)
            .with_audio(audio_clip)
        )

        # Add crossfade except for first clip
        if i > 0:
            img_clip = img_clip.with_effects([])  # placeholder for crossfade

        clips.append(img_clip)
        print(f"  Segment '{img_path.stem}': {duration:.1f}s")

    # Concatenate with crossfade transitions
    final = concatenate_videoclips(clips, method="compose", padding=-0.5)

    total_duration = final.duration
    print(f"\n  Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")

    print(f"  Writing to {OUTPUT_FILE} ...")
    final.write_videofile(
        str(OUTPUT_FILE),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k",
        preset="medium",
        threads=4,
        logger="bar",
    )

    # Clean up
    for clip in clips:
        clip.close()
    final.close()

    print(f"\n✅ Video saved to: {OUTPUT_FILE}")
    print(f"   File size: {OUTPUT_FILE.stat().st_size / 1024 / 1024:.1f} MB")


# ── Main ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  CustomerChurn AI — YouTube Walkthrough Video Generator")
    print("=" * 60)

    screenshot_paths = capture_screenshots()
    audio_paths = generate_narration()
    assemble_video(screenshot_paths, audio_paths)
