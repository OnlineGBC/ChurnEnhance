# file_cleansing.py

"""
Main entry point for the FP&A Customer Sales Churn Streamlit web app.

This script performs the following tasks:
1. Sets up the Streamlit web interface including layout and styling.
2. Provides sidebar controls to upload a CSV file and configure churn thresholds.
3. Calls the CustClean.py module (function: run_cust_clean) to preprocess uploaded customer data.
4. Displays results for customers whose data was not found, and valid customers.
5. Calls SalesFlag.py (function: show_sales_flag) to analyze sales inactivity.
6. Calls ProductFlag.py (function: show_product_flag) to analyze product inactivity.

Modules imported:
- streamlit (for the web UI)
- pandas (for CSV file handling and data manipulation)
- CustClean.py (data preprocessing and customer validation)
- SalesFlag.py (analysis of customer sales inactivity)
- ProductFlag.py (analysis of customer product inactivity)

This script does not get called by any other script; it serves as the entry point.
"""

# Import required libraries and custom modules
import streamlit as st
import pandas as pd
from CustClean import run_cust_clean
from SalesFlag import show_sales_flag
from ProductFlag import show_product_flag

# Set Streamlit page title and layout
st.set_page_config(page_title="FP&A Customer Sales Churn", layout="wide")

# -- Custom CSS --------------------------------------------------------------
# Custom CSS to style the Streamlit web interface
st.markdown("""
<style>
  /* 0) Global: Force every element to use sans-serif font */
  html, body, * {
    font-family: sans-serif !important;
  }
  /* 1) Main title styling for contrast */
  h1 {
    color: #FAF3E0 !important;
  }
  /* 2) File-uploader instruction text styling */
  [data-testid="stFileUploaderDropzoneInstructions"] span,
  [data-testid="stFileUploaderDropzoneInstructions"] small {
    color: #FAF3E0 !important;
  }
  /* 3) Number-input labels styling */
  [data-baseweb="number-input"] label {
    color: #FAF3E0 !important;
  }
  /* 4) Number-input values styling */
  input[data-testid="stNumberInputField"] {
    color: #FAF3E0 !important;
  }
  /* 5) Download button text styling */
  [data-testid="stDownloadButton"] button,
  [data-testid="stDownloadButton"] p {
    color: #FAF3E0 !important;
  }
  /* 6) "Customers Not Found" header styling */
  .cust-not-found {
    color: #FAF3E0 !important;
    font-family: Arial, sans-serif !important;
    margin-top: 1rem;
  }
  /* 7) Custom main page title styling override */
  .main-title {
    color: #FAF3E0 !important;
    font-family: Arial, sans-serif !important;
    margin-bottom: 1rem;
  }
  /* 8) Valid Customers header styling */
  .valid-customers {
    color: #FAF3E0 !important;
    font-family: Arial, sans-serif !important;
    margin-top: 1rem;
  }
  /* 9) Sales Inactivity section header styling */
  .sales-flag {
    color: #FAF3E0 !important;
    font-family: Arial, sans-serif !important;
    margin-top: 1rem;
  }
</style>
""", unsafe_allow_html=True)

# -- Logo --------------------------------------------------------------
# Display the company logo at the top of the web page
st.image("Laborie.png", width=200)

# -- Sidebar Controls --------------------------------------------------------
# Sidebar header
st.sidebar.header("🔧 Controls")

# CSV file uploader in the sidebar
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

# Number inputs for setting churn thresholds (Yellow and Red flags)
yellow_flag = st.sidebar.number_input(
    "Yellow Flag (days ≥ 30)",
    min_value=30, value=30, step=1
)
red_flag = st.sidebar.number_input(
    "Red Flag (days ≥ 60)",
    min_value=60, value=60, step=1
)

# Define a no-operation (no-op) function for the download button callbacks
def noop():
    pass

# Save churn threshold values in session state when "Apply Thresholds" is clicked
if st.sidebar.button("Apply Thresholds"):
    st.session_state.apply = True
    st.session_state.yellow = yellow_flag
    st.session_state.red = red_flag

# -- Main App ---------------------------------------------------------------

# Main page title (styled via custom CSS class 'main-title')
st.markdown(
    '<h1 class="main-title">✅ FP&A Customer Sales Churn</h1>',
    unsafe_allow_html=True
)

# If a CSV file has been uploaded, proceed with data processing
if uploaded_file:
    # Read the uploaded CSV file into a pandas DataFrame
    df_orig = pd.read_csv(uploaded_file, low_memory=False)

    # Run customer data cleaning and matching routines
    # Returns four DataFrames:
    # 1. df_full (full data with preprocessing)
    # 2. df_not_found (customers whose information could not be matched)
    # 3. df_valid (customers whose information is valid and matched)
    # 4. df_valid_cust_prod (valid customer-product combinations for further analyses)
    df_full, df_not_found, df_valid, df_valid_cust_prod = run_cust_clean(df_orig)

    # Section: Display and allow downloading customers not found
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

    # Section: Display and allow downloading valid customers
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

    # Create top-level tabs for two types of inactivity analyses
    tab_sales, tab_product = st.tabs(
        ["🛒 Phase 1:  Sales Inactivity", "📦 Phase 2:  Product Inactivity"]
    )

    # Tab 1: Sales inactivity analysis
    # Calls the show_sales_flag function from SalesFlag.py module
    with tab_sales:
        show_sales_flag(df_valid, noop)

    # Tab 2: Product inactivity analysis
    # Calls the show_product_flag function from ProductFlag.py module
    with tab_product:
        show_product_flag(df_full, df_valid, df_valid_cust_prod, noop)
