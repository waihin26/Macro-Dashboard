import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from data_fetcher.fred import _fred_series 

FIG_H   = 390
RECESS  = "USREC"

SERIES = {
    "EPOP 25-54 Yrs"           : "LNS12300060",   # Employment-Population, 25-54
    "Unemployed ≥15wks (U-1)"  : "U1RATE",        # U-1 unemployment rate
}

SERIES_OT_PT = {
    "OT – Manufacturing"       : "CES3000000004",   # Avg weekly OT hrs, all emp. – manufacturing :contentReference[oaicite:0]{index=0}
    "OT – Nondurable Goods"    : "CES3200000004",   # Avg weekly OT hrs, all emp. – nondurable goods :contentReference[oaicite:1]{index=1}
    "Part-Time Econ Reasons"   : "LNS12032194",     # Employment level, part-time for economic reasons :contentReference[oaicite:2]{index=2}
}

SERIES_QUITS = {
    "Quits – Total"                        : "JTSQUL",
    "Professional and Business Services"   : "JTS540099QUL",
    "Manufacturing"                        : "JTS3000QUL",
    "Leisure and Hospitality"              : "JTS7000QUL",
    "Retail Trade"                         : "JTS4400QUL",
}


def _panel():
    df = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES.items()],
        axis=1
    )
    rec = _fred_series(RECESS, name="USREC")      # NBER recession flags
    return df.join(rec, how="inner").dropna()

@st.cache_data(show_spinner=False)
def _panel_ot_pt():
    df   = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES_OT_PT.items()],
        axis=1
    )
    rec  = _fred_series(RECESS, name="USREC")
    return df.join(rec, how="inner").dropna()

@st.cache_data(show_spinner=False)
def _panel_quits():
    df  = pd.concat(
        [_fred_series(code, name=lbl) for lbl, code in SERIES_QUITS.items()],
        axis=1
    )
    rec = _fred_series(RECESS, name="USREC")
    return df.join(rec, how="inner").dropna()


def _recession_periods(rec):
    rec = rec.astype(bool)
    start = rec & ~rec.shift(1, fill_value=False)
    end   = rec & ~rec.shift(-1, fill_value=False)
    return list(zip(start[start].index, end[end].index))

def _add_recessions(fig, periods):
    for s, e in periods:
        fig.add_vrect(x0=s, x1=e, fillcolor="grey",
                      opacity=0.25, line_width=0, layer="below")
        

def render_alt_labor() -> None:
    """Render EPOP 25-54 and U-1 unemployment side by side."""
    df      = _panel()
    recess  = _recession_periods(df["USREC"])

    col1, col2 = st.columns(2, gap="large")

    # ----- 25-54 Employment-Population Ratio -----------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "% of Employed Persons&nbsp;(Aged 25-54)</div>",
            unsafe_allow_html=True,
        )


        fig = go.Figure()
        fig.add_scatter(
            x=df.index, y=df["EPOP 25-54 Yrs"],
            mode="lines", name="EPOP 25-54", line=dict(width=3, color="#18A5C2")
        )
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            yaxis=dict(title="Percent", tickformat=".1f", ticksuffix="%"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ----- U-1 Unemployment Rate ----------------------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "Labor&nbsp;Force&nbsp;Unemployed&nbsp;15&nbsp;Weeks&nbsp;+&nbsp;(U-1)</div>",
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        fig.add_scatter(
            x=df.index, y=df["Unemployed ≥15wks (U-1)"],
            mode="lines", name="U-1", line=dict(width=3, color="#0D1F2D")
        )
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            yaxis=dict(title="Percent", tickformat=".1f", ticksuffix="%"),
        )
        st.plotly_chart(fig, use_container_width=True)


def render_overtime_and_parttime() -> None:
    """
    (1) Average Weekly Overtime Hours – Manufacturing vs Nondurable Goods
    (2) Part-Time for Economic Reasons (millions), bar chart
    """
    df     = _panel_ot_pt()
    recess = _recession_periods(df["USREC"])

    start_date = "2021-01-01"
    end_date   = df.index.max().strftime("%Y-%m-%d")

    # -------- data wrangling -------------
    df_pt_mln = df["Part-Time Econ Reasons"] / 1_000   # thousands → millions

    col1, col2 = st.columns(2, gap="large")

    # ----- (a) overtime hours ---------------------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:24px;font-weight:700;margin-left:75px;'>"
            "Average Weekly Overtime Hours of All Employees</div>",
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        fig.add_scatter(x=df.index, y=df["OT – Manufacturing"],
                        mode="lines", name="Manufacturing",
                        line=dict(width=3, color="#18A5C2"))
        fig.add_scatter(x=df.index, y=df["OT – Nondurable Goods"],
                        mode="lines", name="Nondurable Goods",
                        line=dict(width=3, color="#0D1F2D"))
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=[start_date, end_date]), 
            yaxis=dict(title="Hours", tickformat=".1f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ----- (b) part-time for economic reasons -----------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:75px;'>"
            "Part-Time&nbsp;Labor&nbsp;for&nbsp;Economic&nbsp;Reasons</div>",
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        fig.add_bar(x=df_pt_mln.index, y=df_pt_mln,
                    name="Part-Time Econ Reasons",
                    marker_color="#9EC9E2")
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(range=[start_date, end_date]), 
            yaxis=dict(title="Millions of People", tickformat=".1f"),
        )
        st.plotly_chart(fig, use_container_width=True)


def render_quits() -> None:
    """
    (1) Total quits (bar); (2) stacked quits for four headline sectors.
    """
    df      = _panel_quits()
    recess  = _recession_periods(df["USREC"])

    # -- zoom window: Jan-2021 to latest date in df
    start_date = "2020-01-01"
    end_date   = df.index.max().strftime("%Y-%m-%d")


    col1, col2 = st.columns(2, gap="large")

    # ---------- (a) Total quits ------------------------------------------
    with col1:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:85px;'>"
            "People&nbsp;Quitting&nbsp;Their&nbsp;Job</div>",
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        fig.add_bar(
            x=df.index, y=df["Quits – Total"],   # thousands → thousands (keep scale)
            name="Total Quits", marker_color="#84C2E5"
        )
        _add_recessions(fig, recess)
        fig.update_layout(
            height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(
            range=[start_date, end_date],   # show 2020-present on load
            type="date"),                   
            yaxis=dict(title="Thousands of People", tickformat=".0f"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ---------- (b) Quits – selected sectors -----------------------------
    with col2:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;margin-left:85px;'>"
            "Quits&nbsp;–&nbsp;Selected&nbsp;Sectors</div>",
            unsafe_allow_html=True,
        )

        order  = ["Professional and Business Services",
                  "Manufacturing", "Leisure and Hospitality",
                  "Retail Trade"]
        colors = ["#EF6F00", "#F3C400", "#008FD5", "#9EC9E2"]

        fig = go.Figure()
        for lbl, col in zip(order, colors):
            fig.add_bar(
                x=df.index, y=df[lbl], name=lbl,
                marker_color=col
            )
        _add_recessions(fig, recess)
        fig.update_layout(
            barmode="stack", height=FIG_H, template="simple_white",
            margin=dict(t=20, b=25),
            xaxis=dict(
            range=[start_date, end_date],   
            type="date"),                 
            yaxis=dict(title="Thousands of People", tickformat=".0f"),
            legend=dict(orientation="h", yanchor="bottom",
                        y=1.02, x=0.01, font=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)