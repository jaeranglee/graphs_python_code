# %% [markdown]
# # IMF Data SDMX 2.1 API
# ## file name
# - imf_api.py
#
# ## 기능
# - IMF Data(2025년 개편된 api.imf.org) SDMX 2.1 API에서 시계열을 받아 DataFrame으로 돌려준다.
# - 범용 함수 `fetch_imf_data()`와 데이터셋 전용 함수(COFER, IL 금보유, WPCPER 암호화폐 환율)가 있다.
# - 캐시: `codes/cache/imf_cache/` parquet. 같은 시리즈이고 시작일이 더 이른 캐시가 있으면 잘라서 쓴다.
#
# ## 출처
# - https://data.imf.org (DATASET → API에서 dataset id·key 형식 확인)
# - API: `https://api.imf.org/external/sdmx/2.1/data/{data_set}/{key}`
# - API key 필요 없음
#
# ## fetch_imf_data()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from imf_api import *
#
# # COFER: 달러 표시 외환보유액(배분분) 중 USD, 분기
# df = fetch_imf_data(
#     data_set="IMF.STA,COFER",
#     country_id="G001",              # 전세계
#     indicator_id="AFXRA.CI_USD",
#     start_period="1999-Q1",
#     end_period="2025-Q4",
#     cycle="Q",
#     unit_id="NV_USD",
# )
# # WEO: 1인당 GDP, 연간 (unit_id 없는 dataset)
# df = fetch_imf_data("IMF.RES,WEO", "KOR", "NGDPDPC", "1980", "2030", cycle="A")
# ```
#
# ## parameters (fetch_imf_data)
# | Parameter      | Type          | Description                                           |
# |----------------|---------------|-------------------------------------------------------|
# | `data_set`     | `str`         | dataset id (예: `IMF.STA,COFER`, `IMF.STA,IL`, `IMF.RES,WEO`) |
# | `country_id`   | `str`         | 국가 코드 (예: `KOR`, `G001` = 전세계)                 |
# | `indicator_id` | `str`         | 지표 코드                                              |
# | `start_period`, `end_period` | `str` | 기간 (`1999-Q1`, `2025`, `2020-01-01` 등)       |
# | `cycle`        | `str`         | 주기 `A`/`Q`/`M`                                       |
# | `use_cache`    | `bool`        | 캐시 사용 (기본 True)                                  |
# | `unit_id`      | `str \| None` | 단위 코드 (예: `NV_USD`, `XDR`). 없으면 key에서 빠짐   |
#
# - key 형식: `country.indicator.unit.cycle` (unit 없으면 `country.indicator.cycle`), WPCPER는 `currency.country.indicator.cycle`
#
# ## returned columns and values
# | Column      | Type     | Description                               |
# |-------------|----------|-------------------------------------------|
# | `Date`      | datetime | 기간 첫날 (2025-Q2 → 2025-04-01)           |
# | `COUNTRY`   | str      | 국가 코드                                  |
# | `Indicator` | str      | 지표 코드                                  |
# | `CURRENCY`  | str      | 단위 코드 (unit_id를 준 경우에만)          |
# | `OBS_VALUE` | float    | 관측값                                     |
#
# ## 그 밖의 함수
# | Function | Returns |
# |----------|---------|
# | `fetch_cofer_data(currency_code, param, start_period, end_period, use_cache=True)` | COFER 통화별 외환보유액: `Date`, `<param>` (예: `NV_USD`, `SHRO_PT`) |
# | `fetch_gold_data(country_id, indicator_id, unit_id, start_period, end_period, use_cache=True)` | IL 금보유: `Date`, `<country_id>`, `<indicator_id>`, `OBS_VALUE` |
# | `fetch_imf_crypto_data(data_set, indicator_id, unit_id, start_period, end_period, cycle, use_cache=True)` | WPCPER: `Date`, `COUNTRY`, `CURRENCY`, `Indicator`, `OBS_VALUE` |
# | `convert_period_to_date(period_str)` | `2025-Q2`, `2025-M04` 등을 `YYYY-MM-01` 문자열로 |
#
# ## 사용하는 곳
# - 약 30개 스크립트. 예: `wallstreet/f_reserve.py`, `wallstreet/f_gold_reserve.py`, `gold/gold_all_countries.py`, `gold/imf_gdp_per_capita.py`, `gold/crypto_based_exrate_api.py`
# - 아래 셀부터는 책 원고용 설명이다.

