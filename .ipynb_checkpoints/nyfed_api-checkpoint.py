# %% [markdown]
# New York Fed Markets Data 에서 시계열 데이터를 받아 pandas DataFrame으로 반환
#
# f_bank_reserves_sofr_iorb.py 에서 사용
# 아래와 같은 식으로 파라미터 입력 하여 사용
# ```python
# from nyfed_api import fetch_secured_rate
# # 사용자 정의 기간
# start = "2023-01-01"
# end = "2025-12-31"
#
# # Fetch series
# # 사용자 정의 데이터 시리즈 호출 secured rate['tgcr', 'sofr', 'bgcr']
#
# dftr = fetch_secured_rate("tgcr", start_date=start, end_date=end)
# ```
# %%
import requests
import pandas as pd
import os

from fred_api import fetch_fred_series

def fetch_secured_rate(rate_type="tgcr", start_date="2000-01-01", end_date="2025-12-31"):
    """
    NY Fed secured rate (TGCR, SOFR, BGCR 등)를 가져오는 함수.

    Parameters:
        rate_type (str): 'tgcr', 'sofr', or 'bgcr'
        start_date (str): 'YYYY-MM-DD'
        end_date (str): 'YYYY-MM-DD'

    Returns:
        pd.DataFrame: [Date, Rate] 형식의 DataFrame
    """
    rate_type = rate_type.lower()
    url = f"https://markets.newyorkfed.org/api/rates/secured/{rate_type}/search.json"

    params = {
        "startDate": start_date,
        "endDate": end_date,
        "type": "rate"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"❌ Failed to fetch {rate_type.upper()}: {response.status_code}\n{response.text}")

    data = response.json()
    records = data.get("refRates", [])
    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=["Date", f"{rate_type.upper()}"])

    df["effectiveDate"] = pd.to_datetime(df["effectiveDate"])
    df = df[["effectiveDate", "percentRate"]].rename(columns={
        "effectiveDate": "Date",
        "percentRate": rate_type.upper()
    })

    return df

#---------------------

def fetch_soma_holdings_asofdates():
    """
    NY Fed SOMA holdings에 asOfDates 를 가져오는 함수

    Parameters:

        start_date (str): 'YYYY-MM-DD'
        end_date (str): 'YYYY-MM-DD'

    Returns:
        pd.DataFrame: [Date, 증권 종류 ] 형식의 DataFrame
    """

    url = f"https://markets.newyorkfed.org/api/soma/asofdates/list.json"

    params = {

    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"❌ Failed to fetch all rates: {response.status_code}\n{response.text}")

    data = response.json()


    #days = pd.DataFrame(data.get("soma", {}).get("asOfDates", []))
    days = data.get("soma", {}).get("asOfDates", [])

    return days

start = fetch_soma_holdings_asofdates()[-1]
end = fetch_soma_holdings_asofdates()[0]


def fetch_soma_holdings(start_date=start, end_date=end):

    """
    NY Fed SOMA holdings를 가져오는 함수.

    Parameters:

        start_date (str): 'YYYY-MM-DD'
        end_date (str): 'YYYY-MM-DD'

    Returns:
        pd.DataFrame: [Date, 증권 종류 ] 형식의 DataFrame
    """

    url = f"https://markets.newyorkfed.org/api/soma/summary.json"

    params = {

    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"❌ Failed to fetch all rates: {response.status_code}\n{response.text}")

    data = response.json()


    df = pd.DataFrame(data.get("soma", {}).get("summary", []))

    df["Date"] = pd.to_datetime(df["asOfDate"])

    rename_dict = {
        "mbs": "MBS",
        "cmbs": "CMBS",
        "tips": "TIPS",
        "frn": "FRN",
        "tipsInflationCompensation": "TIPS INFLATION COMPENSATION",
        "notesbonds": "Notes and Bonds",
        "bills": "Bills",
        "agencies": "Agencies",
        "total": "Total"
    }

    # Rename columns
    df = df.rename(columns=rename_dict)

    # Convert renamed columns to numeric
    for _, new_col in rename_dict.items():

        # change column name to formal expressions
        # convert in Dollars to Million Dollars

        df[new_col] = pd.to_numeric(df[new_col], errors='coerce') / 1e6


    df = df[(df['Date']>=start_date) & (df['Date']<=end_date)]

    # rename 'Date' column to 'observation_date' to match FRED convention

    df = df.rename(columns={'Date': 'observation_date'})
    df.reset_index(drop=True, inplace=True)
    df['observation_date'] = pd.to_datetime(df['observation_date'])

# fetch TGA from FRED api and merge with df
    df1= fetch_fred_series(start_date=start, end_date=end, series_id="WDTGAL")

    df1.rename(columns={'WDTGAL': 'TGA'}, inplace=True)
    df = pd.merge(df, df1, on="observation_date", how="left")


    df.set_index('observation_date', inplace=True)

    return df


def fetch_series_list():

    """
    NY Fed Primary Dealer Position Securities List Descriptions for all timeseries data

    Parameters:


    Returns:
        pd.DataFrame: [Date, 증권 종류 ] 형식의 DataFrame
    """

    url = f"https://markets.newyorkfed.org/api/pd/list/timeseries.json"

    params = {

    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"❌ Failed to fetch all rates: {response.status_code}\n{response.text}")

    data = response.json()


    df = pd.DataFrame(data.get("pd", {}).get("timeseries", []))

    rename_dict = {
        "seriesbreak": "Series",
        "keyid": "Key",
        "description": "Description"
    }

    # Rename columns
    df = df.rename(columns=rename_dict)

    # Convert renamed columns to numeric
    for _, new_col in rename_dict.items():

        # change column name to formal expressions
        # convert in Dollars to Million Dollars

        df[new_col] = df[new_col]

    return df

def fetch_pdpositions(save_path="data/TimeSeries.csv"):
    url = "https://markets.newyorkfed.org/api/pd/get/all/timeseries.csv"
    response = requests.get(url)

    # 요청이 성공했는지 확인
    response.raise_for_status()

    # 저장할 디렉토리 없으면 생성
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # CSV 파일로 저장
    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path

fetch_pdpositions()