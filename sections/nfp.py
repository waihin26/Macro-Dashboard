# sections/nfp.py  – minimal, no widgets
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from data_fetcher.fred import _fred_series

FIG_H   = 390
ANCHOR  = date(2020, 1, 1)       # baseline for cumulative Δ
RECESS  = "USREC"                # recession flag

SERIES = {
    "Total Private"            : "USPRIV",
    "Government"               : "USGOVT",
    "Private Service-Providing": "CES0800000001",
    "Goods-Producing"          : "USGOOD",
    "Federal"                  : "CES9091000001",
    "State Government"         : "CES9092000001",
    "Local Government"         : "CES9093000001",
}

@st.cache_data(show_spinner=False)
def _panel():
    jobs = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES.items()],
        axis=1
    )
    rec  = _fred_series(RECESS, name="USREC")
    return jobs.join(rec, how="inner").dropna()

def _cumulative(df: pd.DataFrame, anchor: date) -> pd.DataFrame:
    anchor = pd.to_datetime(anchor)
    if anchor not in df.index:
        anchor = df.index[df.index.get_loc(anchor, method="bfill")]
    return df.sub(df.loc[anchor])

def _recession_periods(rec):
    rec = rec.astype(bool)
    start = rec & ~rec.shift(1, fill_value=False)
    end   = rec & ~rec.shift(-1, fill_value=False)
    return list(zip(start[start].index, end[end].index))

def _add_recessions(fig, periods):
    for s, e in periods:
        fig.add_vrect(x0=s, x1=e, fillcolor="grey",
                      opacity=0.25, line_width=0, layer="below")

# ───────────────────────────────────────────────────────────────────────────
def render_nfp():
    base   = _panel()                  # fetch data
    df_raw = base.drop(columns="USREC")
    df_cum = _cumulative(df_raw, ANCHOR)
    df     = df_cum[df_cum.index >= "2020-01-01"]
    df = df/1000.0 # convert to millions

    recess = _recession_periods(base["USREC"])

    start_axis = "2020-01-01"
    end_axis   = df.index.max().strftime("%Y-%m-%d")

    col1, col2 = st.columns(2, gap="large")

    # ---- 1) Private vs Government ---------------------------------------
    with col1:
        # YOUR custom header instead of Plotly title
        st.markdown(
            "<div style='font-size:26px; font-weight:700; "
            "margin-left:60px; line-height:1.1;'>"
            "Jobs Private vs Government<br>"
            "</div>",
            unsafe_allow_html=True,
        )

        f1 = go.Figure()
        f1.add_bar(x=df.index, y=df["Total Private"],
                   name="Total Private", marker_color="#0E84C8")
        f1.add_bar(x=df.index, y=df["Government"],
                   name="Government", marker_color="#002B45")
        _add_recessions(f1, recess)
        f1.update_layout(
            barmode="stack",
            height=FIG_H,
            template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=[start_axis, end_axis]),
            yaxis_title="Jobs",
            yaxis=dict(
            title="Jobs (millions)",
            tickformat=".0f",    # no decimals
            ticksuffix="M",      # add “M”
        ),
        )
        st.plotly_chart(f1, use_container_width=True)

    # ---- 2) Service-led breakdown ---------------------------------------
    with col2:
        # ANOTHER custom header
        st.markdown(
            "<div style='font-size:26px; font-weight:700; "
            "margin-left:60px; line-height:1.1;'>"
            "Service-Led Economy Breakdown"
            "</div>",
            unsafe_allow_html=True,
        )

        f2 = go.Figure()
        order  = ["Goods-Producing", "Private Service-Providing",
                  "Local Government", "State Government", "Federal"]
        colors = ["#FDBE4C", "#0E84C8", "#6C8EBF", "#2A4B7C", "#F28E2B"]
        for lbl, col in zip(order, colors):
            f2.add_bar(x=df.index, y=df[lbl], name=lbl, marker_color=col)
        _add_recessions(f2, recess)
        f2.update_layout(
            barmode="stack",
            height=FIG_H,
            template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=[start_axis, end_axis]),
            yaxis_title="Jobs",
            yaxis=dict(
            title="Jobs (millions)",
            tickformat=".0f",    # no decimals
            ticksuffix="M",      # add “M”
        ),
        )
        st.plotly_chart(f2, use_container_width=True)
