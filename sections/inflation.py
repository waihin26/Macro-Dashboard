import streamlit as st
from sections.overview import render_cpi_overview, render_ppi_overview, render_alt_core_and_expectations, render_year_ahead_expectations
from sections.cpi import render_cpi_core_ex, render_cpi_housing, render_cpi_services


def render():
    overview_tab, cpi_tab = st.tabs(
        ["Overview", "CPI"]
    )

    with overview_tab:
        render_cpi_overview()
        render_ppi_overview()
        render_alt_core_and_expectations()
        render_year_ahead_expectations()

    with cpi_tab:
        render_cpi_core_ex()  
        render_cpi_housing()
        render_cpi_services()
