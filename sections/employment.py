# sections/employment.py  ────────────────────────────────────────────────
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

from data_fetcher.fred import (
    get_employment_growth,
    get_unemployment_rate,
    get_initial_claims,
    get_continued_claims,
    _fred_series,
)

FIG_HEIGHT = 390
TOP_GAP_PX = 18


# Load data from the API
@st.cache_data(show_spinner=False)
def _load():
    df_emp, df_unr = get_employment_growth(), get_unemployment_rate()
    df_init, df_cont = get_initial_claims(), get_continued_claims()
    return df_emp, df_unr, df_init, df_cont



# ── subsection helpers ──────────────────────────────────────────────────
def _render_general(df_emp, df_unr):
    """Employment Growth and Unemployment Rate Graphs."""
    # Calculating percentile ranks 
    emp_rank_pct = (df_emp["Emp Growth"] < df_emp["Emp Growth"].iloc[-1]).mean() * 100
    unr_rank_pct = (df_unr["Unemployment Rate"]
                    < df_unr["Unemployment Rate"].iloc[-1]).mean() * 100

    left, right = st.columns(2, gap="large")

    # --------- Employment-Growth chart ----------
    with left:
        st.markdown(
            f"""
            <div style='font-size:20px; font-weight:700; line-height:1.2; margin-left:85px;'>
            Employment Growth
            </div>
            <div style='font-size:20px; font-weight:700; line-height:1.2; margin-left:85px;'>
            Ranking: {emp_rank_pct:.2f}%
            </div>
            """, unsafe_allow_html=True,
        )


        st.markdown(f"<div style='height:{TOP_GAP_PX}px'></div>", unsafe_allow_html=True)

        start_default = "2023-01-01"
        end_default   = df_emp.index.max()

        mask      = (df_emp.index >= start_default) & (df_emp.index <= end_default)
        y_visible = np.concatenate([
            df_emp.loc[mask, "Emp Growth"].values,
            df_emp.loc[mask, "3M MA Emp Growth"].values
        ])
        y_pad   = 0.05 * (y_visible.max() - y_visible.min())
        y_range = [y_visible.min() - y_pad, y_visible.max() + y_pad]

        fig_emp = go.Figure()
        fig_emp.add_trace(go.Scatter(
            x=df_emp.index, y=df_emp["Emp Growth"],
            name="All Employees, Total Nonfarm",
            line=dict(color="#049CA4", width=2)
        ))
        fig_emp.add_trace(go.Scatter(
            x=df_emp.index, y=df_emp["3M MA Emp Growth"],
            name="3-Month MA",
            line=dict(color="black", width=2)
        ))
        fig_emp.update_layout(
            height=FIG_HEIGHT,
            yaxis_title="Change (Thousands of persons)",
            template="simple_white",
            font=dict(size=12),
            margin=dict(l=50, r=25, t=30, b=45),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.18,
                xanchor="left",   x=0,
                font=dict(size=12),
            ),
            xaxis=dict(type="date", range=[start_default, end_default],
                       tickformat="%b %Y"),
            yaxis=dict(range=y_range),
        )
        st.plotly_chart(fig_emp, use_container_width=True)

    # --------- Unemployment-Rate chart ----------
    with right:

        st.markdown(
            f"""
            <div style='font-size:20px; font-weight:700; line-height:1.2; margin-left:85px;'>
            Unemployment Rate
            </div>
            <div style='font-size:20px; font-weight:700; line-height:1.2; margin-left:85px;'>
            Ranking: {unr_rank_pct:.2f}%
            </div>
            """, unsafe_allow_html=True,
        )

        st.markdown(f"<div style='height:{TOP_GAP_PX}px'></div>", unsafe_allow_html=True)
        # add vertical space to shift the graph
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)


        fig_unr = px.line(
            df_unr,
            labels={"index": "", "value": "% Percentage points"},
            height=FIG_HEIGHT,
            color_discrete_sequence=["#1B65C0"],
        )

        avg = df_unr["Unemployment Rate"].mean()
        fig_unr.add_hline(
            y=avg, line_dash="dash",
            annotation_text=f"Long-run avg {avg:.2f}%",
            annotation_position="top left",
            annotation_yshift=150,
        )

        rec = _fred_series("USREC", name="USREC")
        for s, e in zip(rec[rec["USREC"].diff() == 1].index,
                        rec[rec["USREC"].diff() == -1].index):
            fig_unr.add_vrect(x0=s, x1=e, fillcolor="lightgrey",
                              opacity=0.30, line_width=0)

        fig_unr.update_layout(
            template="simple_white",
            font=dict(size=12),
            margin=dict(l=50, r=25, t=30, b=45),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.18,
                xanchor="left",   x=0,
                font=dict(size=12),
            ),
            legend_title_text=None,
        )
        st.plotly_chart(fig_unr, use_container_width=True)