# %% [markdown]
# 코드를 설명하기 전에 IMF Data에서 API로 자료를 fetch하기 위한 기본적 준비사항을 알아보자.
# 우선 IMF Data 홈페이지에서 회원가입을 하는 것을 권장한다.
# Api key는 요구하지 않지만 사용자로 가입하고 로그인해야 API 이용에 필요한 세부 내용을 열람할 수 있다. 참고로,
# 2025년 하반기 IMF Data의 API 형식과 필드 이름 등이 전면 개편되었다. 따라서 IMF API 자료 fetch를 도와주던
# 기존의 많은 python package가 제대로 작동하지 않는다.
#
# IMF API는 endpoint가 Dataset 마다 다르다. data id도 직접 확인해야 한다.
# IMF Data 홈페이지에서 샘플 자료를 받아서 열여보고 확인하는 것이 가장 확실하다.
# 먼저 원하는 자료를 검색해서 csv 파일로 받아서 indicator id, country id 등을 확인한다.
# 다음 DATASET로 가서 원하는 dataset을 찾아 가면 자료의 API 형식을 확인할 수 있다.
#
# 예를 들어보자. DATASET에서 international reserve를 검색한다. 이 자료는 dataset
# 가운데 Composition of Official Foreign Currency Reserves(COFER) dataset에 있다.
# COFER dataset 링크를 타고 가면 API, VIEW DATA, DOWNLOAD 아이콘이 있다.
# DOWNLOAD에 들어가면 자료를 csv 형태로 나의 컴퓨터로 받을 수 있다.
# VIEW DATA에 들어가면 화면에 자료를 보여준다.
# API에 들어가서 SDMX 2.1 API와 SDMX 3.0 API 가운데 하나를 선택해 들어간다.
# IMF data는 SDMX 2.1 API와 SDMX 3.0 API로 자료를 제공한다.
# SDMX1 API 방식은 이제 제공되지 않는다.
# 각각의 endpoint와 형식이 다르기 때문에
# 어떤 것을 사용할 지 정해야 한다.
# SDMX 2.1 API를 선택해 들어간다.
# 왼쪽 중간에 GET Data Query [Flow, Key]를 선택한다.
# 들어가면 오른쪽에 Try it 녹색 아이콘이 있다.
# 클릭하고 들어가면, 입력이 필요한 박스들이 있고 IMF.STA,CPI 데이터셋에서 미국의 CPI를 조회하는 parameter 들이 채워져 있다.
# 그 아래 노란색 아이콘 SEND를 클릭하면 결과가 화면에 나온다. 중간에 GET로 시작하는 부분이 endpoint 형식을
# 보여주는 부분이다. 이제 본인이 원하는 dataset id와 indicator id를 찾아 같은 방식으로 try해보면 된다.
#
# 아래 코드는 IMF IFS COFER Dataset에서 외환보유액의 통화별 구성 자료를 가져오는 함수이다.
# imf_api.py 파일로 저장해 놓았다.
# '[그림 52] 전세계 외환보유액의 주요 통화별 구성'을 그릴 때 fetch_cofer_data() 함수로 자료를 호출했다.
#
# SDMX 2.1 API endpoint에서 자료를 가져온다.
# 다른 Dataset에서 자료를 가져오려면 endpoint와 field 등을 그 Dataset에 맞게 수정해야 한다.
# 앞의 내용과 중복되는 부분은 설명을 생략하였다.
#
# 특징적인 부분은 다음과 같다. endpoint url이 있고, 들어가는 parameter는 currency_code, param, start_period,
# end_period이다.
# 호출된 자료는 'Date', param의 실제값이 열의 이름인 dataframe이다.
# currency_code는 IMF가 쓰는 코드를 사용해야 한다. DATA EXPLORER에서 미리 확인이 필요하다.
# param은 통화별 달러표시 총액(NV_USD)과 통화별 비중(SHRO_PT)이다. 이 이름도 미리 확인해 두어야 한다.
#
# IMF Data는 날짜 표시 형식이 FRED나 NY FED Markets Data와 다르다.
# convert_period_to_date() 함수는 IMF Date의 분기 표기방식을 FRED 방식으로
# 바꿔준다. IMF Data는 분기를 2025-Q2로 표시한다. 아래 함수는 이것을 2025-04-01로 바꿔준다.
# IMF Data의 월간 데이터 표시는 2025-M05로 표시한다. 아래 함수가 이것을 2025-05-01로 바꾼다.
#
# # Update History
# - 2026.3
#   - fetch_imf_data() 수정
#   - WEO Data set 등 데이터구조가 다른 경우를 반영
#   - Series → Obs 구조, Obs -> Series 구조 모두 처리 가능하도록 수정
#   - COFER, IL, 등 Dataset도 fetch_imf_data()를 이용할 수 있도록 일반화
#   - cache file이 unit_id에 따라서도 변화하도록 수정
# %%
import os
import sys
from cache_def import find_longer_cache, period_start, shared_cache_dir

