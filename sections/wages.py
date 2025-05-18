import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from data_fetcher.fred import _fred_series    

FIG_H   = 390
ANCHOR  = date(2020, 1, 1)       
RECESS  = "USREC"                

SERIES = {
    # Average hourly earnings (SA, $/hour)
    "Total Private"             : "CES0500000003",
    "Goods-Producing"           : "CES0600000003",
    "Private Service-Providing" : "CES0800000003",

    # Headline CPI (index 1982-84 = 100)
    "CPI"                       : "CPIAUCSL",
}

@st.cache_data(show_spinner=False)
def _panel():
    wages = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES.items()],
        axis=1
    )
    rec   = _fred_series(RECESS, name="USREC")
    return wages.join(rec, how="inner").dropna()

def _pct_change(df: pd.DataFrame, anchor: date) -> pd.DataFrame:
    anchor = pd.to_datetime(anchor)
    if anchor not in df.index:
        anchor = df.index[df.index.get_loc(anchor, method="bfill")]
    return (df.div(df.loc[anchor]).sub(1)).mul(100)

def _recession_periods(rec):
    rec = rec.astype(bool)
    start = rec & ~rec.shift(1, fill_value=False)
    end   = rec & ~rec.shift(-1, fill_value=False)
    return list(zip(start[start].index, end[end].index))

def _prepared():
    """
    Returns
        df_pct   : %-change since ANCHOR (2020-01-01 onward)
        recess   : list of (start, end) tuples
        x_range  : two-element list for Plotly layout
    """
    base   = _panel()
    df_raw = base.drop(columns="USREC")
    df_pct = _pct_change(df_raw, ANCHOR).loc["2020-01-01":]
    recess = _recession_periods(base["USREC"])
    x_rng  = ["2020-01-01", df_pct.index.max().strftime("%Y-%m-%d")]
    return df_pct, recess, x_rng

def _add_recessions(fig, periods):
    for s, e in periods:
        fig.add_vrect(x0=s, x1=e, fillcolor="grey",
                      opacity=0.25, line_width=0, layer="below")
        


def render_wages_vs_cpi() -> None:
    df, recess, x_rng = _prepared()

    col1, col2 = st.columns(2, gap="large")

    # ---------- (1) Private wages vs CPI --------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:85px;'>"
            "Private Wages&nbsp;Vs&nbsp;CPI</div>",
            unsafe_allow_html=True,
        )

        fig1 = go.Figure()
        fig1.add_scatter(x=df.index, y=df["Total Private"],
                         name="Total Private", mode="lines",
                         line=dict(width=3, color="#18A5C2"))
        fig1.add_scatter(x=df.index, y=df["CPI"],
                         name="CPI", mode="lines",
                         line=dict(width=3, color="#0D1F2D"))
        _add_recessions(fig1, recess)
        fig1.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Percent", tickformat=".1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01),
        )
        st.plotly_chart(fig1, use_container_width=True)

    # ---------- (2) Goods & services wages vs CPI -----------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:85px;'>"
            "Goods&nbsp;&amp;&nbsp;Services&nbsp;Vs&nbsp;CPI</div>",
            unsafe_allow_html=True,
        )

        order  = ["Goods-Producing", "Private Service-Providing", "CPI"]
        colors = ["#18A5C2", "#9EC9E2", "#F4B400"]

        fig2 = go.Figure()
        for lbl, col in zip(order, colors):
            fig2.add_scatter(x=df.index, y=df[lbl],
                             name=lbl, mode="lines",
                             line=dict(width=3, color=col))
        _add_recessions(fig2, recess)
        fig2.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Percent", tickformat=".1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01),
        )
        st.plotly_chart(fig2, use_container_width=True)