#Render initial claims and continued claims
def _render_initial_vs_continued(df_init, df_cont):
    """Render Initial Claims vs Continued Claims charts with 4-week moving average."""
    left, right = st.columns(2, gap="large")  # Create two columns for side-by-side layout

    # Define the start date for the initial view (2023 onwards)
    start_default = "2023-01-01"
    end_default = df_init.index.max()  # or df_cont.index.max() if you prefer

    # Filter data to focus on the desired range (2023 onwards) for initial y-range calculation
    mask_init = (df_init.index >= start_default) & (df_init.index <= end_default)
    mask_cont = (df_cont.index >= start_default) & (df_cont.index <= end_default)

    # Calculate y-range for Initial Claims
    y_visible_init = np.concatenate([
        df_init.loc[mask_init, 'Initial Claims'].values,
        df_init.loc[mask_init, '4 Week Moving Average'].values
    ])
    y_pad_init = 0.05 * (y_visible_init.max() - y_visible_init.min())  # 5% padding
    y_range_init = [y_visible_init.min() - y_pad_init, y_visible_init.max() + y_pad_init]

    # Plot Initial Claims with 4-week moving average in the left column
    with left:

        st.markdown(
            """
            <div style="font-size:24px; font-weight:700; margin-left:85px;">
              Initial Claims
            </div>
            """, unsafe_allow_html=True)
        
        fig_init = go.Figure()

        fig_init.add_trace(go.Scatter(
            x=df_init.index, y=df_init['Initial Claims'],
            name="Initial Claims",
            line=dict(color="#1F77B4", width=2)
        ))

        fig_init.add_trace(go.Scatter(
            x=df_init.index, y=df_init['4 Week Moving Average'],
            name="4 Week Moving Average",
            line=dict(color="black", width=2)
        ))

        fig_init.update_layout(
            height=FIG_HEIGHT,
            yaxis_title="Claims",
            template="simple_white",
            font=dict(size=12),
            margin=dict(l=50, r=25, t=30, b=45),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.18,
                xanchor="left", x=0,
                font=dict(size=12),
            ),
            xaxis=dict(
                type="date",
                range=[start_default, end_default],  # Default to 2023 onwards
                tickformat="%b %Y"
            ),
            yaxis=dict(range=y_range_init),  # Apply y-range for Initial Claims
        )
        st.plotly_chart(fig_init, use_container_width=True)

    # Calculate y-range for Continued Claims
    y_visible_cont = np.concatenate([
        df_cont.loc[mask_cont, 'Continued Claims'].values,
        df_cont.loc[mask_cont, '4 Week Moving Average'].values
    ])
    y_pad_cont = 0.05 * (y_visible_cont.max() - y_visible_cont.min())  # 5% padding
    y_range_cont = [y_visible_cont.min() - y_pad_cont, y_visible_cont.max() + y_pad_cont]

    # Plot Continued Claims with 4-week moving average in the right column
    with right:

        st.markdown(
            """
            <div style="font-size:24px; font-weight:700; margin-left:85px;">
              Continued Claims
            </div>
            """, unsafe_allow_html=True)
        
        fig_cont = go.Figure()

        fig_cont.add_trace(go.Scatter(
            x=df_cont.index, y=df_cont['Continued Claims'],
            name="Continued Claims",
            line=dict(color="#FF7F0E", width=2)
        ))

        fig_cont.add_trace(go.Scatter(
            x=df_cont.index, y=df_cont['4 Week Moving Average'],
            name="4 Week Moving Average",
            line=dict(color="black", width=2)
        ))

        fig_cont.update_layout(
            height=FIG_HEIGHT,
            yaxis_title="Claims",
            template="simple_white",
            font=dict(size=12),
            margin=dict(l=50, r=25, t=30, b=45),
            legend=dict(
                orientation="h",
                yanchor="bottom", y=1.18,
                xanchor="left", x=0,
                font=dict(size=12),
            ),
            xaxis=dict(
                type="date",
                range=[start_default, end_default],  # Default to 2023 onwards
                tickformat="%b %Y"
            ),
            yaxis=dict(range=y_range_cont),  # Apply y-range for Continued Claims
        )
        st.plotly_chart(fig_cont, use_container_width=True)




# ── public entry-point ─────────────────────────────────────────────────
def render():
    """Top-level call from Home.py – builds the sub-tabs."""
    df_emp, df_unr, df_init, df_cont = _load()

    gen_tab, nfp_tab, wages_tab, alt_tab = st.tabs(
        ["General", "NFP", "Wages", "Alternatives"]
    )

    with gen_tab:
        _render_general(df_emp, df_unr)
        _render_initial_vs_continued(df_init, df_cont)

    with nfp_tab:
        st.info("Coming soon.")

    with wages_tab:
        st.info("Coming soon.")

    with alt_tab:
        st.info("Coming soon.")
