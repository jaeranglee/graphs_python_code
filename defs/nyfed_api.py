# %% [markdown]
# # New York Fed Markets Data API: 금리·SOMA·Primary Dealer
# ## file name
# - nyfed_api.py
#
# ## 기능
# - 뉴욕 연준 Markets Data API에서 secured rate(TGCR/SOFR/BGCR), SOMA 보유 증권, Primary Dealer 포지션 자료를 받는다.
# - 캐시 없음
#
# ## 출처
# - https://markets.newyorkfed.org/static/docs/markets-api.html
# - API: `https://markets.newyorkfed.org/api/rates/secured/{rate_type}/search.json`, `/api/soma/summary.json`,
#   `/api/pd/list/timeseries.json`, `/api/pd/get/all/timeseries.csv`
# - API key 필요 없음 (`fetch_soma_holdings`는 FRED TGA를 같이 받으므로 `FRED_API_KEY` 필요)
#
# ## fetch_secured_rate()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from nyfed_api import fetch_secured_rate, fetch_soma_holdings, fetch_pdpositions
#
# dftr = fetch_secured_rate(rate_type="tgcr", start_date="2023-01-01", end_date="2026-10-30")
# soma = fetch_soma_holdings(start_date="2020-01-01", end_date="2026-10-30")
# path = fetch_pdpositions("data/TimeSeries.csv")
# ```
#
# ## parameters (fetch_secured_rate)
# | Parameter    | Type  | Description                          |
# |--------------|-------|--------------------------------------|
# | `rate_type`  | `str` | `tgcr`, `sofr`, `bgcr`                |
# | `start_date` | `str` | 시작일 `YYYY-MM-DD`                   |
# | `end_date`   | `str` | 종료일 `YYYY-MM-DD`                   |
#
# ## returned columns and values
# | Function | Columns |
# |----------|---------|
# | `fetch_secured_rate` | `Date`(datetime), `<RATE_TYPE>`(금리 %, 예: `TGCR`) |
# | `fetch_soma_holdings` | index `observation_date`; `Bills`, `Notes and Bonds`, `FRN`, `TIPS`, `TIPS INFLATION COMPENSATION`, `Agencies`, `MBS`, `CMBS`, `Total` (백만 달러), `TGA`(FRED WDTGAL) |
# | `fetch_series_list` | `Series`, `Key`, `Description` (Primary Dealer 시계열 목록) |
# | `fetch_pdpositions` | 저장한 CSV 경로 (`save_path`, 기본 `data/TimeSeries.csv`) |
#
# ## 그 밖의 함수
# - `fetch_secured_series(rate_type="tgcr", start_date="2000-01-01", end_date="2025-12-31")`: 금리와 거래량을 함께 받아
#   `Date`, `<RATE_TYPE>`(%), `<RATE_TYPE>_VOLUME`(10억 달러) DataFrame으로 (graphs_python_code/nyfed_api_vol_rate.py에서 옮김)
# - `fetch_soma_holdings_asofdates()`: SOMA 자료 기준일 목록 (최신일이 맨 앞)
#
# ## 사용하는 곳
# - `wallstreet/f_soma_holdings.py`, `wallstreet/f_nyfed_pdposition.py`, `wallstreet/nyfed_ftr_fdr.py`, `graphs_python_code/f32_nyfed_pdposition.py`
# %%

import os

import pandas as pd
import requests

from fred_api import fetch_fred_series


def fetch_secured_rate(rate_type, start_date, end_date):

    rate_type = rate_type.lower()
    url = f"https://markets.newyorkfed.org/api/rates/secured/{rate_type}/search.json"

    params = {"startDate": start_date, "endDate": end_date, "type": "rate"}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(
            f"❌ Failed to fetch {rate_type.upper()}: {response.status_code}\n{response.text}"
        )

    data = response.json()
    records = data.get("refRates", [])
    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=["Date", f"{rate_type.upper()}"])

    df["effectiveDate"] = pd.to_datetime(df["effectiveDate"])
    df = df[["effectiveDate", "percentRate"]].rename(
        columns={"effectiveDate": "Date", "percentRate": rate_type.upper()}
    )

    return df


# %% [markdown]
# ## sub function for fetching soma holdings
# NY Fed SOMA holdings에 asOfDates 를 가져오는 함수
# %%


def fetch_soma_holdings_asofdates():

    url = f"https://markets.newyorkfed.org/api/soma/asofdates/list.json"

    params = {}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(
            f"❌ Failed to fetch all rates: {response.status_code}\n{response.text}"
        )

    data = response.json()
    days = data.get("soma", {}).get("asOfDates", [])

    return days


