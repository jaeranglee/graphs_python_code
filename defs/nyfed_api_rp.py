# %% [markdown]
# # New York Fed Markets Data API: Repo 공개시장조작
# ## file name
# - nyfed_api_rp.py
#
# ## 기능
# - 뉴욕 연준 Repo(RP) 운영 결과(한도, 응찰액, 낙찰액)를 받는다.
# - 캐시: `codes/cache/nyfed_cache/rp_vol_<start>_<end>.<term>.parquet`
#   - 같은 종료일·만기이고 시작일이 더 이른 캐시가 있으면 잘라서 쓴다.
#
# ## 출처
# - https://markets.newyorkfed.org/static/docs/markets-api.html
# - API: `https://markets.newyorkfed.org/api/rp/results/search.json?operationTypes=Repo&term={term}`
# - API key 필요 없음
#
# ## fetch_rp_operation()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from nyfed_api_rp import fetch_rp_operation
#
# df_rp = fetch_rp_operation(start_date="2025-01-01", end_date="2026-10-30", term="overnight")
# ```
#
# ## parameters
# | Parameter    | Type   | Description                              |
# |--------------|--------|------------------------------------------|
# | `start_date` | `str`  | 시작일 `YYYY-MM-DD`                       |
# | `end_date`   | `str`  | 종료일 `YYYY-MM-DD`                       |
# | `term`       | `str`  | `overnight`(기본) 또는 `term`             |
# | `use_cache`  | `bool` | 캐시 사용 (기본 True)                     |
#
# ## returned columns and values
# 날짜 오름차순
#
# | Column      | Type     | Description                       |
# |-------------|----------|-----------------------------------|
# | `Date`      | datetime | 운영일                             |
# | `Limit`     | float    | 운영 한도 (달러)                   |
# | `Sumbitted` | float    | 응찰액 (달러; 열 이름 철자 그대로)  |
# | `Accepted`  | float    | 낙찰액 (달러)                      |
# | `Type`      | str      | 운영 종류 (`Repo`)                 |
#
# ## 사용하는 곳
# - `wallstreet/f_rp_vol.py`, `wallstreet/rrp_rp_vol_recent.py`, `graphs_python_code/f40_rp_vol.py`
# %%
import os

import pandas as pd
import requests
from cache_def import find_longer_cache, prune_stale_cache, shared_cache_dir

CACHE_DIR = shared_cache_dir("nyfed_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def fetch_rp_operation(start_date, end_date, term="overnight", use_cache=True):

    cache_file = os.path.join(
        CACHE_DIR, f"rp_vol_{start_date}_{end_date}.{term}.parquet"
    )

    # 같은 종료일·만기이고 시작일이 더 이른 캐시가 있으면 잘라서 사용
    if use_cache and not os.path.exists(cache_file):
        longer = find_longer_cache(
            CACHE_DIR, start_date, f"_{end_date}.{term}.parquet", prefix="rp_vol_"
        )
        if longer:
            print(f"🔹 Using cached data for rp operation ({os.path.basename(longer)})")
            df = pd.read_parquet(longer)
            return df[df["Date"] >= pd.Timestamp(start_date)].reset_index(drop=True)

    # 캐시가 있을 때
    if use_cache and os.path.exists(cache_file):
        print(f"🔹 Using cached data for rp operation")
        df = pd.read_parquet(cache_file)
    else:
        print(f"⚙️ Fetching API data for rp operation")

        url = (
            f"https://markets.newyorkfed.org/api/rp/results/search.json?"
            # f"startDate={start_date}&endDate={end_date}&operationTypes=Repo")
            f"startDate={start_date}&endDate={end_date}&operationTypes=Repo&term={term}"
        )

        params = {"startDate": "start_date", "endDate": "end_date"}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            raise RuntimeError(
                f"Failed to fetch all: {response.status_code}\n{response.text}"
            )

        data = response.json()
        records = data.get("repo", {}).get("operations", [])

        df = pd.DataFrame(records)

        if df.empty:
            return pd.DataFrame(columns=["Date", "Type"])

        df["operationDate"] = pd.to_datetime(df["operationDate"])
        df = df[
            [
                "operationDate",
                "operationLimit",
                "totalAmtSubmitted",
                "totalAmtAccepted",
                "operationType",
            ]
        ].rename(
            columns={
                "operationDate": "Date",
                "operationLimit": "Limit",
                "totalAmtSubmitted": "Sumbitted",
                "totalAmtAccepted": "Accepted",
                "operationType": "Type",
                "term": "Term",
            }
        )
        df["Date"] = pd.to_datetime(df["Date"]).copy()
        df = df.sort_values("Date", ascending=True)
    print(df.tail())
    df.to_parquet(cache_file)
    prune_stale_cache(cache_file)

    return df