import pandas as pd
import requests
from lxml import etree

# add parent directory (where "common" folder lives)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "sample_codes"))


def _sliced_longer_cache(cache_dir, start, suffix, prefix, cycle, end=None):
    """시작일만 더 이른 같은 시리즈 캐시를 찾아 start부터 잘라 반환 (없으면 None)
    end를 주면 캐시가 end 기간까지 들어 있을 때만 사용 (캐시 이름에 종료일이 없는 경우)"""
    try:
        longer = find_longer_cache(cache_dir, start, suffix, prefix)
        if not longer:
            return None
        df = pd.read_parquet(longer)
        if end is not None and df["Date"].max() < period_start(end, cycle):
            return None
        df = df[df["Date"] >= period_start(start, cycle)].reset_index(drop=True)
    except (ValueError, KeyError):
        return None
    print(f"🔹 Using cached data ({os.path.basename(longer)})")
    return df


def convert_period_to_date(period_str):

    if "-M" in period_str:
        year, month = period_str.split("-M")
        return f"{year}-{month}-01"
    elif "-Q" in period_str:
        year, quarter = period_str.split("-Q")
        month_map = {"1": "01", "2": "04", "3": "07", "4": "10"}
        return f"{year}-{month_map[quarter]}-01"
    elif "-S" in period_str:
        year, semi = period_str.split("-S")
        month_map = {"1": "01", "2": "06"}
        return f"{year}-{month_map[semi]}-01"
    else:
        return f"{period_str}-01-01"


