# file_cleansing.py

import streamlit as st
import pandas as pd
from CustClean import run_cust_clean
from SalesFlag import show_sales_flag
from ProductFlag import show_product_flag

# Set page title and wide layout
st.set_page_config(page_title="FP&A Customer Sales Churn", layout="wide")

# -- Custom CSS --------------------------------------------------------------
# Only the selectors that actually work are injected here
st.markdown("""
<style>
  /* 0) Global: force every element—main, sidebar, widgets—to use sans-serif */
  html, body, * {
    font-family: sans-serif !important;
  }
  /* 1) Main title contrast */
  h1 {
    color: #FAF3E0 !important;
  }
  /* 2) File-uploader instructions ("Drag and drop file here" & "Limit 200MB per file • CSV") */
  [data-testid="stFileUploaderDropzoneInstructions"] span,
  [data-testid="stFileUploaderDropzoneInstructions"] small {
    color: #FAF3E0 !important;
  }
  /* 3) Number-input labels (the "Yellow Flag..." and "Red Flag..." text) */
  [data-baseweb="number-input"] label {
    color: #FAF3E0 !important;
  }
  /* 4) Number-input values inside the inputs (the actual 30 and 60) */
  input[data-testid="stNumberInputField"] {
    color: #FAF3E0 !important;
  }
  /* 5) Download button text (normal state) */
  [data-testid="stDownloadButton"] button,
  [data-testid="stDownloadButton"] p {
    color: #FAF3E0 !important;
  }
  /* 6) Style only the “Customers Not Found” heading */
  .cust-not-found {
    color: #FAF3E0 !important;
    font-family: Arial, sans-serif !important;
    margin-top: 1rem;
  }
  /* 7) Custom main page title override */
  .main-title {
    color: #FAF3E0 !important;
    font-family: Arial, sans-serif !important;
    margin-bottom: 1rem;
  }
  /* 8) Valid Customers header */
  .valid-customers {
    color: #FAF3E0 !important;
    font-family: Arial, sans-serif !important;
    margin-top: 1rem;
  }
  /* 9) Sales Inactivity section header */
  .sales-flag {
    color: #FAF3E0 !important;
    font-family: Arial, sans-serif !important;
    margin-top: 1rem;
  }
</style>
""", unsafe_allow_html=True)

# -- Logo --------------------------------------------------------------
# Display the company logo at the top of the page
st.image("Laborie.png", width=200)

# -- Sidebar Controls --------------------------------------------------------
st.sidebar.header("🔧 Controls")

# File uploader in sidebar
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

# Sidebar inputs for churn thresholds
yellow_flag = st.sidebar.number_input(
    "Yellow Flag (days ≥ 30)",
    min_value=30, value=30, step=1
)
red_flag = st.sidebar.number_input(
    "Red Flag (days ≥ 60)",
    min_value=60, value=60, step=1
)

# No-op callback for download buttons
def noop():
    pass

# Store thresholds in session state when button clicked
if st.sidebar.button("Apply Thresholds"):
    st.session_state.apply = True
    st.session_state.yellow = yellow_flag
    st.session_state.red = red_flag

# -- Main App ---------------------------------------------------------------

# Main page title (via markdown so we can style with .main-title)
st.markdown(
    '<h1 class="main-title">✅ FP&A Customer Sales Churn</h1>',
    unsafe_allow_html=True
)

if uploaded_file:
    # Read uploaded CSV
    df_orig = pd.read_csv(uploaded_file, low_memory=False)

    # Run cleaning and matching routines (now returns 4 DataFrames)
    df_full, df_not_found, df_valid, df_valid_cust_prod = run_cust_clean(df_orig)

    # Section: show invalid customer rows
    st.markdown(
        '<h3 class="cust-not-found">😟 Customers Not Found</h3>',
        unsafe_allow_html=True
    )
    st.download_button(
        label="Download CustIdentifierNotFound.csv",
        data=df_not_found.to_csv(index=False).encode("utf-8"),
        file_name="CustIdentifierNotFound.csv",
        mime="text/csv",
        on_click=noop
    )
    st.markdown("---")

    # Section: show valid customer rows
    st.markdown(
        '<h2 class="valid-customers">✅ Valid Customers</h2>',
        unsafe_allow_html=True
    )
    st.download_button(
        label="Download ValidCustomers.csv",
        data=df_valid.to_csv(index=False).encode("utf-8"),
        file_name="ValidCustomers.csv",
        mime="text/csv",
        on_click=noop
    )
    st.markdown("---")

    # Top-level tabs for two analyses
    tab_sales, tab_product = st.tabs(
        ["🛒 Phase 1:  Sales Inactivity", "📦 Phase 2:  Product Inactivity"]
    )

    # Sales inactivity analysis
    with tab_sales:
        show_sales_flag(df_valid, noop)

    # Product inactivity analysis
    with tab_product:
        # pass along the new df_valid_cust_prod for any product-flag logic
        show_product_flag(df_full, df_valid, df_valid_cust_prod, noop)
