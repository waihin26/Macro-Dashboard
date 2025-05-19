import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from data_fetcher.fred import _fred_series 
import numpy as np


FIG_H   = 390
ANCHOR  = date(2020, 1, 1)       # baseline for cumulative Δ
RECESS  = "USREC"                # recession flag

FIG_H   = 390
RECESS  = "USREC"

SERIES_CPI = {
    "Headline CPI" : "CPIAUCSL",   # All-items CPI (SA, 1982-84=100)
    "Core CPI"     : "CPILFESL",   # CPI ex-Food & Energy (SA)
}

       
SERIES_PPI = {
    "Headline PPI": "PPIACO",   # All Commodities PPI (not seasonally adjusted)                             
    "Core PPI"    : "PPICOR",   # Final Demand: Less Foods & Energy (not seasonally adjusted)          
}

SERIES_ALT_CORE = {
        "Trimmed Mean PCE"     : "PCETRIM12M159SFRBDAL",       
        "16% Trimmed-Mean CPI" : "TRMMEANCPIM158SFRBCLE",     
        "Median CPI"           : "MEDCPIM158SFRBCLE",          
}

SERIES_INFL_EXP = {
    "5Y Breakeven" : "T5YIE",   # 5-Year Breakeven Inflation Rate
    "5Y5Y Forwards": "T5YIFR",  # 5-Year, 5-Year Forward Inflation Expectation
}

SERIES_PROB_YR_AHEAD = {
    "Prob > 2.5% Next Yr" : "STLPPM",   
}

SERIES_UMICH_YR_AHEAD = {
    "UMich 1-Yr Exp"      : "MICH",     
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


@st.cache_data(show_spinner=False)
def _panel_ppi() -> pd.DataFrame:
    """
    Build a DataFrame with:
      • YoY % change in headline/core PPI
      • 3-month rolling annualised % change
      • NBER recession flag
    """
    df_idx = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES_PPI.items()],
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


@st.cache_data(show_spinner=False)
def _panel_alt_core() -> pd.DataFrame:
    df = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES_ALT_CORE.items()],
        axis=1
    ).dropna()
    rec = _fred_series(RECESS, name="USREC")
    return df.join(rec, how="inner").dropna()


@st.cache_data(show_spinner=False)
def _panel_infl_exp() -> pd.DataFrame:
    return pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES_INFL_EXP.items()],
        axis=1
    ).dropna()

@st.cache_data(show_spinner=False)
def _panel_prob_next_year() -> pd.DataFrame:
    """Return probability series converted to percent (0–100)."""
    df = _fred_series(SERIES_PROB_YR_AHEAD["Prob > 2.5% Next Yr"],
                      name="Prob > 2.5% Next Yr")
    return (df * 100.0).dropna()              # decimal → percent


@st.cache_data(show_spinner=False)
def _panel_umich_next_year() -> pd.DataFrame:
    """Return UMich median 1-year inflation expectation (%)."""
    return _fred_series(SERIES_UMICH_YR_AHEAD["UMich 1-Yr Exp"],
                        name="UMich 1-Yr Exp").dropna()


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




@st.cache_data(show_spinner=False)
def _panel_pce() -> pd.DataFrame:
    """
    Same construction as _panel_cpi(), but for PCE:
        • YoY % change
        • 3-month rolling annualised % change
        • US recession indicator
    """
    df_idx = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES_PCE.items()],
        axis=1
    ).dropna()

    yoy = df_idx.pct_change(12) * 100
    yoy.columns = [f"{c} YoY" for c in df_idx.columns]

    ann3 = (df_idx / df_idx.shift(3)) ** 4 - 1
    ann3 = ann3 * 100
    ann3.columns = [f"{c} 3M" for c in df_idx.columns]

    rec = _fred_series(RECESS, name="USREC")

    return pd.concat([yoy, ann3, rec], axis=1).dropna()