if __name__ == "__main__":
    start = fetch_soma_holdings_asofdates()[-1]
    end = fetch_soma_holdings_asofdates()[0]


# %% [markdown]
# ## fetch_soma_holdings()
# NY Fed SOMA holdings value를 가져오는 함수
# %%


def fetch_soma_holdings(start_date, end_date):

    url = f"https://markets.newyorkfed.org/api/soma/summary.json"

    params = {}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(
            f"❌ Failed to fetch all rates: {response.status_code}\n{response.text}"
        )

    data = response.json()

    df = pd.DataFrame(data.get("soma", {}).get("summary", []))

    # rename 'Date' column to 'observation_date' to match FRED convention
    df = df.rename(columns={"asOfDate": "observation_date"})

    rename_dict = {
        "mbs": "MBS",
        "cmbs": "CMBS",
        "tips": "TIPS",
        "frn": "FRN",
        "tipsInflationCompensation": "TIPS INFLATION COMPENSATION",
        "notesbonds": "Notes and Bonds",
        "bills": "Bills",
        "agencies": "Agencies",
        "total": "Total",
    }

    # Rename columns
    df = df.rename(columns=rename_dict)
    print(df)
    # Convert renamed columns to numeric
    for _, new_col in rename_dict.items():

        # change column name to formal expressions
        # convert in Dollars to Million Dollars

        df[new_col] = pd.to_numeric(df[new_col], errors="coerce") / 1e6

    df = df[
        (df["observation_date"] >= start_date) & (df["observation_date"] <= end_date)
    ]

    df = df.reset_index(drop=True)
    df["observation_date"] = pd.to_datetime(df["observation_date"])

    # fetch TGA from FRED api and merge with df
    df1 = fetch_fred_series(
        start_date=start_date, end_date=end_date, series_id="WDTGAL"
    )

    df1 = df1.rename(columns={"WDTGAL": "TGA"})
    df = pd.merge(df, df1, on="observation_date", how="left")

    df = df.set_index("observation_date")

    return df


def fetch_series_list():
    """
    NY Fed Primary Dealer Position Securities List Descriptions for all timeseries data

    Parameters:


    Returns:
        pd.DataFrame: [Date, 증권 종류 ] 형식의 DataFrame
    """

    url = f"https://markets.newyorkfed.org/api/pd/list/timeseries.json"

    params = {}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(
            f"❌ Failed to fetch all rates: {response.status_code}\n{response.text}"
        )

    data = response.json()

    df = pd.DataFrame(data.get("pd", {}).get("timeseries", []))

    rename_dict = {
        "seriesbreak": "Series",
        "keyid": "Key",
        "description": "Description",
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


def fetch_secured_series(rate_type="tgcr", start_date="2000-01-01", end_date="2025-12-31"):
    # secured rate(tgcr, sofr, bgcr)의 금리와 거래량을 각각 받아 날짜로 합침
    rate_type = rate_type.lower()
    base_url = f"https://markets.newyorkfed.org/api/rates/secured/{rate_type}/search.json"

    def fetch_data(query_type):
        params = {"startDate": start_date, "endDate": end_date, "type": query_type}  # 'rate' 또는 'volume'
        r = requests.get(base_url, params=params)
        r.raise_for_status()
        return pd.DataFrame(r.json().get("refRates", []))

    df_rate = fetch_data("rate")
    if df_rate.empty:
        df_rate = pd.DataFrame(columns=["Date", f"{rate_type.upper()}"])
    else:
        df_rate = df_rate[["effectiveDate", "percentRate"]].rename(
            columns={"effectiveDate": "Date", "percentRate": rate_type.upper()}
        )
        df_rate["Date"] = pd.to_datetime(df_rate["Date"])

    df_vol = fetch_data("volume")
    if df_vol.empty:
        df_vol = pd.DataFrame(columns=["Date", f"{rate_type.upper()}_VOLUME"])
    else:
        # API의 거래량 열 이름이 volume → volumeInBillions로 바뀜 (둘 다 받음)
        vol = "volumeInBillions" if "volumeInBillions" in df_vol else "volume"
        df_vol = df_vol[["effectiveDate", vol]].rename(
            columns={"effectiveDate": "Date", vol: f"{rate_type.upper()}_VOLUME"}
        )
        df_vol["Date"] = pd.to_datetime(df_vol["Date"])

    return pd.merge(df_rate, df_vol, on="Date", how="outer").sort_values("Date").reset_index(drop=True)
