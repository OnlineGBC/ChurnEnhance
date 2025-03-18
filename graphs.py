import matplotlib.pyplot as plt
import streamlit as st

def draw_data_graph():
    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))

    # Data setup – replace with your actual data as needed
    years = [2019, 2020, 2021, 2022, 2023]
    revenues = [37.27, 33.03, 38.73, 42.84, 45.83]
    gross_income = [22.67, 19.53, 23.22, 24.81, 27.38]

    # Compute profit margins
    profit_margins = [(gi / rev) * 100 for gi, rev in zip(gross_income, revenues)]

    # Plot Sales/Revenue on left y-axis
    color_revenue = 'tab:blue'
    ax.set_xlabel('Year')
    ax.set_ylabel('Sales/Revenue (Billion USD)', color=color_revenue)
    ax.plot(years, revenues, marker='o', linestyle='-', color=color_revenue, label='Sales/Revenue')
    ax.tick_params(axis='y', labelcolor=color_revenue)

    # Create a twin axis for Profit Margin
    ax2 = ax.twinx()
    color_margin = 'tab:red'
    ax2.set_ylabel('Profit Margin (%)', color=color_margin)
    ax2.plot(years, profit_margins, marker='s', linestyle='--', color=color_margin, label='Profit Margin')
    ax2.tick_params(axis='y', labelcolor=color_margin)

    plt.title('Sales/Revenue and Profit Margin Trends (2019-2023)')
    fig.tight_layout()
    plt.grid(True)

    st.pyplot(fig)
