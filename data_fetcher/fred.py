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