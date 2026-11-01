# %% [markdown]
# # 미국 재무부 Fiscal Data API: 국채 경매 결과·예정 경매
# ## file name
# - treasury_auctions_api.py
#
# ## 기능
# - Treasury Securities Auctions Data에서 경매 결과(낙찰액, 응찰자 유형별 금액, 응찰률, 낙찰금리)와 예정 경매를 받는다.
# - 1000건씩 페이지를 넘겨 받는다 (마지막에 나오는 HTTP 오류 메시지는 무시해도 됨).
# - 캐시: `codes/cache/treasury_cache/treasury_auction.<start>.<end>.parquet`, `coming_auction.<start>.<end>.parquet`
#   - 같은 종료일이고 시작일이 더 이른 캐시가 있으면 잘라서 쓴다.
#
# ## 출처
# - https://fiscaldata.treasury.gov (Datasets → Treasury Securities Auctions Data, Upcoming Auctions)
# - API: `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query`,
#   `.../od/upcoming_auctions`
# - API key 필요 없음
#
# ## fetch_securities_auction()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from treasury_auctions_api import fetch_securities_auction, fetch_coming_auction
#
# df = fetch_securities_auction(start_date="2023-01-01", end_date="2026-12-31")
# df = fetch_securities_auction("2023-01-01", "2026-12-31", csv_path="data/treasury_auctions.csv")
# coming = fetch_coming_auction("2026-10-01", "2026-12-31")
# ```
#
# ## parameters
# | Parameter                | Type          | Description                              |
# |--------------------------|---------------|------------------------------------------|
# | `start_date`, `end_date` | `str`         | 경매일(예정 경매는 기록일) 기간 `YYYY-MM-DD` |
# | `use_cache`              | `bool`        | 캐시 사용 (기본 True)                     |
# | `csv_path`               | `str \| None` | 주면 결과를 CSV로도 저장                  |
#
# ## returned columns and values
# `fetch_securities_auction`: API 필드 이름 그대로
#
# | Column | Description |
# |--------|-------------|
# | `record_date`, `auction_date`, `issue_date` | 기록일, 경매일, 발행일 |
# | `security_type`, `security_term` | 국채 종류(Bill/Note/Bond/TIPS/FRN), 만기 (예: `10-Year`) |
# | `total_accepted` | 총 낙찰액 (달러) |
# | `primary_dealer_accepted`, `direct_bidder_accepted`, `indirect_bidder_accepted`, `soma_accepted`, `fima_noncomp_accepted`, `treas_retail_accepted` | 응찰자 유형별 낙찰액 |
# | `direct_bidder_tendered`, `indirect_bidder_tendered` | 응찰액 |
# | `bid_to_cover_ratio` | 응찰률 |
# | `high_yield`, `high_discnt_rate`, `high_investment_rate`, `high_discnt_margin` | 낙찰금리 |
#
# `fetch_coming_auction`: `record_date`, `security_type`, `security_term`, `reopening`, `cusip`, `offering_amt`, `announcemt_date`, `auction_date`, `issue_date`
#
# ## 사용하는 곳
# - `wallstreet/f_treasury_auctions.py`, `wallstreet/f_treasury_bid_to_cover.py`, `wallstreet/treasury_auction_rate.py`, `wallstreet/treasury_auction_recent.py`, `graphs_python_code/f26/f27`
# - 아래 셀부터는 책 원고용 설명이다.

# %% [markdown]
# 미국 재무부 Fiscal Data API에서 Treasury Securities Auctions data를 가져와서 파일로 저장하는 코드를 살펴보자.
# 다른 곳에서 설명한 것은 제외하고 특징적인 사항위주로 설명하였다.
# Markets Data 웹페이지에서 API를 이용할 때 필요한 endpoint, parameter 등에 대한 정보를 자세히 알려주고 있다.
#
# 아래 코드가 '[그림 26] 월별 미국 국채 경매규모'에 활용되었다.
# 먼저 필요한 패키지를 호출한다.
# %%

import os