def fetch_cofer_data(currency_code, param, start_period, end_period, use_cache=True):

    CACHE_DIR = shared_cache_dir("imf_cache")
    os.makedirs(CACHE_DIR, exist_ok=True)

    cache_file = os.path.join(
        CACHE_DIR,
        f"G001.AFXRA.{currency_code}.{param}.{start_period}.{end_period}.parquet",
    )

    # 같은 시리즈·같은 종료일이고 시작일이 더 이른 캐시가 있으면 잘라서 사용
    if use_cache and not os.path.exists(cache_file):
        df = _sliced_longer_cache(
            CACHE_DIR,
            start_period,
            f".{end_period}.parquet",
            f"G001.AFXRA.{currency_code}.{param}.",
            "Q",
        )
        if df is not None:
            return df

    # ✅ Load from cache
    if use_cache and os.path.exists(cache_file):
        print(f"🔹 Using cached data for G001.AFXRA.{currency_code}.{param}")
        return pd.read_parquet(cache_file)
    else:
        # ⚙️ Otherwise fetch from API
        print(f"⚙️ Fetching API data for G001.AFXRA.{currency_code}.{param}")

        base_url = (
            "https://api.imf.org/external/sdmx/2.1/data/"
            f"IMF.STA,COFER/G001.AFXRA.{currency_code}.{param}.Q"
        )
        params = {
            "startPeriod": start_period,
            "endPeriod": end_period,
            "detail": "full",
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        tree = etree.fromstring(response.content)
        obs_nodes = tree.xpath('//*[local-name()="Obs"]')

        data = []
        for obs in obs_nodes:
            time = obs.attrib.get("TIME_PERIOD")
            value = obs.attrib.get("OBS_VALUE")
            if value:
                date = pd.to_datetime(time)
                data.append((date, float(value)))

        df = pd.DataFrame(data, columns=["Date", param])

        df.to_parquet(cache_file)
        print(f"💾 Saved cache for G001.AFXRA.{currency_code}.{param}")

    return df


# %% [markdown]
# 다른 py 파일에서 위의 함수를 다음과 같이 import한다.
# imf_api 파일에 함수가 두개 있어서 함수를 모두 호출하도록 * 표시했다.
# currency의 key 값은 저자가 쓴 것이고 value 값은 IMF Data가 정한 통화별 코드이다.
# 다른 통화에 대한 자료를 fetch하려면 IMF Data 홈페이지에서 검색해서 입력한다.
# ```python
# from imf_api import *
#
# currencies = {
#     "USD": "CI_USD",
#     "EUR": "CI_EUR",
#     "JPY": "CI_JPY",
#     "GBP": "CI_GBP",
#     "CNY": "CI_CNY"
# }
#
# start = "1999-Q1"
# end = "2025-Q1"
# ```
# 한 번의 fetch로 한 가지 통화의 자료만 가져오기 때문에
# dictionary에 있는 다섯 통화의 자료를 순차적으로 fetch해서
# 하나의 dataframe으로 만든다. 'Date' column을 index로 한다.
#
# ```python
# dfs_usd = []
# dfs_share = []
#
# for name, code in currencies.items():
#     df_usd = fetch_data(code, "NV_USD",
#               start_period=start, end_period=end)
#     df_usd.rename(columns={"NV_USD": name}, inplace=True)
#     dfs_usd.append(df_usd.set_index("Date"))
#
#     df_share = fetch_data(code, "SHRO_PT",
#               start_period=start, end_period=end)
#     df_share.rename(columns={"SHRO_PT": name}, inplace=True)
#     dfs_share.append(df_share.set_index("Date"))
# ```
# %% [markdown]
# 아래 코드는 IMF IL(International Liquidity) Dataset에서 세계 각국의 금보유 자료를 가져오는 함수이다.
# imf_api.py 파일 안에 저장해 놓았다.
# '[그림 50] 전세계 금 보유량, 국가별 보유량'을 그릴 때 fetch_gold_data() 함수로 자료를 호출했다.
# Dataset이 바뀌면서 endpoint도 달라졌다.
# %%
def fetch_gold_data(
    country_id, indicator_id, unit_id, start_period, end_period, use_cache=True
):

    CACHE_DIR = shared_cache_dir("imf_cache")
    os.makedirs(CACHE_DIR, exist_ok=True)

    cache_file = os.path.join(
        CACHE_DIR,
        f"{country_id}.{indicator_id}.{unit_id}.{start_period}.{end_period}.parquet",
    )

    # 같은 시리즈·같은 종료일이고 시작일이 더 이른 캐시가 있으면 잘라서 사용
    if use_cache and not os.path.exists(cache_file):
        df = _sliced_longer_cache(
            CACHE_DIR,
            start_period,
            f".{end_period}.parquet",
            f"{country_id}.{indicator_id}.{unit_id}.",
            "M",
        )
        if df is not None:
            return df

    # ✅ Load from cache
    if use_cache and os.path.exists(cache_file):
        print(f"🔹 Using cached data for {country_id}.{indicator_id}.{unit_id}")
        return pd.read_parquet(cache_file)
    else:
        base_url = (
            "https://api.imf.org/external/sdmx/2.1/data/"
            "IMF.STA,IL/"
            f"{country_id}.{indicator_id}.{unit_id}.M"
        )

        url = base_url.format(indicator_id=indicator_id, unit_id=unit_id)
        params = {
            "startPeriod": start_period,
            "endPeriod": end_period,
            "dimensionAtObservation": "TIME_PERIOD",
            "detail": "dataonly",
            "includeHistory": "false",
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        tree = etree.fromstring(response.content)
        obs_nodes = tree.xpath('//*[local-name()="Obs"]')

        data = []

        for obs in obs_nodes:
            time = obs.attrib.get("TIME_PERIOD")
            value = obs.attrib.get("OBS_VALUE")
            if value:
                date = pd.to_datetime(convert_period_to_date(time))
                data.append((date, country_id, indicator_id, float(value)))

        df = pd.DataFrame(data, columns=["Date", country_id, indicator_id, "OBS_VALUE"])
        df.to_parquet(cache_file)
        print(
            f"💾 Saved cache for {country_id}.{indicator_id}.{unit_id}.{start_period}"
        )

    return df


# %% [markdown]
# 사용 사례는 아래와 같다. 먼저 imf_api에서 모든 함수를 import한다.
# IMF IL Dataset에서 사용하는 data id를 확인해서 필요한 id를 변수에 할당하는 코드이다.
# indicator_id는 각각 금보유량(온스), 금보유량(금액), 외환보유액(금액)을 의미한다.
# 자료를 불러올 해당 국가코드를 country_idl로 할당했다. G001은 전세계를 의미한다.
# 단위를 표시하는 id가운데 FTO는 금의 무게를 재는 단위인 troy oz를, XDR은 IMF 특별인출권 SDR을 의미한다.
# ```python
# from imf_api import *
# indicator_id = ['RGV_REVS', 'RGOLDMV_REVS', 'TRGMV_REVS']
#
# country_id = ['G001','USA','DEU','ITA', 'FRA',
#               'CHN', 'CHE','IND','JPN','TUR']
# unit_id = ['FTO', 'XDR']
# ```
# world total gold volume을 불러와서 df_world_gold로 할당하는 코드이다.
# ```python
# df_world_gold = fetch_gold_data(country_id[0], indicator_id[0],
#               unit_id[0], start_period=start, end_period=end)
# df_world_gold = df_world_gold.rename(columns={"OBS_VALUE":
#               "World Holdings"}).copy()
# ```
# 나라별 금보유량을 불러와서 df_pivot이라는 dataframe에 할당하는 코드이다.
# 한 국가씩 fetch_gold_data로 자료를 불러와서 all_data라는 dictionary에 차곡, 차곡 모은다음
# df_pivot이라는 dataframe으로 변환한다. indicator_id[0]는 'RGV_REVS'이며 금보유량을 의미한다.
# unit_id[0]는 'FTO'이며 troy oz를 의미한다. 'Date'를 index로 설정하고, 호출된 금보유량이 들어있는
# 열의 이름을 나라이름 코드로 바꾼다.
# ```python
# countries = ['DEU', 'CHN', 'IND', 'JPN', 'TUR']
#
# all_data = {}
# for country in countries:
#       df = fetch_gold_data(country, indicator_id[0],
#       unit_id[0], start_period=start, end_period=end)
#
#       df.rename(columns={df.columns[-1]: "value"}, inplace=True)
# all_data[country] = df.set_index("Date")['value'].to_dict()
# df_pivot = pd.DataFrame(all_data)
# ```
# %%

CACHE_DIR = shared_cache_dir("imf_cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def fetch_imf_data(
    data_set,
    country_id,
    indicator_id,
    start_period,
    end_period,
    cycle,
    use_cache=True,
    unit_id=None,
):

    cache_file = os.path.join(
        CACHE_DIR,
        f"{country_id}.{indicator_id}.{unit_id}.{start_period}.{cycle}.parquet",
    )

    # 같은 시리즈·주기이고 시작일이 더 이른 캐시가 있으면 잘라서 사용
    # 캐시 이름에 종료일이 없으므로 end_period 기간까지 들어 있는 캐시만 사용
    if use_cache and not os.path.exists(cache_file):
        df = _sliced_longer_cache(
            CACHE_DIR,
            start_period,
            f".{cycle}.parquet",
            f"{country_id}.{indicator_id}.{unit_id}.",
            cycle,
            end=end_period,
        )
        if df is not None:
            return df

    if use_cache and os.path.exists(cache_file):
        print(f"🔹 Using cached data for {country_id}.{indicator_id}.{unit_id}.{cycle}")
        df = pd.read_parquet(cache_file)

    else:
        print(f"⚙️ Fetching API data for {country_id}.{indicator_id}.{cycle}")

        # -------------------------------------------------
        # KEY 생성 (dataset별 예외 처리)
        # -------------------------------------------------
        if data_set == "IMF.STA,WPCPER":

            # WPCPER: CURRENCY.COUNTRY.INDICATOR.FREQ
            # 기존 코드 유지 위해 country_id → 무시하고
            # unit_id를 currency로 사용 (기존 param 구조 유지)

            unit_crypto = unit_id if unit_id else ""

            key = f"{unit_crypto}.{country_id if country_id else ''}.{indicator_id}.{cycle}"

        else:

            # ✅ unit_id 있는 dataset
            if unit_id is not None:
                key = f"{country_id}.{indicator_id}.{unit_id}.{cycle}"

            # ✅ unit_id 없는 dataset (RES, WEO)
            else:
                key = f"{country_id}.{indicator_id}.{cycle}"

        base_url = "https://api.imf.org/external/sdmx/2.1/data/" f"{data_set}/{key}"

        params = {
            "startPeriod": start_period,
            "endPeriod": end_period,
            "dimensionAtObservation": "TIME_PERIOD",
            # "detail": "full",
            "detail": "dataonly",
            "includeHistory": "false",
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()

        # for checking
        # print(base_url)
        # print(response.text[:6000])

        tree = etree.fromstring(response.content)

        data = []

        series_nodes = tree.xpath('//*[local-name()="Series"]')

        # -------------------------------------------------
        # CASE 1: Series → Obs 구조
        # -------------------------------------------------
        series_nodes = tree.xpath('//*[local-name()="Series"]')

        if series_nodes:

            for series in series_nodes:

                country = (
                    series.attrib.get("COUNTRY")
                    or series.attrib.get("REF_AREA")
                    or country_id
                )
                currency = series.attrib.get("CURRENCY", None)

                obs_nodes = series.xpath('.//*[local-name()="Obs"]')

                for obs in obs_nodes:

                    time = obs.attrib.get("TIME_PERIOD")
                    value = obs.attrib.get("OBS_VALUE")

                    if value is not None:
                        date = pd.to_datetime(convert_period_to_date(time))

                        # ----------------------------------------
                        # dataset별 append 구조
                        # ----------------------------------------
                        if data_set == "IMF.STA,WPCPER":

                            data.append(
                                (
                                    date,
                                    country,
                                    indicator_id,
                                    currency,  # 🔥 추가
                                    float(value),
                                )
                            )

                        else:

                            data.append((date, country, indicator_id, float(value)))
        # -------------------------------------------------
        # CASE 2: Obs only 구조 (WEO)
        # -------------------------------------------------
        else:

            obs_nodes = tree.xpath('//*[local-name()="Obs"]')

            for obs in obs_nodes:

                time = obs.attrib.get("TIME_PERIOD")
                value = obs.attrib.get("OBS_VALUE")

                country = (
                    obs.attrib.get("COUNTRY")
                    or obs.attrib.get("REF_AREA")
                    or country_id
                )

                if value is not None:
                    date = pd.to_datetime(convert_period_to_date(time))

                    data.append((date, country, indicator_id, float(value)))

        if data_set == "IMF.STA,WPCPER":
            df = pd.DataFrame(
                data, columns=["Date", "COUNTRY", "Indicator", "CURRENCY", "OBS_VALUE"]
            )
        else:
            df = pd.DataFrame(
                data, columns=["Date", "COUNTRY", "Indicator", "OBS_VALUE"]
            )

        df["Date"] = pd.to_datetime(df["Date"])
        df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")

        df.to_parquet(cache_file)
        print(f"💾 Saved cache for {country_id}.{indicator_id}")

    return df


# %% [markdown]
# - Fetches Crypto-based Parallel Exchange Rate Dataset data from IMF API (Dataset WPCPER).
#
#   - Expected URL Pattern based on request:
#       - .../IMF.STA,WPCPER/{unit_id}.{country_id}.{indicator_id}.{cycle}
#       - Example: .../JPY.JPN.BIT_SHD_PT.M
#   - Args:
#       - data_set (str): "IMF.STA,WPCPER"
#       - country_id (str): "JPN"
#       - indicator_id (str): "BIT_SHD_PT"
#       - unit_id (str): "JPY" (Currency code acts as the first dimension here)
#       - cycle (str): "M" (Frequency)
#   - Alternative option
#       - Use fetch_imf_data(), a general format def.
# %%


def fetch_imf_crypto_data(
    data_set,
    # country_id,
    indicator_id,
    unit_id,
    start_period,
    end_period,
    cycle,
    use_cache=True,
):
    # Create a unique cache filename including all dimensions
    cache_file = os.path.join(
        CACHE_DIR, f"{unit_id}.{indicator_id}.{start_period}.{end_period}.parquet"
    )
    # cache_file = os.path.join(CACHE_DIR, f"{unit_id}.{country_id}.{indicator_id}.{start_period}.parquet")

    # 같은 시리즈·같은 종료일이고 시작일이 더 이른 캐시가 있으면 잘라서 사용
    if use_cache and not os.path.exists(cache_file):
        df = _sliced_longer_cache(
            CACHE_DIR,
            start_period,
            f".{end_period}.parquet",
            f"{unit_id}.{indicator_id}.",
            cycle,
        )
        if df is not None:
            return df

    # ✅ Load from cache
    if use_cache and os.path.exists(cache_file):
        print(f"🔹 Using cached data for {unit_id}.{indicator_id}")
        # print(f"🔹 Using cached data for {unit_id}.{country_id}.{indicator_id}")
        df = pd.read_parquet(cache_file)
    else:
        print(f"⚙️ Fetching API data for {unit_id}.{indicator_id}")
        # print(f"⚙️ Fetching API data for {unit_id}.{country_id}.{indicator_id}")

        # Construct URL: Currency.Country.Indicator.Frequency
        # Note: cycle is assumed to be "M", so we add the dot before it.
        base_url = (
            "https://api.imf.org/external/sdmx/2.1/data/"
            f"{data_set}/"
            f"{unit_id}..{indicator_id}.{cycle}"
        )

        params = {
            "startPeriod": start_period,
            "endPeriod": end_period,  # Optional based on usage, but good to keep
            "dimensionAtObservation": "TIME_PERIOD",
            "detail": "dataonly",
            "includeHistory": "false",
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        print(response.text)
        tree = etree.fromstring(response.content)
        series_nodes = tree.xpath('//*[local-name()="Series"]')

        data = []

        for series in series_nodes:
            # Parse attributes based on the XML provided:
            # <Series CURRENCY="JPY" COUNTRY="JPN" ...>
            r_country = series.attrib.get("COUNTRY")
            r_currency = series.attrib.get("CURRENCY")

            obs_nodes = series.xpath('.//*[local-name()="Obs"]')

            for obs in obs_nodes:
                time = obs.attrib.get("TIME_PERIOD")
                value = obs.attrib.get("OBS_VALUE")
                if value:
                    date = pd.to_datetime(convert_period_to_date(time))
                    data.append(
                        (date, r_country, r_currency, indicator_id, float(value))
                    )

        # Create DataFrame with distinct Country and Currency columns
        df = pd.DataFrame(
            data, columns=["Date", "COUNTRY", "CURRENCY", "Indicator", "OBS_VALUE"]
        )

        # Save to cache
        df.to_parquet(cache_file)
        print(f"💾 Saved cache for {unit_id}.{indicator_id}")
        # print(f"💾 Saved cache for {unit_id}.{country_id}.{indicator_id}")

    return df
