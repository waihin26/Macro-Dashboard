# sections/pce.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
from data_fetcher.fred import _fred_series   # for US recession flags only

# ------------------------------------------------------------------------
FIG_H  = 390
RECESS = "USREC"

# San Francisco Fed CSVs
URL_YOY  = "https://www.frbsf.org/wp-content/uploads/cyclical_acyclical_data_chart_1.csv"
URL_MOM  = "https://www.frbsf.org/wp-content/uploads/cyclical_acyclical_data_chart_2_monthly.csv"

# Fed AIT band
AIT_LOW, AIT_HIGH = 2.0, 2.5
# ------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def _load_cyclical_acyclical() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      * YoY DF  — columns: Cyclical, Acyclical  (pct)
      * MoM DF — columns: Cyclical, Acyclical  (MoM annualised pct)
    Index for both is datetime (period end of month).
    """
    yoy = pd.read_csv(URL_YOY, parse_dates=["DATE"], index_col="DATE")
    yoy = yoy.rename(columns=lambda c: c.strip().title())  # tidy -> Cyclical / Acyclical

    mom = pd.read_csv(URL_MOM, parse_dates=["DATE"], index_col="DATE")
    mom = mom.rename(columns=lambda c: c.strip().title())

    return yoy, mom


def _recession_periods(rec: pd.Series):
    rec = rec.astype(bool)
    start = rec & ~rec.shift(1, fill_value=False)
    end   = rec & ~rec.shift(-1, fill_value=False)
    return list(zip(start[start].index, end[end].index))


def _add_recessions(fig: go.Figure, periods):
    for s, e in periods:
        fig.add_vrect(
            x0=s, x1=e, fillcolor="grey",
            opacity=0.25, line_width=0, layer="below"
        )


def _add_fed_ait_band(fig: go.Figure):
    fig.add_hrect(
        y0=AIT_LOW, y1=AIT_HIGH,
        fillcolor="#D9D9D9", opacity=0.4,
        line_width=0, layer="below"
    )
    fig.add_annotation(
        xref="paper", x=0.01, y=(AIT_LOW + AIT_HIGH) / 2,
        text="FED&nbsp;AIT", showarrow=False,
        font=dict(size=11, color="#444"), bgcolor="rgba(0,0,0,0)"
    )


# ========================== main render =================================

def render_pce_cyclical() -> None:
    """(L) YoY Cyclical vs Acyclical; (R) MoM-annualised stacked bars."""
    df_yoy, df_mom = _load_cyclical_acyclical()
    rec = _fred_series(RECESS, name="USREC").squeeze()
    recess = _recession_periods(rec)

    col1, col2 = st.columns(2, gap="large")

    colours = {"Cyclical": "#18A5C2", "Acyclical": "#0D1F2D"}

    # ----------- (1) YoY line panel -------------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:25px;'>"
            "Core&nbsp;PCE – Cyclical&nbsp;&amp;&nbsp;Acyclical</div>",
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        for col in ["Cyclical", "Acyclical"]:
            fig.add_scatter(
                x=df_yoy.index, y=df_yoy[col],
                mode="lines", name=col,
                line=dict(width=3, color=colours[col])
            )
        _add_fed_ait_band(fig)
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#000")
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25, r=10),
            yaxis=dict(title="YoY", tickformat=".1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ----------- (2) MoM annualised stacked bars ------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:25px;'>"
            "Core PCE – Cyclical&nbsp;&amp;&nbsp;Acyclical</div>",
            unsafe_allow_html=True,
        )
        # focus on the past 48 months for readability
        start_zoom = df_mom.index.max() - pd.DateOffset(months=48)

        fig = go.Figure()
        # bottom stack: Acyclical
        fig.add_bar(
            x=df_mom.index, y=df_mom["Acyclical"],
            name="Acyclical", marker_color=colours["Acyclical"]
        )
        # top stack: Cyclical
        fig.add_bar(
            x=df_mom.index, y=df_mom["Cyclical"],
            name="Cyclical", marker_color=colours["Cyclical"]
        )

        _add_fed_ait_band(fig)
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#000")
        fig.update_layout(
            barmode="stack", height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25, r=10),
            xaxis=dict(range=[start_zoom, df_mom.index.max()]),
            yaxis=dict(
                title="MoM Annualized",
                tickformat=".1f", ticksuffix="%"
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)
