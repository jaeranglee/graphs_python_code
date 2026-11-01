# %% [markdown]
# # FRED(St. Louis Fed) API
# ## file name
# - fred_api.py
#
# ## 기능
# - FRED에서 시계열을 받아 `observation_date`, `<series_id>` DataFrame으로 돌려준다.
# - 캐시: `codes/cache/fred_cache/` parquet. 종료일을 오늘로 주면 하루 한 번만 새로 받고,
#   같은 시리즈·같은 종료일이고 시작일이 더 이른 캐시가 있으면 잘라서 쓴다.
# - ALFRED vintage(발표 시점별) 자료, 캐시 없는 버전도 있다.
#
# ## 출처
# - https://fred.stlouisfed.org (시리즈 ID는 FRED 검색에서 확인)
# - API: `https://api.stlouisfed.org/fred/series/observations`
# - API key: `defs/.env`의 `FRED_API_KEY`
#
# ## fetch_fred_series()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from fred_api import fetch_fred_series   # plot_def의 star import로도 들어옴
#
# df = fetch_fred_series("IORB", start_date="2025-09-01", end_date="2025-09-30")
# #   observation_date  IORB
# # 0       2025-09-01   4.4
#
# vint = fetch_vintage_series("PAYEMS", start_date="2024-01-01", end_date="2026-12-31")
# ```
#
# ## parameters
# | Parameter    | Type   | Description                                   |
# |--------------|--------|-----------------------------------------------|
# | `series_id`  | `str`  | FRED 시리즈 ID (예: `CPIAUCNS`, `IORB`)        |
# | `start_date` | `str`  | 시작일 `YYYY-MM-DD`                            |
# | `end_date`   | `str`  | 종료일 `YYYY-MM-DD`                            |
# | `use_cache`  | `bool` | False면 캐시 무시하고 새로 받음 (기본 True)    |
#
# ## returned columns and values
# | Column             | Type     | Description                       |
# |--------------------|----------|-----------------------------------|
# | `observation_date` | datetime | 관측일                             |
# | `<series_id>`      | float    | 관측값 (FRED의 `.`은 NaN)          |
#
# - `fetch_vintage_series`는 `realtime_start`(그 값이 발표된 날) 열이 더 있다.
#
# ## 그 밖의 함수
# | Function | Description |
# |----------|-------------|
# | `fetch_vintage_series(series_id, start_date, end_date, use_cache=True)` | ALFRED vintage: `observation_date`, `realtime_start`, `<series_id>` |
# | `fetch_fred_series_no_cache(series_id, start_date, end_date)` | 캐시 없이 매번 호출 (결과는 `fetch_fred_series`와 같음) |
# | `fetch_fred_vintage_dates(series_id)` | ALFRED vintage 날짜(발표일) 목록 `["YYYY-MM-DD", …]`, 실패하면 `[]`. 캐시 없음 |
# | `fetch_fred_as_of(series_id, vintage_date, start_date, end_date)` | `vintage_date`에 발표된 그대로의 관측값 목록 `[{"date", "value", …}, …]` (FRED 원 응답). 캐시 없음, 오류는 `requests.HTTPError` |
#
# ## 사용하는 곳
# - 170여 개 스크립트 (모든 폴더). `plot_def.py`가 star import로 `fetch_fred_series`를 넘겨준다.
# - 아래 셀부터는 책 원고용 설명이다.

# %% [markdown]
# 파이썬 코드에 FRED에서 데이터를 호출하는 부분을 포함하면 코드가 길어지고 가독성이 떨어진다.
# FRED 자료를 자주 조회 한다면 함수를 별도 파일로 저장해 놓고 사용하길 권장한다. 코드길이도 짧아지고 호출 형식도 통일할 수 있어서 편하다.
# 그리고 API key를 함수에 포함시켜 놓으면 매번 입력하지 않아도 된다.
# 이 코드는 FRED에서 시계열 데이터를 받아 pandas DataFrame으로 반환하는 함수, def fetch_fred_series()를 fred_api.py라는 별도 파일로 저장한 것이다.
# 이 함수의 사용 방법은 앞에 이미 설명했다. 함수의 내용을 더 자세히 알아보자.
#
# 이 함수의 구성은 다음과 같다. 먼저 필요한 패키지를 불러온다. os, requests, pandas 패키지가 필요하다.
# %%
import os

