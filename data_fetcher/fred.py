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
    Returns a DataFrame with 'Unemployment Rate' (ICSA).
    """
    df_init = _fred_series("ICSA", start, end, name="Initial Claims")
    df_init['4 Week Moving Average'] = df_init['Initial Claims'].rolling(4).mean()
    return df_init


def get_continued_claims(start: str=None, end: str=None) -> pd.DataFrame:
    """
    Returns a DataFrame with 'Continued Claims' (CCSA).
    """
    df_cont = _fred_series("CCSA", start, end, name="Continued Claims")
    df_cont['4 Week Moving Average'] = df_cont['Continued Claims'].rolling(4).mean()
    return df_cont
