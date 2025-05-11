# home.py
import datetime as dt
from pathlib import Path
import streamlit.components.v1 as components
import streamlit as st

# ── 1️⃣ Page config & CSS ────────────────────────────────────────
st.set_page_config(
    page_title="Dual Mandate Monitor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# load your existing theme.css + Mulish font
css = Path("assets/theme.css").read_text()
components.html(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=Mulish:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
    {css}
    </style>
    """,
    height=0,
    scrolling=False,
)

# ── 2️⃣ Header + gradient bar ────────────────────────────────────
st.markdown(
    """
    <h1 style="text-align:center; margin:0">FED</h1>
    <div style="
        height:4px;
        background:linear-gradient(90deg,#ff572f 0%,#ffed6f 100%);
        margin:1.6rem 0 4rem 0;
    "></div>
    """,
    unsafe_allow_html=True,
)

# ── 3️⃣ Main title ───────────────────────────────────────────────
st.markdown("# The Dual Mandate Monitor")

# ── 4️⃣ First‐level tabs ─────────────────────────────────────────
tab_emp, tab_inf = st.tabs(["Employment", "Inflation"])

# ===== Employment branch =====
with tab_emp:
    gen, nfp, wages, alt = st.tabs(
        ["General", "NFP", "Wages", "Alternatives"]
    )
    with gen:
        # ─ Two-column blank area ───────────────────────
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown("## Employment Growth")
            # <-- insert chart here -->
        with right:
            st.markdown("## Unemployment Rate")
            # <-- insert chart here -->

# ===== Inflation branch =====
with tab_inf:
    o, cpi, pce = st.tabs(
        ["General", "CPI", "PCE – SF FED"]
    )
    with o:

        l, r = st.columns(2, gap="large")
        with l:
            st.markdown("## Some Inflation Chart")
        with r:
            st.markdown("## Another Inflation Chart")
