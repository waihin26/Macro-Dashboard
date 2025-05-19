import streamlit as st
from sections.overview import render_cpi_overview, render_ppi_overview, render_alt_core_and_expectations


def render():
    overview_tab, cpi_tab, pce_tab = st.tabs(
        ["Overview", "CPI", "PCE – SF FED"]
    )

    with overview_tab:
        render_cpi_overview()
        render_ppi_overview()
        render_alt_core_and_expectations()

    with cpi_tab:
        st.info("Overview content goes here.")         

    with pce_tab:
        st.info("PCE – SF FED content goes here.")
