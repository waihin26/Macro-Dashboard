import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from data_fetcher.fred import _fred_series

FIG_H   = 390
ANCHOR  = date(2020, 1, 1)       # baseline for cumulative Δ
RECESS  = "USREC"                # recession flag

SERIES = {
    # headline splits
    "Total Private"             : "USPRIV",
    "Government"                : "USGOVT",
    "Private Service-Providing" : "CES0800000001",   
    "Goods-Producing"           : "USGOOD",
    "Federal"                   : "CES9091000001",
    "State Government"          : "CES9092000001",
    "Local Government"          : "CES9093000001",

    # service sub-sectors  ❱❱ use the short IDs
    "TTU"                       : "USTPU",
    "Information"               : "USINFO",
    "Financial"                 : "USFIRE",
    "Business"                  : "USPBS",
    "Private Edu. & Health"     : "USEHS",
    "Leisure & Hosp."           : "USLAH",
    "Other"                     : "USSERV",

    # goods sub-sectors      
    "Mining and Logging"        : "USMINE",
    "Construction"              : "USCONS",
    "Manufacturing"             : "MANEMP",
}


@st.cache_data(show_spinner=False)
def _panel():
    jobs = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES.items()], axis=1
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

def _prepared():
    """
    Returns
        df_m      : cumulative Δ since ANCHOR, 2020-onward, millions
        recess    : list[(start,end)]
        x_range   : [str, str] for layout
    """
    base   = _panel()
    df_raw = base.drop(columns="USREC")
    df_cum = _cumulative(df_raw, ANCHOR)
    df_m   = df_cum.loc["2020-01-01":] / 1_000.0        # millions
    recess = _recession_periods(base["USREC"])
    x_rng  = ["2020-01-01", df_m.index.max().strftime("%Y-%m-%d")]
    return df_m, recess, x_rng

def _add_recessions(fig, periods):
    for s, e in periods:
        fig.add_vrect(x0=s, x1=e, fillcolor="grey",
                      opacity=0.25, line_width=0, layer="below")


def render_nfp() -> None:
    df, recess, x_rng = _prepared()

    col1, col2 = st.columns(2, gap="large")

    # ---- Private vs Government -----------------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;"
            "margin-left:85px;'>Jobs Private vs Government</div>",
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        fig.add_bar(x=df.index, y=df["Total Private"],
                    name="Total Private", marker_color="#0E84C8")
        fig.add_bar(x=df.index, y=df["Government"],
                    name="Government", marker_color="#002B45")
        _add_recessions(fig, recess)
        fig.update_layout(
            barmode="stack", height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Jobs (millions)", tickformat=".0f", ticksuffix=" M"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---- Service-led breakdown -----------------------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;"
            "margin-left:85px;'>Service-Led Economy Breakdown</div>",
            unsafe_allow_html=True,
        )
        labels = ["Goods-Producing", "Private Service-Providing",
                  "Local Government", "State Government", "Federal"]
        colors = ["#FDBE4C", "#0E84C8", "#6C8EBF", "#2A4B7C", "#F28E2B"]
        fig = go.Figure()
        for lbl, col in zip(labels, colors):
            fig.add_bar(x=df.index, y=df[lbl], name=lbl, marker_color=col)
        _add_recessions(fig, recess)
        fig.update_layout(
            barmode="stack", height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Jobs (millions)", tickformat=".0f", ticksuffix=" M"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.caption("Source: BLS CES & NBER recession dates via FRED. Figures in millions.")

# Sub-sector charts  
def render_nfp_subsector() -> None:
   
    df, recess, x_rng = _prepared()

    row1, row2 = st.columns(2, gap="large")

    # --- Services by sub-sector -----------------------------------------
    with row1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;"
            "margin-left:85px;'>Services by Sub-Sector</div>",
            unsafe_allow_html=True,
        )
        serv_order  = ["TTU", "Information", "Financial",
                       "Business", "Private Edu. & Health",
                       "Leisure & Hosp.", "Other"]
        serv_colors = ["#FDBE4C", "#FABB2A", "#F29D35",
                       "#0E84C8", "#1F5673", "#2A7F9C", "#8DB7C7"]
        fig = go.Figure()
        for lbl, col in zip(serv_order, serv_colors):
            fig.add_bar(x=df.index, y=df[lbl], name=lbl, marker_color=col)
        _add_recessions(fig, recess)
        fig.update_layout(
            barmode="stack", height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Jobs (millions)", tickformat=".0f", ticksuffix=" M"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Goods by sub-sector --------------------------------------------
    with row2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;"
            "margin-left:85px;'>Goods by Sub-Sector</div>",
            unsafe_allow_html=True,
        )
        goods_order  = ["Mining and Logging", "Construction", "Manufacturing"]
        goods_colors = ["#FDBE4C", "#0E84C8", "#6C8EBF"]
        fig = go.Figure()
        for lbl, col in zip(goods_order, goods_colors):
            fig.add_bar(x=df.index, y=df[lbl], name=lbl, marker_color=col)
        _add_recessions(fig, recess)
        fig.update_layout(
            barmode="stack", height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Jobs (millions)", tickmode="linear", dtick=0.5, tickformat=".1f", ticksuffix=" M"),
        )
        st.plotly_chart(fig, use_container_width=True)