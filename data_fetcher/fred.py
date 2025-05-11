# data_fetcher/fred.py
import pandas_datareader.data as web
import pandas as pd
from datetime import datetime

DEFAULT_START = "1950-01-01"

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
