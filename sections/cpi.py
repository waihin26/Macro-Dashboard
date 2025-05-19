# sections/cpi.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_fetcher.fred import _fred_series          

FIG_H   = 390
RECESS  = "USREC"

# CPI components (seasonally-adjusted indexes, 1982-84 = 100)
SERIES_CPI_COMP = {
    "Core CPI"   : "CPILFESL",   # CPI ex-Food & Energy
    "Food CPI"   : "CPIUFDSL",   # Food
    "Energy CPI" : "CPIENGSL",   # Energy
}

SERIES_CPI_HOUSING = {
    "Rent of Primary Residence" : "CUSR0000SEHA",   # SA
    "OER"                       : "CUSR0000SEHC",   # Owners’ Equivalent Rent
}

@st.cache_data(show_spinner=False)
def _panel_housing() -> pd.DataFrame:
    """
    Build YoY % and 3-month annualised % changes for Rent & OER,
    plus US recession flag.
    """
    idx = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES_CPI_HOUSING.items()],
        axis=1
    ).dropna()

    yoy  = idx.pct_change(12) * 100
    yoy.columns = [f"{c} YoY" for c in idx.columns]

    ann3 = (idx / idx.shift(3)) ** 4 - 1
    ann3 = ann3 * 100
    ann3.columns = [f"{c} 3M" for c in idx.columns]

    rec = _fred_series(RECESS, name="USREC")

    return pd.concat([yoy, ann3, rec], axis=1).dropna()


# Fed’s average-inflation-target band
AIT_LOW, AIT_HIGH = 2.0, 2.5


@st.cache_data(show_spinner=False)
def _panel_components() -> pd.DataFrame:
    """
    Returns a DataFrame with:
        • YoY % change for core, food, energy
        • 3-month rolling annualised % change for the same
        • NBER recession flag
    """
    idx = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES_CPI_COMP.items()],
        axis=1
    ).dropna()

    yoy = idx.pct_change(12) * 100
    yoy.columns = [f"{c} YoY" for c in idx.columns]

    ann3 = (idx / idx.shift(3)) ** 4 - 1
    ann3 = ann3 * 100
    ann3.columns = [f"{c} 3M" for c in idx.columns]

    rec = _fred_series(RECESS, name="USREC")

    return pd.concat([yoy, ann3, rec], axis=1).dropna()


def _recession_periods(rec: pd.Series):
    rec = rec.astype(bool)
    s = rec & ~rec.shift(1, fill_value=False)
    e = rec & ~rec.shift(-1, fill_value=False)
    return list(zip(s[s].index, e[e].index))


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


def render_cpi_core_ex() -> None:
    """
    (L) YoY – Core CPI vs Food & Energy
    (R) 3-month rolling annualised – same three series
    """
    df      = _panel_components()
    recess  = _recession_periods(df["USREC"])

    df_yoy = df[[f"{k} YoY" for k in ["Core CPI", "Food CPI", "Energy CPI"]]]
    df_3m  = df[[f"{k} 3M"  for k in ["Core CPI", "Food CPI", "Energy CPI"]]]

    col1, col2 = st.columns(2, gap="large")

    # ---------- (1) YoY panel -------------------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "CPI Core vs Ex Component</div>",
            unsafe_allow_html=True,
        )

        colours = ["#86C7DE", "#0794C6", "#F4B400"]   # core, food, energy
        fig = go.Figure()
        for (series, col) in zip(df_yoy.columns, colours):
            fig.add_scatter(
                x=df_yoy.index, y=df_yoy[series],
                mode="lines", name=series.split()[0],  # Core / Food / Energy
                line=dict(width=3, color=col)
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

    # ----------  3-month annualised panel ----------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "Core and Ex&nbsp;Short&nbsp;term</div>",
            unsafe_allow_html=True,
        )

        start_zoom = df_3m.index.max() - pd.DateOffset(months=36)

        fig = go.Figure()
        for (series, col) in zip(df_3m.columns, colours):
            fig.add_scatter(
                x=df_3m.index, y=df_3m[series],
                mode="lines", name=series.split()[0],
                line=dict(width=3, color=col)
            )

        _add_fed_ait_band(fig)
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25, r=10),
            xaxis=dict(range=[start_zoom, df_3m.index.max()]),
            yaxis=dict(
                title="3-Month Rolling Annualised CPI",
                tickformat=".1f", ticksuffix="%",
                range=[-40, 60]
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)


def render_cpi_housing() -> None:
    """
    (L) YoY – Rent of Primary Residence & OER
    (R) 3-month rolling annualised – same two series
    """
    df      = _panel_housing()
    recess  = _recession_periods(df["USREC"])

    df_yoy = df[[f"{k} YoY" for k in SERIES_CPI_HOUSING.keys()]]
    df_3m  = df[[f"{k} 3M"  for k in SERIES_CPI_HOUSING.keys()]]

    col1, col2 = st.columns(2, gap="large")

    colours = ["#18A5C2", "#0D1F2D"]   # teal for Rent, navy for OER

    # -------- (1) YoY panel ---------------------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "Housing Components</div>",
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        for series, col in zip(df_yoy.columns, colours):
            fig.add_scatter(
                x=df_yoy.index, y=df_yoy[series],
                mode="lines", name=series.replace(" YoY", ""),
                line=dict(width=3, color=col)
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

    # -------- (2) 3-month annualised panel ------------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "Short Term Housing</div>",
            unsafe_allow_html=True,
        )
        start_zoom = df_3m.index.max() - pd.DateOffset(months=48)

        fig = go.Figure()
        for series, col in zip(df_3m.columns, colours):
            fig.add_scatter(
                x=df_3m.index, y=df_3m[series],
                mode="lines", name=series.replace(" 3M", ""),
                line=dict(width=3, color=col)
            )
        _add_fed_ait_band(fig)
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25, r=10),
            xaxis=dict(range=[start_zoom, df_3m.index.max()]),
            yaxis=dict(
                title="3-Month Rolling Annualised CPI",
                tickformat=".1f", ticksuffix="%"
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)