import pandas as pd
import requests

# %% [markdown]
# 이번에는 API key를 외부파일로 저장해 놓고 호출해서 쓰는 방식을 소개한다.
# 외부파일로 저장해 놓으면 함수 파일을 공유할 때 나의 key를 노출하지 않아도 된다.
# 매번 긴 문자열을 외우거나 복사, 붙여넣기 하지 않아도 된다.
# 서로 다른 기관에서 제공하는 데이터 호출용 API key를 한 곳에 모아 관리할 수 있다.
# .env라는 이름의 텍스트 파일을 만든다.
# 이름은 없고 확장자만 .env로 정의된 파일이다.
# 노트패드나 PyCharm 같은 에디터로 FRED_API_KEY = "aaabbbcccdddeeefff12345"라고 기록하고 파일 이름을 .env 로 해서 저장한다.
# load_dotenv 패키지를 불러온 다음 .env 파일에서 FRED_API_KEY를 가져온다.
# key를 외부파일로 저장하지 않으려면 api_key = os.getenv("FRED_API_KEY") 대신
# api_key = "aaabbbcccdddeeefff12345"와 같이 사용한다.
# 키를 직접 할당하면 from dotenv import load_dotenv를 지우고, load_dotenv()도 삭제한다.
# %%
import os

# kor_birth_marridge.py
import sys

from dotenv import find_dotenv, load_dotenv
from pathlib import Path
from cache_def import find_longer_cache, prune_stale_cache, shared_cache_dir

load_dotenv(Path(__file__).resolve().parent / ".env")
api_key = os.getenv("FRED_API_KEY")


# %% [markdown]
# FRED에서 시계열 데이터를 받아 pandas DataFrame으로 반환하는 함수이다.
# 필요한 파라미터 3개를 넣어야 한다. series_id는 가져오려는 시계열 자료의 ID이다.
# FRED 홈페이지를 검색해서 찾아야 한다. 예를 들면 'CPIAUCNS'는 계절조정을 하지 않은 소비자물가지수의 ID이다.
# start_date는 조회 시작일, end_date는 자료의 마지막 일자이다.
# YYYY-MM-DD 형식으로 적어야 한다. start_date, end_date, series_id는 모두 문자열이며 작은따옴표, 또는
# 큰따옴표 안에 적는다.
#
# url은 FRED API의 주소(endpoint)이며, requests 패키지가 자료를 json 형식으로 불러온다.
# 우리가 필요한 자료는 data['observation'] 항목안에 들어있고, 그것을 골라서 df라는 이름의
# dataframe에 할당했다. 날짜는 'observation_date'라는 이름의 열에 넣었고,
# 조회한 시계열자료의 ID인 series_id를 호출한 자료의 이름으로 삼았다.
# 'observation_date'는 날짜 형식으로 변환하며, 호출한 자료는 숫자형식으로 변환한 다음
# dataframe 형식으로 반환한다.
# %%

