# %% [markdown]
# # 한국은행 ECOS Open API
# ## file name
# - bok_ecos_api.py
#
# ## 기능
# - 한국은행 경제통계시스템(ECOS) StatisticSearch API에서 시계열 하나를 받아 `Date`, `Value` DataFrame으로 돌려준다.
# - 캐시: `codes/cache/ecos_cache/<stat_name>_<시작>_<종료>_<코드…>_<cycle>.csv`
#   - 같은 시리즈(코드·주기)·같은 종료일이고 시작일이 더 이른 캐시가 있으면 잘라서 쓴다 (`stat_name`은 비교 안 함).
#   - 종료일을 오늘로 주면 하루 한 번만 새로 받는다.
#
# ## 출처
# - https://ecos.bok.or.kr (통계표 코드·항목 코드는 ECOS 개발 가이드/통계 검색에서 확인)
# - API: `http://ecos.bok.or.kr/api/StatisticSearch/{API_KEY}/xml/en/1/{건수}/{stat_code}/{cycle}/{시작}/{종료}/{item_code}[/{item_code2}][/{item_code3}]`
# - API key: `defs/.env`의 `ECOS_API_KEY`
#
# ## fetch_ecos_series()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from bok_ecos_api import *
#
# series_list = [
#     # [이름, 통계표 코드, 항목코드1, 항목코드2, 항목코드3, 주기]
#     ["달러", "731Y003", "0000003", "", "", "D"],       # 원/달러 환율(종가)
#     ["KGB 1Y", "817Y002", "010190000", "", "", "D"],   # 국고채 1년
# ]
# dfs = {}
# for name, stat_code, item_code, item_code2, item_code3, cycle in series_list:
#     df = fetch_ecos_series(name, stat_code, item_code, item_code2, item_code3,
#                            cycle, start_date="2007-01-01", end_date="2026-12-31")
#     dfs[name] = df.rename(columns={"Value": name})
# ```
#
# ## parameters
# | Parameter    | Type   | Description                                          |
# |--------------|--------|------------------------------------------------------|
# | `stat_name`  | `str`  | 시리즈 이름 (캐시 파일 이름·출력용)                   |
# | `stat_code`  | `str`  | 통계표 코드 (예: `731Y003`)                           |
# | `item_code`  | `str`  | 항목코드1                                            |
# | `item_code2` | `str`  | 항목코드2 (없으면 `""` 또는 None)                     |
# | `item_code3` | `str`  | 항목코드3 (없으면 `""` 또는 None)                     |
# | `cycle`      | `str`  | 주기 `D`/`M`/`Q`/`A`                                  |
# | `start_date` | `str`  | 시작일 `YYYY-MM-DD`                                  |
# | `end_date`   | `str`  | 종료일 `YYYY-MM-DD`                                  |
# | `cache_dir`  | `str`  | 캐시 폴더 이름 (기본 `ecos_cache`)                    |
# | `use_cache`  | `bool` | False면 캐시 무시하고 새로 받음 (기본 True)           |
#
# ## returned columns and values
# | Column  | Type     | Description                                                  |
# |---------|----------|--------------------------------------------------------------|
# | `Date`  | datetime | 관측일. 월·분기·연 자료는 기간 첫날 (예: 2025Q2 → 2025-04-01) |
# | `Value` | float    | 관측값 (숫자로 바꿀 수 없으면 NaN)                            |
#
# - 자료가 없거나 HTTP 오류면 빈 DataFrame을 돌려준다.
#
# ## 그 밖의 함수
# - `convert_date_format(date_str, cycle)`: `YYYY-MM-DD`를 ECOS 기간 형식(`20250101`, `202501`, `2025Q1`, `2025`)으로 바꾼다.
# - `calculate_length(start_date, end_date, cycle)`: 요청할 자료 건수를 계산한다.
#
# ## 사용하는 곳
# - 100여 개 스크립트 (`exchange/`, `gold/`, `macro_econ/`, `wallstreet/` 등). 예: `gold/kor_swaprate.py`, `wallstreet/f_real_dollar_and_gold.py`

# %%
# -----------------------------------------------
# Fetch from ECOS
# -----------------------------------------------
# BOK Ecos OPEN API 에서 데이터 가져오는 루틴
# 다른 곳에서 호출하는 법
# 아래와 같이 호출
# 사용사례 참고 : f_real_dollar_and_gold.py
# 아래사례 참고
# ECOS_API_KEY: codes/defs/.env 파일에 포함되어 있음 (모든 폴더 공용)

import xml.etree.ElementTree as ET
from dotenv import find_dotenv, load_dotenv
from pathlib import Path
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dotenv import find_dotenv, load_dotenv

import requests
import pandas as pd
import sys
import os
from cache_def import (
    find_longer_cache,
    period_start,
    prune_stale_cache,
    shared_cache_dir,
)

# add parent directory (where "common" folder lives)
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "sample_codes"))
# 🔑 Load API key
load_dotenv(Path(__file__).resolve().parent / ".env")
API_KEY_ECOS = os.getenv("ECOS_API_KEY")


def convert_date_format(date_str, cycle):

    print(f"🧪 convert_date_format called with: date_str={date_str}, cycle={cycle}")

    if not date_str:
        raise ValueError("date_str is empty. Please provide a valid date string.")
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    # 이후 cycle에 따른 포맷 변환 로직

    if cycle == "D":
        return dt.strftime("%Y%m%d")
    elif cycle == "M":
        return dt.strftime("%Y%m")
    elif cycle == "Q":
        quarter = (dt.month - 1) // 3 + 1
        return f"{dt.year}Q{quarter}"
    elif cycle == "A":
        return str(dt.year)
    else:
        raise ValueError("Unsupported cycle type. Use 'D', 'M', 'Q', or 'A'.")


