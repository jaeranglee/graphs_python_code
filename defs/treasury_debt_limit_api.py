# %% [markdown]
# # 미국 재무부 Fiscal Data: 부채한도 대상 국가부채 (DTS Debt Subject to Limit)
# ## file name
# - treasury_debt_limit_api.py
#
# ## 기능
# - Daily Treasury Statement의 Debt Subject to Limit 표에서 부채한도·한도 대상 부채 잔액을 일별로 가져온다.
# - API로 직접 받거나(`fetch_debt_limit`, 여러 페이지라 오래 걸림), 내려받은 JSON/CSV 파일을 읽는다.
# - 캐시 없음
#
# ## 출처
# - https://fiscaldata.treasury.gov (Datasets → Daily Treasury Statement → Debt Subject to Limit)
# - API: `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/debt_subject_to_limit`
# - API key 필요 없음
#
# ## fetch_debt_limit()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from treasury_debt_limit_api import *
#
# df = fetch_debt_limit(start_date="2015-01-01", end_date="2026-12-31")             # API (느림)
# df = fetch_debt_limit_json("2015-01-01", "2026-12-31", base_url="data/DTS_DebtLimit.json")
# df = fetch_debt_limit_cvs("2015-01-01", "2026-12-31", file_path="data/DTS_DebtLimit.csv")
# ```
#
# ## parameters
# | Parameter                | Type  | Description                                |
# |--------------------------|-------|--------------------------------------------|
# | `start_date`, `end_date` | `str` | 기간 `YYYY-MM-DD`                           |
# | `base_url`               | `str` | (`_json`) 내려받은 JSON 파일 경로            |
# | `file_path`              | `str` | (`_cvs`) 내려받은 CSV 파일 경로              |
#
# ## returned columns and values
# | Column                  | Type     | Description                                  |
# |-------------------------|----------|----------------------------------------------|
# | `Record Date`           | datetime | 기준일                                        |
# | `Debt Category`         | str      | 항목 (부채한도, 한도 대상 부채 등)             |
# | `Closing Balance Today` | float    | 당일 기말 잔액                                |
#
# ## 사용하는 곳
# - `wallstreet/f_public_debt.py`, `wallstreet/f_public_debt_2023.py`, `graphs_python_code/f34_public_debt.py`
# %%

import json
import platform

import pandas as pd
import requests


def fetch_debt_limit(start_date, end_date):
    """
    Fiscaldata.treasury 에서 데이터을 직접 최신 자료로 모두 가져와 병합한 DataFrame 반환.
    시간이 많이 걸림.
    한 페이지로 가져올 수 있는 자료 수 제한이 있기 때문에 여러번 가져와서 합치기 때문
    """

    base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/debt_subject_to_limit"

    params = {
        "filter": f"record_date:gte:{start_date},record_date:lte:{end_date}",
        "sort": "-record_date",
        "fields": "record_date,debt_catg,close_today_bal",
        "format": "json",
        "page[size]": 1000,
        "page[number]": 1,
    }

    all_data = []

    while True:
        response = requests.get(base_url, params=params)
        print(
            f"Fetching page {params['page[number]']} - Status code: {response.status_code}"
        )
        if response.status_code != 200:
            break

        page_data = response.json().get("data", [])
        if not page_data:
            break

        all_data.extend(page_data)
        params["page[number]"] += 1

    df = pd.DataFrame(all_data)

    df["record_date"] = pd.to_datetime(df["record_date"])
    df = df.rename(
        columns={
            "record_date": "Record Date",
            "debt_catg": "Debt Category",
            "close_today_bal": "Closing Balance Today",
        }
    )

    df["Closing Balance Today"] = pd.to_numeric(
        df["Closing Balance Today"], errors="coerce"
    )

    return df


# %% [markdown]
# 데이터를 한번에 json 으로 받은 다음 \data 디렉토리에 저장후 추출
# fetch_debt_limit 으로 받으면 여러 번 나눠 받기 때문에 시간이 오래 걸림
# ## parameters
# | Parameter    | Type  | Description                               |
# |--------------|-------|-------------------------------------------|
# | `start_date` | `str` | start date, 'YYYY-MM-DD'                  |
# | `end_date`   | `str` | end date, 'YYYY-MM-DD'                    |
# | `base_url`   | `str` | file path and downloaded json file name   |
# ## Returns
#  df=df[['Record Date', 'Debt Category', 'Closing Balance Today']]
# ## Example
# ```phyton
# print(fetch_debt_limit_json().info())
# ```
# %%


def fetch_debt_limit_json(start_date, end_date, base_url):

    data = pd.read_json(base_url)
    # Expand the list of dicts inside "data"
    df = pd.json_normalize(data.get("data", []))

    print(df.head())

    df["record_date"] = pd.to_datetime(df["record_date"])
    df = df.rename(
        columns={
            "record_date": "Record Date",
            "debt_catg": "Debt Category",
            "close_today_bal": "Closing Balance Today",
        }
    )

    df["Closing Balance Today"] = pd.to_numeric(
        df["Closing Balance Today"], errors="coerce"
    )

    df = df[(df["Record Date"] >= start_date) & (df["Record Date"] <= end_date)]
    df = df[["Record Date", "Debt Category", "Closing Balance Today"]]
    return df


# %% [markdown]
# 데이터를 한번에 csv 로 받은 다음 \data 디렉토리에 저장후 추출
# fetch_debt_limit 으로 받으면 여러 번 나눠 받기 때문에 시간이 오래 걸림
# ## Example
# ```phyton
# print(fetch_debt_limit_csv().info())
# ```
# %%


def fetch_debt_limit_cvs(start_date, end_date, file_path):
    na_vals = ["null", "NULL", "Null", " null", "null "]
    # CSV 파일 불러오기
    df = pd.read_csv(file_path, na_values=na_vals)

    # 날짜를 datetime 형식으로 변환
    df["Record Date"] = pd.to_datetime(df["Record Date"])

    # Filter for
    df = df[(df["Record Date"] >= start_date)].copy()
    df = df[(df["Record Date"] <= end_date)].copy()

    return df
