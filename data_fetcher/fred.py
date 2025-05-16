import pandas_datareader.data as web
import pandas as pd
from datetime import datetime

DEFAULT_START = "1950-01-01"

# Reusable Wrapper to pull FRED Data
def _fred_series(code: str, start: str=None, end: str=None, name: str=None) -> pd.DataFrame:
    start = start or DEFAULT_START
    end   = end   or datetime.now().strftime("%Y-%m-%d")
    df    = web.DataReader(code, "fred", start, end)
    if name:
        df.columns = [name]
    return df


def get_employment_growth(start: str=None, end: str=None) -> pd.DataFrame:
    """
    Returns a DataFrame with:
      - 'Emp Growth': month-over-month diff in PAYEMS
      - '3M MA Emp Growth': 3-month rolling average
    """
    df = _fred_series("PAYEMS", start, end, name="Payroll Level")
    df["Emp Growth"]       = df["Payroll Level"].diff()
    df["3M MA Emp Growth"] = df["Emp Growth"].rolling(3).mean()
    return df[["Emp Growth", "3M MA Emp Growth"]]


def get_unemployment_rate(start: str=None, end: str=None) -> pd.DataFrame:
    """
    Returns a DataFrame with 'Unemployment Rate' (UNRATE).
    """
    return _fred_series("UNRATE", start, end, name="Unemployment Rate")


def get_initial_claims(start: str=None, end: str=None) -> pd.DataFrame:
    """
    Returns a DataFrame with 'Initial Claims' (ICSA) and 4-week moving average (IC4WSA).
    """
    df_init = _fred_series("ICSA", start, end, name="Initial Claims")
    df_init_4wma = _fred_series("IC4WSA", start, end, name="4 Week Moving Average")  # FRED series for 4-week MA
    df_init = df_init.join(df_init_4wma)  # Join the two dataframes by date
    return df_init

def get_continued_claims(start: str=None, end: str=None) -> pd.DataFrame:
    """
    Returns a DataFrame with 'Continued Claims' (CCSA) and 4-week moving average (CC4WSA).
    """
    df_cont = _fred_series("CCSA", start, end, name="Continued Claims")
    df_cont_4wma = _fred_series("CC4WSA", start, end, name="4 Week Moving Average")  # FRED series for 4-week MA
    df_cont = df_cont.join(df_cont_4wma)  # Join the two dataframes by date
    return df_cont

def get_labour_market_conditions(start: str=None, end: str=None) -> pd.DataFrame:
    """
    Returns a DataFrame with 'Labour Market Conditions from Kansas City FED'
    """
    return _fred_series("FRBKCLMCILA", start, end, name="LMCI")


def get_job_opening_per_person(start: str=None, end: str=None) -> pd.DataFrame:
    df_jolts = _fred_series("JTSJOL", start, end, name="Job Openings")
    df_unemp = _fred_series("UNEMPLOY", start, end, name="Unemployed")
    df = df_jolts.join(df_unemp, how="inner")
    df["Jobs per Unemployed"] = df["Job Openings"] / df["Unemployed"]
    return df[["Jobs per Unemployed"]]

#  Labor Supply  vs  Labor Demand  (+ balance)
def get_labor_supply_demand(start: str = None, end:   str = None) -> pd.DataFrame:
    """
    Returns a DataFrame with:
      - 'Labor Demand (Openings + Employment)'  — JTSJOL + PAYEMS
      - 'Labor Supply (Civilian Labor Force)'   — CLF16OV
    All series converted to **millions of persons** (÷1_000).
    """
    openings   = _fred_series("JTSJOL",   start, end, name="Job Openings")
    employment = _fred_series("PAYEMS",   start, end, name="Employment")
    labor_sup  = _fred_series("CLF16OV",  start, end, name="Labor Supply")

    data = openings.join(employment, how="inner")
    data["Labor Demand (Openings + Employment)"] = (data["Job Openings"] +
                                                    data["Employment"]) / 1_000
    data["Labor Supply (Civilian Labor Force)"]  = labor_sup["Labor Supply"] / 1_000
    return data[
        ["Labor Demand (Openings + Employment)",
         "Labor Supply (Civilian Labor Force)"]
    ]


def get_labor_balance(start: str = None, end:   str = None) -> pd.DataFrame:
    """
    Excess (Jobs-demand minus Supply) in millions.
    Positive ⇒ demand exceeds supply (= tight market).
    """
    df = get_labor_supply_demand(start, end)
    df["Excess Jobs"] = (
        df["Labor Supply (Civilian Labor Force)"] -
        df["Labor Demand (Openings + Employment)"]
        )
    return df[["Excess Jobs"]]