CACHE_DIR = shared_cache_dir("fred_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def fetch_fred_series(series_id, start_date, end_date, use_cache=True):

    cache_file = os.path.join(CACHE_DIR, f"{series_id}.{start_date}.{end_date}.parquet")

    # 같은 날 받은 더 긴 기간의 캐시가 있으면 잘라서 사용 (API 호출 생략)
    if use_cache and not os.path.exists(cache_file):
        longer = find_longer_cache(
            CACHE_DIR, start_date, f".{end_date}.parquet", prefix=f"{series_id}."
        )
        if longer:
            print(f"🔹 Using cached data for {series_id} ({os.path.basename(longer)})")
            df = pd.read_parquet(longer)
            df = df[df["observation_date"] >= pd.Timestamp(str(start_date))]
            return df[["observation_date", series_id]].reset_index(drop=True)

    # 캐시가 있을 때
    if use_cache and os.path.exists(cache_file):
        print(f"🔹 Using cached data for {series_id}")
        df = pd.read_parquet(cache_file)
    else:
        print(f"⚙️ Fetching API data for {series_id}")

        if not api_key:
            raise ValueError("FRED_API_KEY가 .env에 없습니다.")

        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date,
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "observations" not in data:
            raise ValueError(
                f"FRED 응답 오류: " f"{data.get('message', 'Unknown error')}"
            )
        df = pd.DataFrame(data["observations"])

    df["observation_date"] = pd.to_datetime(df["date"])
    df[series_id] = pd.to_numeric(df["value"], errors="coerce")
    df.to_parquet(cache_file)
    prune_stale_cache(cache_file)

    return df[["observation_date", series_id]]


# %% [markdown]
# 예시를 위해 FRED에서 'IORB'라는 ID를 가진 자료를 불러와서 iorb라는 변수에 할당하고 출력해보자.
# 자료의 시작은 2025-09-01이고 자료의 끝은 2025-09-30이다. 먼저 함수를 import 해아하지만 지금 함수가
# 같은 코드 안에 들어 있어서 import 과정을 생략할 수 있었다. 만약 fetch_fred_series() 함수가 다른 파일에
# 저장되어 있다면, 아래와 같이 import 문을 앞에 써야 한다.
# ```python
# from fred_api import fetch_fred_series
# iorb = fetch_fred_series('IORB',
#        start_date='2025-09-01', end_date='2025-09-30')
# ```
#
# 확인을 위해 처음 5개의 자료만 출력한다. 첫 번째 열의 이름은 'observation_date'이고, 두 번째 열의 이름은 'IORB'가 되었다.
# 모든 줄에 인덱스가 있다. 첫 번째 줄의 인덱스가 0, 다음이 1, 이어서 순서대로 나가고 있다.
# ```python
# print(iorb.head())
#   observation_date  IORB
# 0       2025-09-01   4.4
# 1       2025-09-02   4.4
# 2       2025-09-03   4.4
# 3       2025-09-04   4.4
# 4       2025-09-05   4.4
# ```
# %%


# %% [markdown]
# # FRED Vintage data fetch
# %%
def fetch_vintage_series(series_id, start_date, end_date, use_cache=True):

    cache_file = os.path.join(
        CACHE_DIR, f"{series_id}vintage.{start_date}.{end_date}.parquet"
    )

    # 캐시가 있을 때
    if use_cache and os.path.exists(cache_file):
        print(f"🔹 Using cached data for {series_id}")
        df = pd.read_parquet(cache_file)
    else:
        print(f"⚙️ Fetching API data for {series_id}")

        if not api_key:
            raise ValueError("FRED_API_KEY가 .env에 없습니다.")

        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "realtime_start": start_date,
            "realtime_end": end_date,
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            print("❌ FRED raw response:")
            print(response.text)
            response.raise_for_status()

        data = response.json()

        if "observations" not in data:
            raise ValueError(
                f"FRED 응답 오류: " f"{data.get('message', 'Unknown error')}"
            )
        df = pd.DataFrame(data["observations"])

    df["observation_date"] = pd.to_datetime(df["date"])
    df["realtime_start"] = pd.to_datetime(df["realtime_start"])
    df[series_id] = pd.to_numeric(df["value"], errors="coerce")
    df.to_parquet(cache_file)
    prune_stale_cache(cache_file)

    return df[["observation_date", "realtime_start", series_id]]


# %% [markdown]
# # 캐시 없는 버전 (graphs_python_code, us_korea_trade에서 쓰던 fred_api.py)
# 위의 fetch_fred_series()와 같은 결과를 반환하지만 fred_cache/에 저장하지 않고 매번 FRED API를 호출한다.
# 두 함수 이름이 같으면 뒤의 것이 앞의 것을 덮어쓰므로 이름을 fetch_fred_series_no_cache로 바꿨다.
#
# FRED에서 시계열 데이터를 받아 pandas DataFrame으로 반환하는 함수이다.
# 필요한 파라미터 3개를 넣어야 한다. series_id는 가져오려는 시계열 자료의 ID이다.
# FRED 홈페이지를 검색해서 찾아야 한다. 예를 들면 'CPIAUCNS'는 계절조정을 하지 않은 소비자물가지수의 ID이다.
# start_date는 조회 시작일, end_date는 자료의 마지막 일자이다.
# YYYY-MM-DD 형식으로 적어야 한다. start_date, end_date, series_id는 모두 문자열이며 작은따옴표, 또는
# 큰따옴표 안에 적는다.
# url은 FRED API의 주소(endpoint)이며, requests 패키지가 자료를 json 형식으로 불러온다.
# 우리가 필요한 자료는 data['observation'] 항목안에 들어있고, 그것을 골라서 df라는 이름의
# dataframe에 할당했다. 날짜는 'observation_date'라는 이름의 열에 넣었고,
# 조회한 시계열자료의 ID인 series_id를 호출한 자료의 이름으로 삼았다.
# 'observation_date'는 날짜 형식으로 변환하며, 호출한 자료는 숫자형식으로 변환한 다음
# dataframe 형식으로 반환한다.


# %%
def fetch_fred_series_no_cache(series_id, start_date, end_date):

    if not api_key:
        raise ValueError("FRED_API_KEY가 .env에 없습니다.")

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "observations" not in data:
        raise ValueError(f"FRED 응답 오류: " f"{data.get('message', 'Unknown error')}")

    df = pd.DataFrame(data["observations"])
    df["observation_date"] = pd.to_datetime(df["date"])
    df[series_id] = pd.to_numeric(df["value"], errors="coerce")

    return df[["observation_date", series_id]]


# %% [markdown]
# 예시를 위해 FRED에서 'IORB'라는 ID를 가진 자료를 불러와서 iorb라는 변수에 할당하고 출력해보자.
# ```python
# from fred_api import fetch_fred_series_no_cache
#
# iorb = fetch_fred_series_no_cache('IORB',
#     start_date='2025-09-01', end_date='2025-09-30')
# print(iorb.head())
#   observation_date  IORB
# 0       2025-09-01   4.4
# 1       2025-09-02   4.4
# 2       2025-09-03   4.4
# 3       2025-09-04   4.4
# 4       2025-09-05   4.4
# ```


# %% [markdown]
# # FRED vintage 날짜와 특정 발표 시점의 값 (graphs_python_code/nfp_revision.py에서 옮김)
# 고용지표처럼 발표 뒤 수정되는 자료는 "언제 발표된 값인가"에 따라 값이 다르다.
# fetch_fred_vintage_dates()는 그 시리즈가 발표(수정)된 날짜를 모두 돌려주고,
# fetch_fred_as_of()는 그중 한 날짜(vintage_date)에 발표된 그대로의 관측값을 돌려준다.
# 요청이 많아지므로(월마다 3번) 캐시하지 않는다.


# %%
def fetch_fred_vintage_dates(series_id):

    url = "https://api.stlouisfed.org/fred/series/vintagedates"
    params = {"series_id": series_id, "api_key": api_key, "file_type": "json"}
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json().get("vintage_dates", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching vintage dates: {e}")
        return []


def fetch_fred_as_of(series_id, vintage_date, start_date, end_date):

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "realtime_start": vintage_date,
        "realtime_end": vintage_date,
        "observation_start": start_date,
        "observation_end": end_date,
    }
    r = requests.get("https://api.stlouisfed.org/fred/series/observations", params=params)
    r.raise_for_status()
    return r.json().get("observations", [])
