import streamlit as st


def render():
    overview_tab, cpi_tab, pce_tab = st.tabs(
        ["Overview", "CPI", "PCE – SF FED"]
    )

    with overview_tab:
        st.info("Overview content goes here.")

    with cpi_tab:
        st.info("Overview content goes here.")         

    with pce_tab:
        st.info("PCE – SF FED content goes here.")