import pandas as pd
import requests
from cache_def import find_longer_cache, prune_stale_cache, shared_cache_dir

# %% [markdown]
# 국채 경매결과를 호출하는 함수를 정의하는 곳이다. start_date, end_date를 파라미터로 입력한다.
# %%


CACHE_DIR = shared_cache_dir("treasury_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def fetch_securities_auction(start_date, end_date, use_cache=True, csv_path=None):
    df = pd.DataFrame()

    cache_file = os.path.join(
        CACHE_DIR, f"treasury_auction.{start_date}.{end_date}.parquet"
    )

    # 같은 종료일이고 시작일이 더 이른 캐시 (정확히 일치하는 캐시가 없을 때만)
    longer = None
    if use_cache and not os.path.exists(cache_file):
        longer = find_longer_cache(
            CACHE_DIR, start_date, f".{end_date}.parquet", prefix="treasury_auction."
        )

    # 캐시가 있을 때
    if use_cache and os.path.exists(cache_file):
        print(f"🔹 Using cached data for treasury auction on {start_date}.{end_date}")
        df = pd.read_parquet(cache_file)
    elif longer:
        print(f"🔹 Using cached data for treasury auction ({os.path.basename(longer)})")
        df = pd.read_parquet(longer)
        df = df[pd.to_datetime(df["auction_date"]) >= pd.Timestamp(start_date)]
        df = df.reset_index(drop=True)
    else:
        print(f"⚙️ Fetching API data for treasury auction on {start_date}.{end_date}")

        # treasury fiscal data의 Treasury Securities Auctions Data에 접근하는 endpoint를 url에 할당한다.

        url = (
            "https://api.fiscaldata.treasury.gov/services"
            "/api/fiscal_service/v1/accounting/od/auctions_query"
        )
        # %% [markdown]
        # 시작일, 종료일이 필터로 들어가는 곳이다. 필드에 호출하는 자료의 이름이 들어간다. Auctions Data는 상당히 구체적인 정보를 제공한다.
        # 자료 기록일, 경매 실시일, 발행일을 알려주며 발행금액, 발행한 채권의 종류와 만기(term)도 나온다.
        # 다만, 낙찰기관에 대한 구체적 정보가 없고 primary dealer, direct bidder, indirect bidder, soma, fima 등의
        # 그룹별 데이터를 제공한다.
        #
        # 한번에 가져올 수 있는 페이지 크기는 1000줄로 제한되며, 1 페이지 씩 가져온다. 먼 과거부터 자료를 가져오면 호출시간이
        # 오래 걸린다. 2023년부터 최근까지
        # 자료를 가져오면, 2페이지로 끝난다.
        # json 포맷으로 자료를 가저오며,
        # 호출이 끝나면 자동으로 dataframe 형식으로 전환한다.
        # %%
        params = {
            "filter": [f"auction_date:gte:{start_date},auction_date:lte:{end_date}"],
            "fields": "record_date,security_type,security_term,auction_date,issue_date,"
            "primary_dealer_accepted,soma_accepted,"
            "total_accepted,direct_bidder_accepted,"
            "direct_bidder_tendered,indirect_bidder_accepted,"
            "indirect_bidder_tendered,fima_noncomp_accepted,treas_retail_accepted,"
            "bid_to_cover_ratio,high_discnt_rate,high_investment_rate,"
            "high_discnt_margin,high_yield",
            "page[size]": 1000,
            "page[number]": 1,
        }

        all_data = []
        print("데이터 가져오기를 시작합니다...")

        while True:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # 요청 실패 시 예외 발생

                print(
                    f"페이지 {params['page[number]']} 가져오는 중 - 상태 코드: {response.status_code}"
                )
                page_data = response.json().get("data", [])

                if not page_data:
                    print("더 이상 가져올 데이터가 없습니다.")
                    break

                all_data.extend(page_data)
                params["page[number]"] += 1

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP 오류: {http_err}")
                print(f"응답 내용: {response.text}")
                break
            except requests.exceptions.RequestException as req_err:
                print(f"요청 중 오류: {req_err}")
                break

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_parquet(cache_file)
            prune_stale_cache(cache_file)

            df["auction_date"] = pd.to_datetime(df["auction_date"])
            df["issue_date"] = pd.to_datetime(df["issue_date"])
            # 숫자 컬럼 변환 및 단위 조정 (단위: 십억 달러)
            cols_to_convert = [
                "total_accepted",
                "direct_bidder_accepted",
                "indirect_bidder_accepted",
                "primary_dealer_accepted",
                "soma_accepted",
                "fima_noncomp_accepted",
                "treas_retail_accepted",
            ]
            for col in cols_to_convert:
                # convert in Billion Dollars
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # %% [markdown]
    # 자료호출이 끝나면 자료의 처음 5개를 화면에 출력하고 자료를 csv파일로 저장한다.
    # 현재는 csv 파일만 return 하도록 했는데, df를 return해도 된다.
    # %%

    # csv_path를 주면 결과를 CSV 파일로도 저장
    if csv_path:
        os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
        df.to_csv(csv_path, index=False)

    return df


# %% [markdown]
# 함수를 호출할 때의 예시이다.
# 이 함수와 별개의 py 파일에서 호출한다면 먼저 함수를 import 한다.
# 한편 자료를 정상적으로 모두 가져와도 'HTTP 오류가 발생했습니다.'라는 오류 메시지가 뜬다.
# 마지막 자료 호출 이후 한번 더 자료를 호출하면서 나타나는 오류인데 무시하면 된다.
# 중간에 자료를 가져오는 중이라는 메시지가 계속 나왔다면 잘 실행된 것이다.
# output_path에서 지정한 경로에서 csv 파일을 찾아 확인하면 된다.
# ```python
# from treasury_auctions_api import fetch_securities_auction
# fetch_securities_auction(start_date='2023-01-01', end_date='2025-12-31')
# ```
# %%


def fetch_coming_auction(start_date, end_date, use_cache=True):
    df = pd.DataFrame()
    cache_file = os.path.join(
        CACHE_DIR, f"coming_auction.{start_date}.{end_date}.parquet"
    )

    # 캐시가 있을 때
    if use_cache and os.path.exists(cache_file):
        print(
            f"🔹 Using cached data for treasury coming auction on {start_date}.{end_date}"
        )
        df = pd.read_parquet(cache_file)
    else:
        print(
            f"⚙️ Fetching API data for treasury coming auction on {start_date}.{end_date}"
        )

        # treasury fiscal data의 Treasury Securities Auctions Data에 접근하는 endpoint를 url에 할당한다.

        url = (
            "https://api.fiscaldata.treasury.gov/services"
            "/api/fiscal_service/v1/accounting/od/upcoming_auctions"
        )

        params = {
            "filter": [f"record_date:gte:{start_date},record_date:lte:{end_date}"],
            "fields": "record_date,security_type,security_term,"
            "reopening,"
            "cusip,"
            "offering_amt,"
            "announcemt_date,"
            "auction_date,issue_date",
            "page[size]": 1000,
            "page[number]": 1,
        }

        all_data = []
        print("데이터 가져오기를 시작합니다...")

        while True:
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()  # 요청 실패 시 예외 발생

                print(
                    f"페이지 {params['page[number]']} 가져오는 중 - 상태 코드: {response.status_code}"
                )
                page_data = response.json().get("data", [])

                if not page_data:
                    print("더 이상 가져올 데이터가 없습니다.")
                    break

                all_data.extend(page_data)
                params["page[number]"] += 1

            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP 오류: {http_err}")
                print(f"응답 내용: {response.text}")
                break
            except requests.exceptions.RequestException as req_err:
                print(f"요청 중 오류: {req_err}")
                break

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_parquet(cache_file)
            prune_stale_cache(cache_file)
            # 숫자 컬럼 변환 및 단위 조정 (단위: 십억 달러)
            cols_to_convert = [
                "offering_amt",
            ]
            for col in cols_to_convert:
                # convert in Billion Dollars
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.sort_values(by="auction_date")

    return df
