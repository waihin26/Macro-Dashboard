import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components
from sections import employment

# ── Page-wide setup ─────────────────────────────────────
st.set_page_config(page_title="Dual Mandate Monitor", layout="wide")

css = Path("assets/theme.css").read_text()
components.html(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=Mulish:wght@400;600;700&display=swap" rel="stylesheet">
    <style>{css}</style>
    """,
    height=0, scrolling=False
)

st.markdown("""
<h1 style="text-align:center; margin:0">FED</h1>
<div style="height:4px;background:linear-gradient(90deg,#ff572f 0%,#ffed6f 100%);
            margin:0.8rem 0 4rem 0;"></div>
""", unsafe_allow_html=True)

st.markdown("# The Dual Mandate Monitor")

# ── Tabs & Sections ─────────────────────────────────────
from sections import employment, inflation  # noqa: E402

employment_tab, inflation_tab = st.tabs(["Employment", "Inflation"])

with employment_tab:
    employment.render()        # <── one-liner!

with inflation_tab:
    inflation.render()         # <── stub for future work
