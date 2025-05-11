import streamlit as st
from pathlib import Path
import datetime as dt
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px

from data_fetcher.fred import (
    get_employment_growth,
    get_unemployment_rate,
    _fred_series,   # for recession shading
)


# Page config & CSS 
st.set_page_config(page_title="Dual Mandate Monitor", layout="wide")

# load your existing theme.css + Mulish font
css = Path("assets/theme.css").read_text()
components.html(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=Mulish:wght@400;600;700&display=swap" rel="stylesheet">
    <style>{css}</style>
    """,
    height=0,
    scrolling=False,
)

# Header + gradient bar 
st.markdown(
    """
    <h1 style="text-align:center; margin:0">FED</h1>
    <div style="
        height:4px;
        background:linear-gradient(90deg,#ff572f 0%,#ffed6f 100%);
        margin:0.8rem 0 4rem 0;
    "></div>
    """,
    unsafe_allow_html=True,
)

# Main title 
st.markdown("# The Dual Mandate Monitor")

# Build “Employment” vs “Inflation” tabs
employment_tab, inflation_tab = st.tabs(["Employment", "Inflation"])

# ===== Employment branch =====
with employment_tab:
    gen, nfp, wages, alt = st.tabs(
        ["General", "NFP", "Wages", "Alternatives"]
    )

with gen:
    # getting data from backend servers
    df_emp = get_employment_growth()
    df_unr      = get_unemployment_rate()
    
    # Computes what share of all historical observations are below the latest value as percentage. (Percentile Rank)
    emp_rank_pct = (df_emp["Emp Growth"] < df_emp["Emp Growth"].iloc[-1]).mean() * 100
    unr_rank_pct = (df_unr["Unemployment Rate"] < df_unr["Unemployment Rate"].iloc[-1]).mean() * 100
    
    left, right = st.columns(2, gap="large")
    FIG_HEIGHT = 390
    TOP_GAP_PX = 18

    # Employment Growth 
    with left:
        st.markdown(
            f"""
            <span style='font-size:20px;font-weight:700;line-height:1.2'>
              Employment Growth<br>
              Ranking: {emp_rank_pct:.2f}%
            </span>
            """,
            unsafe_allow_html=True,
        )

        # blank gap between heading & chart
        st.markdown(f"<div style='height:{TOP_GAP_PX}px'></div>", unsafe_allow_html=True)

        fig_emp = go.Figure()
        fig_emp.add_trace(go.Scatter(
            x=df_emp.index, y=df_emp["Emp Growth"],
            name="All Employees, Total Nonfarm",
            line=dict(color="#049CA4", width=2)
        ))
        fig_emp.add_trace(go.Scatter(
            x=df_emp.index, y=df_emp["3M MA Emp Growth"],
            name="3-Month MA",
            line=dict(color="black", width=2)
        ))

        fig_emp.update_layout(
            height     = FIG_HEIGHT,
            yaxis_title="Change (Thousands of persons)",
            template   ="simple_white",
            font       =dict(size=12),
            margin     =dict(l=50, r=25, t=30, b=45),
            legend     =dict(
                orientation="h",
                yanchor="bottom", y=1.18,            # same for both charts
                xanchor="left",   x=0,
                font=dict(size=12)
            ),
        )
        st.plotly_chart(fig_emp, use_container_width=True)

    # Unemployment Rate 
    with right:
        st.markdown(
            f"""
            <span style='font-size:20px;font-weight:700;line-height:1.2'>
              Unemployment Rate<br>
              Ranking: {unr_rank_pct:.2f}%
            </span>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f"<div style='height:{TOP_GAP_PX}px'></div>", unsafe_allow_html=True)

        fig_unr = px.line(
            df_unr, labels={"index": "", "value": "% Percentage points"},
            height=FIG_HEIGHT, color_discrete_sequence=["#1B65C0"]
        )

        # dashed long-run average line
        avg = df_unr["Unemployment Rate"].mean()
        fig_unr.add_hline(
            y=avg, line_dash="dash",
            annotation_text=f"Long-run avg {avg:.2f}%",
            annotation_position="bottom right"
        )

        # optional recession shading
        rec = _fred_series("USREC", name="USREC")
        for s, e in zip(rec[rec["USREC"].diff()==1].index,
                        rec[rec["USREC"].diff()==-1].index):
            fig_unr.add_vrect(x0=s, x1=e, fillcolor="lightgrey",
                              opacity=0.30, line_width=0)

        fig_unr.update_layout(
            template ="simple_white",
            font     =dict(size=12),
            margin   =dict(l=50, r=25, t=30, b=45),
            legend   =dict(
                orientation="h",
                yanchor="bottom", y=1.18,
                xanchor="left",   x=0,
                font=dict(size=12)
            ),
        )
        st.plotly_chart(fig_unr, use_container_width=True)


# ===== Inflation branch =====
with inflation_tab:
    o, cpi, pce = st.tabs(
        ["General", "CPI", "PCE – SF FED"]
    )
    with o:

        l, r = st.columns(2, gap="large")
        with l:
            st.markdown("## Some Inflation Chart")
        with r:
            st.markdown("## Another Inflation Chart")
