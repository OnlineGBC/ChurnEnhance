# ui_graphics.py
import streamlit as st
import matplotlib.pyplot as plt

# Custom CSS setup (explicitly from your original app.py)
def setup_custom_css():
    st.markdown(
        """
        <style>
        * { font-size: 16px !important; }
        .app-title {
            text-align: center;
            font-size: 64px;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        div[data-testid="stSidebar"] button[id^="delete_"] {
            background-color: transparent;
            color: red;
            border: none;
            font-size: 16px;
            padding: 0;
        }
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

# Blinking message function
def show_blinking_message(message, color="red"):
    st.markdown(
        f"<div style='font-size:64px; color:{color}; text-align:center; animation:blink 1.5s infinite;'>{message}</div>",
        unsafe_allow_html=True
    )

# explicitly add this to ui_graphics.py
import streamlit as st

def blinking_message(message, color="red"):
    blinking_placeholder = st.empty()
    blinking_placeholder.markdown(
        f"<div style='font-size:64px; color:{color}; text-align:center; animation:blink 1.5s infinite;'>"
        f"{message}</div>",
        unsafe_allow_html=True,
    )


# Display extracted text in a Streamlit text area
def display_extracted_text(text, file_name):
    st.text_area(f"Extracted Text: {file_name}", text, height=200)

# Display DataFrame in Streamlit
def display_dataframe(df, file_name):
    st.dataframe(df, use_container_width=True)

# Display images and their OCR-extracted text
def display_image_with_text(image, extracted_text, file_name):
    st.image(image, caption=f"Uploaded image ({file_name})", use_container_width=True)
    st.text_area(f"Extracted text from image ({file_name})", extracted_text, height=200)

# Explicitly copied from your provided graphs.py (unchanged):
import matplotlib.pyplot as plt
import streamlit as st

def draw_data_graph():
    fig, ax = plt.subplots(figsize=(10, 6))

    years = [2019, 2020, 2021, 2022, 2023]
    revenues = [37.27, 33.03, 38.73, 42.84, 45.83]
    gross_income = [22.67, 19.53, 23.22, 24.81, 27.38]
    profit_margins = [(gi / rev) * 100 for gi, rev in zip(gross_income, revenues)]

    color_revenue = 'tab:blue'
    ax = plt.gca()
    ax.set_xlabel('Year')
    ax.set_ylabel('Sales/Revenue (Billion USD)', color=color_revenue)
    ax.plot(years, revenues, marker='o', linestyle='-', color=color_revenue, label='Sales/Revenue')
    ax.tick_params(axis='y', labelcolor=color_revenue)

    ax2 = ax.twinx()
    color_margin = 'tab:red'
    ax2.set_ylabel('Profit Margin (%)', color=color_margin)
    ax2.plot(years, profit_margins, marker='s', linestyle='--', color=color_margin, label='Profit Margin')
    ax2.tick_params(axis='y', labelcolor=color_margin)

    plt.title('Sales/Revenue and Profit Margin Trends (2019-2023)')
    plt.grid(True)
    plt.tight_layout()

    st.pyplot(plt.gcf())