def calculate_length(start_date, end_date, cycle):
    start = datetime.strptime(
        start_date, "%Y-%m-%d" if cycle in ["M", "Q", "A"] else "%Y-%m-%d"
    )
    end = datetime.strptime(
        end_date, "%Y-%m-%d" if cycle in ["M", "Q", "A"] else "%Y-%m-%d"
    )

    if cycle == "D":
        diff = (end - start).days + 1
    elif cycle == "M":
        diff = (end.year - start.year) * 12 + end.month - start.month + 1
    elif cycle == "Q":
        diff = ((end.year - start.year) * 12 + end.month - start.month) // 3 + 1
    elif cycle == "A":
        diff = end.year - start.year + 1
    else:
        raise ValueError("Unsupported cycle type. Use 'D', 'M', 'Q', or 'A'.")
    return diff


def fetch_ecos_series(
    stat_name,
    stat_code,
    item_code,
    item_code2,
    item_code3,
    cycle,
    start_date,
    end_date,
    cache_dir="ecos_cache",
    use_cache=True,
):
    """
    BOK ECOS API에서 시계열 데이터를 가져오는 함수.
    - stat_name: 시계열 이름
    - stat_code: 통계코드
    - item_code: 항목코드1
    - cycle: 'D', 'M', 'Q', 'A'
    - start_date, end_date: 'YYYY-MM-DD'
    - item_code2: 항목코드2 (없으면 None)
    """

    cache_dir = shared_cache_dir(cache_dir)

    # Convert dates
    start_fmt = convert_date_format(start_date, cycle)
    end_fmt = convert_date_format(end_date, cycle)

    import re

    def sanitize_filename(name: str) -> str:
        # 파일명에 허용되지 않는 문자 제거
        return re.sub(r'[\\/:*?"<>|]', "_", name)

    cache_path = os.path.join(
        cache_dir,
        sanitize_filename(
            f"{stat_name}_{start_fmt}_{end_fmt}_{stat_code}_{item_code}_{item_code2}_{item_code3}_{cycle}.csv"
        ),
    )

    print("CACHE PATH:", cache_path)
    print("CACHE EXISTS:", os.path.exists(cache_path))

    if use_cache and os.path.exists(cache_path):
        print(f"📥 Loaded from cache: {stat_name}")
        return pd.read_csv(cache_path, parse_dates=["Date"])

    # 같은 시리즈(코드·주기)·같은 종료일이고 시작일이 더 이른 캐시가 있으면 잘라서 사용
    # stat_name은 스크립트마다 다를 수 있어 비교하지 않음
    if use_cache:
        suffix = sanitize_filename(
            f"_{end_fmt}_{stat_code}_{item_code}_{item_code2}_{item_code3}_{cycle}.csv"
        )
        longer = find_longer_cache(cache_dir, start_fmt, suffix)
        if longer:
            print(f"📥 Loaded from cache: {stat_name} ({os.path.basename(longer)})")
            df = pd.read_csv(longer, parse_dates=["Date"])
            # 월·분기·연 자료의 Date는 기간 첫날이므로 시작일이 속한 기간의 첫날로 자름
            start_ts = period_start(start_date, cycle)
            return df[df["Date"] >= start_ts].reset_index(drop=True)

    length = calculate_length(start_date, end_date, cycle)

    url = [
        f"http://ecos.bok.or.kr/api/StatisticSearch/{API_KEY_ECOS}/xml/en/1/{length}",
        stat_code,
        cycle,
        start_fmt,
        end_fmt,
        item_code,
    ]

    if item_code2:  # 있을 때만 추가
        url.append(item_code2)
    if item_code3:  # 있을 때만 추가
        url.append(item_code3)

    url = "/".join(url)

    print("🔗 URL:", url.replace(API_KEY_ECOS, "***"))  # 👉 디버깅용 출력 (API 키는 가림)

    response = requests.get(url)
    # print(response.text)
    if response.status_code != 200:
        print("❌ HTTP error:", response.status_code)
        return pd.DataFrame()

    root = ET.fromstring(response.content)
    rows = root.findall(".//row")

    if not rows:
        print(
            f"❌ No data found for {stat_name} - item_code: {item_code}, item_code2: {item_code2}, item_code3: {item_code3}"
        )
        return pd.DataFrame()

    data = []
    for row in rows:
        time = row.find("TIME").text
        value = row.find("DATA_VALUE").text
        try:
            data.append({"Date": time, "Value": value})
        except ValueError:
            continue
    df = pd.DataFrame(data)

    # 날짜 형식 파싱
    if cycle == "D":
        df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
    elif cycle == "M":
        df["Date"] = pd.to_datetime(df["Date"], format="%Y%m")
    #    elif cycle == "Q":
    #        df["Date"] = pd.to_datetime(df["Date"].str.replace("Q", "-Q"), format="%Y%Q")
    elif cycle == "Q":
        df["Date"] = df["Date"].apply(
            lambda x: pd.Timestamp(
                year=int(x[:4]), month=(int(x[-1]) - 1) * 3 + 1, day=1
            )
        )

    elif cycle == "A":
        df["Date"] = pd.to_datetime(df["Date"], format="%Y")

    # 숫자 변환 (문자 → float, 변환 안 되면 NaN)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df.to_csv(cache_path, index=False)
    prune_stale_cache(cache_path)
    print(f"✅ Fetched and cached: {stat_name}")
    return df


# sample = f"http://ecos.bok.or.kr/api/StatisticTableList/{API_KEY_ECOS}/json/kr/1/10/281Y001"
# res = requests.get(sample); print(res.text)
