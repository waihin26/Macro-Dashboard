import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from data_fetcher.fred import _fred_series    

FIG_H   = 390
ANCHOR  = date(2020, 1, 1)       
RECESS  = "USREC"                

SERIES = {
    "Total Private"             : "CES0500000003",
    "Goods-Producing"           : "CES0600000003",
    "Private Service-Providing" : "CES0800000003",
    "CPI"                       : "CPIAUCSL",
    "TTU"                       : "CES4000000003",   
    "Information"               : "CES5000000003",  
    "Financial"                 : "CES5500000003",   
    "Business"                  : "CES6000000003",   
    "Private Edu. & Health"     : "CES6500000003",   
    "Leisure & Hosp."           : "CES7000000003",   
    "Mining and Logging"        : "CES1000000003",  
    "Construction"              : "CES2000000003",   
    "Manufacturing"             : "CES3000000003",
    "Non-supervisory"           : "AHETPI",   
    "ECI Wages"                 : "ECIWAG", 
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

    # Private wages vs CPI 
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


# Sub-sector wage lines vs CPI  
def render_wages_subsector() -> None:
    df, recess, x_rng = _prepared()

    row1, row2 = st.columns(2, gap="large")

    # ---------- (a) Services detail --------------------------------------
    with row1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:85px;'>"
            "Services by Sub-Sector</div>",
            unsafe_allow_html=True,
        )

        serv_order  = ["TTU", "Information", "Financial",
                       "Business", "Private Edu. & Health",
                       "Leisure & Hosp.", "CPI"]
        serv_colors = ["#0E84C8", "#6C8EBF", "#2A7F9C",
                       "#002B45", "#FABB2A", "#FDBE4C", "#F28E2B"]

        fig = go.Figure()
        for lbl, col in zip(serv_order, serv_colors):
            fig.add_scatter(x=df.index, y=df[lbl],
                            name=lbl, mode="lines",
                            line=dict(width=3, color=col))
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Percent", tickformat=".1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom",
                        y=1.02, x=0.01, font=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------- (b) Goods detail -----------------------------------------
    with row2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:85px;'>"
            "Goods&nbsp;By&nbsp;Sub-Sector</div>",
            unsafe_allow_html=True,
        )

        goods_order  = ["Manufacturing", "Construction",
                        "Mining and Logging", "CPI"]
        goods_colors = ["#9EC9E2", "#18A5C2", "#F4B400", "#F28E2B"]

        fig = go.Figure()
        for lbl, col in zip(goods_order, goods_colors):
            fig.add_scatter(x=df.index, y=df[lbl],
                            name=lbl, mode="lines",
                            line=dict(width=3, color=col))
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Percent", tickformat=".1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom",
                        y=1.02, x=0.01, font=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)



# Non-supervisory AHE vs CPI  +  Employment-Cost-Index YoY           #
def render_wage_benchmarks() -> None:
    df_pct, recess, x_rng = _prepared()         
    base     = _panel()                         

    # ---- build ECI YoY (quarterly) ------------------------------
    eci_yoy = base["ECI Wages"].pct_change(4) * 100   # 4 quarters ⇒ YoY
    eci_yoy = eci_yoy.dropna()

    col1, col2 = st.columns(2, gap="large")

    # ---------- Non-supervisory earnings vs CPI ---------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:85px;'>"
            "Non-Supervisory Wages&nbsp;Vs&nbsp;CPI</div>",
            unsafe_allow_html=True,
        )

        fig = go.Figure()
        fig.add_scatter(
            x=df_pct.index, y=df_pct["Non-supervisory"],
            name="Non-supervisory", mode="lines",
            line=dict(width=3, color="#18A5C2")
        )
        fig.add_scatter(
            x=df_pct.index, y=df_pct["CPI"],
            name="CPI", mode="lines",
            line=dict(width=3, color="#0D1F2D")
        )
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Percent", tickformat=".1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------- Employment Cost Index YoY ---------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:85px;'>"
            "Employment Cost Index – Wages (YoY)</div>",
            unsafe_allow_html=True,
        )

        fig = go.Figure()
        fig.add_scatter(
            x=eci_yoy.index, y=eci_yoy,
            name="ECI Wages YoY", mode="lines",
            line=dict(width=3, color="#F4B400")
        )
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=x_rng),
            yaxis=dict(title="Percent", tickformat=".1f", ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

