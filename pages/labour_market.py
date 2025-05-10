import streamlit as st
import pandas as pd
import altair as alt
import datetime as dt
from data_fetcher.fred import (
    continued_claims,
    jolts_openings,
    nonfarm_payroll_growth,
    labour_demand,      
    labour_supply,  
    initial_jobless_claims,
    average_hourly_earnings
)

# Page configurations
st.set_page_config(page_title="Data Panel", page_icon="📈", layout="wide")
st.title("📈 Data Panel")


# choose the data series
SERIES_MAP = {
    "Continued Claims": continued_claims,
    "Job Openings (Total NF)": jolts_openings,
    "Nonfarm Payroll Growth": nonfarm_payroll_growth,
    "Labour Demand (Openings + Employment)": labour_demand,  
    "Labour Supply (Civilian Labour Force)": labour_supply,   
    "Initial Jobless Claims (Seasonally Adjusted)": initial_jobless_claims,
    "Average Hourly Earnings": average_hourly_earnings
}

option = st.sidebar.selectbox("Choose data you want to see", SERIES_MAP.keys())

# ────────────────────────────────────────────────────────────────────────────────
# date‑range picker (only matters for FRED series)
# ────────────────────────────────────────────────────────────────────────────────
col1, col2 = st.sidebar.columns(2)

start_date = col1.date_input(
    "Start",
    value=dt.date(1980, 1, 1),      
    min_value=dt.date(1980, 1, 1),  
    max_value=dt.date.today()       
)

end_date = col2.date_input(
    "End",
    value=dt.date.today(),          
    min_value=dt.date(1980, 1, 1),  
    max_value=dt.date.today()       
)

# moving average slider
ma_window = st.sidebar.slider("Moving average (months)", 1, 5, value=1, step=2)

# fetch & plot
df = SERIES_MAP[option](start_date, end_date)

# Apply moving average if the index is a datetime index
if isinstance(df.index, pd.DatetimeIndex) and ma_window > 1:
    df = df.rolling(ma_window).mean()

plot_df = df.reset_index().dropna()
plot_df.columns = ["Date"] + list(plot_df.columns[1:])

# chart to display data
chart = (
    alt.Chart(plot_df)
      .mark_line()
      .encode(
          x=alt.X("Date:T", axis=alt.Axis(format="%b %Y", labelAngle=-45, tickCount="month")),
          y=alt.Y(f"{plot_df.columns[1]}:Q", title=plot_df.columns[1]),
      )
      .properties(height=400)
)

st.altair_chart(chart, use_container_width=True)