def render_ppi_overview() -> None:
    """Render PPI YoY trend and 3-month annualised change (side-by-side)."""
    df      = _panel_ppi()
    recess  = _recession_periods(df["USREC"])

    df_yoy = df[["Core PPI YoY", "Headline PPI YoY"]]
    df_3m  = df[["Core PPI 3M",  "Headline PPI 3M"]]

    col1, col2 = st.columns(2, gap="large")

    # 1) PPI YoY trend ----------------------------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "US PPI Trend&nbsp;–&nbsp;YoY</div>",
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        fig.add_scatter(
            x=df_yoy.index, y=df_yoy["Core PPI YoY"],
            mode="lines", name="Core",
            line=dict(width=3, color="#18A5C2")
        )
        fig.add_scatter(
            x=df_yoy.index, y=df_yoy["Headline PPI YoY"],
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
            "US PPI Short&nbsp;Term&nbsp;Change</div>",
            unsafe_allow_html=True,
        )

        # show last 24 months
        start_zoom = df_3m.index.max() - pd.DateOffset(months=24)

        fig = go.Figure()
        fig.add_scatter(
            x=df_3m.index, y=df_3m["Core PPI 3M"],
            mode="lines", name="Core",
            line=dict(width=3, color="#18A5C2")
        )
        fig.add_scatter(
            x=df_3m.index, y=df_3m["Headline PPI 3M"],
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
                title="3-Month Rolling Annualised PPI",
                tickformat=".1f", ticksuffix="%",
                range=[0, 7]
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)



def render_alt_core_and_expectations() -> None:
    """
    (L) Alternative core CPI/PCE measures (YoY)
    (R) Market inflation expectations (5Y breakeven, 5Y5Y forward)
    """
    df_core = _panel_alt_core()
    df_exp  = _panel_infl_exp()

    # --- layout ---------------------------------------------------------
    col1, col2 = st.columns(2, gap="large")

    # -------- Alternative Core Measures -----------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "Alternative Core Measures&nbsp;–&nbsp;YoY</div>",
            unsafe_allow_html=True,
        )

        colours = ["#86C7DE", "#0794C6", "#F4B400"]  # lt-blue, blue, orange
        fig = go.Figure()
        for (lbl, col) in zip(SERIES_ALT_CORE.keys(), colours):
            fig.add_scatter(
                x=df_core.index, y=df_core[lbl],
                mode="lines", name=lbl,
                line=dict(width=3, color=col)
            )

        _add_fed_ait_band(fig)
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#000")
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25, r=10),
            yaxis=dict(title="YoY", tickformat=".1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

    # -------- (2) Market Inflation Expectations -------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "Market Inflation Expectations</div>",
            unsafe_allow_html=True,
        )

        # focus on the past two years for clarity
        start_zoom = df_exp.index.max() - pd.DateOffset(months=24)

        colours = ["#18A5C2", "#0D1F2D"]  # teal-ish & dark navy
        fig = go.Figure()
        for (lbl, col) in zip(SERIES_INFL_EXP.keys(), colours):
            fig.add_scatter(
                x=df_exp.index, y=df_exp[lbl],
                mode="lines", name=lbl,
                line=dict(width=3, color=col)
            )

        _add_fed_ait_band(fig)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25, r=10),
            xaxis=dict(range=[start_zoom, df_exp.index.max()]),
            yaxis=dict(
                title="Rate %", tickformat=".2f", ticksuffix="%",
                range=[1.9, 2.7]        # matches your screenshot
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

def render_year_ahead_expectations() -> None:
    """
    (L) Probability inflation > 2.5 % in next 12 months (STLPPM)
    (R) University of Michigan 1-year inflation expectations (MICH)
    """
    df_prob  = _panel_prob_next_year()
    df_umich = _panel_umich_next_year()

    col1, col2 = st.columns(2, gap="large")

    # ---------------- (1) probability panel ------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "Year Ahead Expectations</div>",
            unsafe_allow_html=True,
        )

        fig = go.Figure()
        fig.add_scatter(
            x=df_prob.index, y=df_prob["Prob > 2.5% Next Yr"],
            mode="lines", name="",  # single series → no legend
            line=dict(width=3, color="#86C7DE")
        )
        fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#000")
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25, r=10),
            yaxis=dict(
                title="Chances of Inflation Exceeding 2.5% in a Year",
                tickformat=".0f", ticksuffix="%", range=[0, 100]
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- (2) UMich survey panel -----------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "Year Ahead Expectations (UMICH Survey) </div>",
            unsafe_allow_html=True,
        )

        # zoom to ≈ last 24 months
        start_zoom = df_umich.index.max() - pd.DateOffset(months=24)

        fig = go.Figure()
        fig.add_scatter(
            x=df_umich.index, y=df_umich["UMich 1-Yr Exp"],
            mode="lines", name="",
            line=dict(width=3, color="#86C7DE")
        )
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25, r=10),
            xaxis=dict(range=[start_zoom, df_umich.index.max()]),
            yaxis=dict(
                title="Expected Rate", tickformat=".1f", ticksuffix="%",
                range=[2.5, 5.5]   # matches screenshot
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)