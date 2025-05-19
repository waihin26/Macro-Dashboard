import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from data_fetcher.fred import _fred_series 

FIG_H   = 390
ANCHOR  = date(2020, 1, 1)       # baseline for cumulative Δ
RECESS  = "USREC"                # recession flag

FIG_H   = 390
RECESS  = "USREC"

SERIES_CPI = {
    "Headline CPI" : "CPIAUCSL",   # All-items CPI (SA, 1982-84=100)
    "Core CPI"     : "CPILFESL",   # CPI ex-Food & Energy (SA)
}

# Fed’s Average-Inflation-Target (AIT) band, expressed in %-pts
AIT_BAND_LOW  = 2.0
AIT_BAND_HIGH = 2.5

@st.cache_data(show_spinner=False)
def _panel_cpi() -> pd.DataFrame:
    """
    Returns a DataFrame containing:
        • YoY % change in headline / core CPI
        • 3-month rolling annualised % change in headline / core CPI
        • US recession indicator
    Columns are labelled:
        Headline CPI YoY,  Core CPI YoY,
        Headline CPI 3M,   Core CPI 3M,  USREC
    """
    # raw indices
    df_idx = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES_CPI.items()],
        axis=1
    ).dropna()

    # YoY %
    yoy = df_idx.pct_change(12) * 100
    yoy.columns = [f"{c} YoY" for c in df_idx.columns]

    # 3-month rolling annualised %
    ann3 = (df_idx / df_idx.shift(3)) ** 4 - 1
    ann3 = ann3 * 100
    ann3.columns = [f"{c} 3M" for c in df_idx.columns]

    rec = _fred_series(RECESS, name="USREC")

    return pd.concat([yoy, ann3, rec], axis=1).dropna()


def _recession_periods(rec: pd.Series):
    """Return list of (start, end) timestamps where rec == 1."""
    rec = rec.astype(bool)
    starts = rec & ~rec.shift(1, fill_value=False)
    ends   = rec & ~rec.shift(-1, fill_value=False)
    return list(zip(starts[starts].index, ends[ends].index))


def _add_recessions(fig: go.Figure, periods):
    for s, e in periods:
        fig.add_vrect(
            x0=s, x1=e, fillcolor="grey",
            opacity=0.25, line_width=0, layer="below"
        )

def _add_fed_ait_band(fig: go.Figure):
    """Grey horizontal band for the Fed’s 2-2.5 % average-inflation target."""
    fig.add_hrect(
        y0=AIT_BAND_LOW, y1=AIT_BAND_HIGH,
        fillcolor="#D9D9D9", opacity=0.4,
        line_width=0, layer="below"
    )
    fig.add_annotation(
        xref="paper", x=0.01, y=(AIT_BAND_LOW + AIT_BAND_HIGH) / 2,
        text="FED&nbsp;AIT", showarrow=False,
        font=dict(size=11, color="#444"), bgcolor="rgba(0,0,0,0)"
    )

def render_cpi_overview() -> None:
    """Render CPI YoY trend and 3-month annualised change side-by-side."""
    df      = _panel_cpi()
    recess  = _recession_periods(df["USREC"])

    # split out the two panels
    df_yoy = df[["Core CPI YoY", "Headline CPI YoY"]]
    df_3m  = df[["Core CPI 3M",  "Headline CPI 3M"]]

    # ----- layout --------------------------------------------------------
    col1, col2 = st.columns(2, gap="large")

    # 1) CPI YoY trend ----------------------------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "US CPI Trend&nbsp;–&nbsp;YoY</div>",
            unsafe_allow_html=True,
        )

        fig = go.Figure()
        fig.add_scatter(
            x=df_yoy.index, y=df_yoy["Core CPI YoY"],
            mode="lines", name="Core",
            line=dict(width=3, color="#18A5C2")
        )
        fig.add_scatter(
            x=df_yoy.index, y=df_yoy["Headline CPI YoY"],
            mode="lines", name="Headline",
            line=dict(width=3, color="#0D1F2D")
        )
        _add_fed_ait_band(fig)
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#000")
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            yaxis=dict(title="YoY", tickformat=".1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

    # 2) Short-term (3-month annualised) change --------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "US CPI Short&nbsp;Term&nbsp;Change</div>",
            unsafe_allow_html=True,
        )

        # Zoom to ~last 24 months for readability
        start_zoom = df_3m.index.max() - pd.DateOffset(months=24)

        fig = go.Figure()
        fig.add_scatter(
            x=df_3m.index, y=df_3m["Core CPI 3M"],
            mode="lines", name="Core",
            line=dict(width=3, color="#18A5C2")
        )
        fig.add_scatter(
            x=df_3m.index, y=df_3m["Headline CPI 3M"],
            mode="lines", name="Headline",
            line=dict(width=3, color="#0D1F2D")
        )
        _add_fed_ait_band(fig)
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=[start_zoom, df_3m.index.max()]),
            yaxis=dict(
                title="3-Month Rolling Annualised CPI",
                tickformat=".1f", ticksuffix="%", range=[0, 5]
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)