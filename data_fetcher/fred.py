import pandas_datareader.data as web
from datetime import datetime
import pandas as pd

DEFAULT_START = '1980-01-01'

def _fred_series(code: str,
                 start_date: str | None = None,
                 end_date: str | None = None,
                 rename_as: str | None = None) -> pd.DataFrame:
    """
    Generic wrapper around pandas‑datareader’s FRED reader.
    """
    start_date = start_date or DEFAULT_START
    end_date = end_date or datetime.now().strftime('%Y-%m-%d')
    df = web.DataReader(code, 'fred', start_date, end_date)
    if rename_as:
        df.columns = [rename_as]
    return df

#Number of people already on unemployment insurance who file a subsequent (i.e. weekly “continuing”) claim after their initial claim week
def continued_claims(start_date=None, end_date=None):
    return _fred_series('CCSA', start_date, end_date, 'Continued Claims')

#JOLTS – Job Openings: Total Nonfarm (seasonally adjusted)
def jolts_openings(start_date=None, end_date=None):
    return _fred_series('JTSJOL', start_date, end_date,
                        'Job Openings (Total NF)')

#The absolute change in Total Nonfarm Payrolls
def nonfarm_payroll_growth(start_date=None, end_date=None):
    df = _fred_series('PAYEMS', start_date, end_date, 'Total Nonfarm Payrolls')
    df['Unemployment Growth'] = df['Total Nonfarm Payrolls'].diff()
    return df[['Unemployment Growth']]


# Civilian labour force (total supply), seasonally adjusted.
def labour_supply(start_date=None, end_date=None):
    return _fred_series('CLF16OV', start_date, end_date, 'Labour Supply')


#Job Openings (Total NF) + Total Nonfarm Payrolls (employment level)
def labour_demand(start_date=None, end_date=None):
    df_open = _fred_series('JTSJOL', start_date, end_date, 'Job Openings (Total NF)')
    df_emp  = _fred_series('PAYEMS', start_date, end_date, 'Total Nonfarm Payrolls')

    df = df_open.join(df_emp, how='inner')
    
    # computing the sum
    df['Labour Demand'] = df['Job Openings (Total NF)'] + df['Total Nonfarm Payrolls']
    return df[['Labour Demand']]

#The number of people filing for unemployment insurance for the first time in a given week.
def initial_jobless_claims(start_date=None, end_date=None):
    return _fred_series('ICSA', start_date, end_date, 'Initial Jobless Claims (SA)')


def average_hourly_earnings(start_date=None, end_date=None):
    return _fred_series('AHETPI', start_date, end_date, 'Average Hourly Earnings')