# %% [markdown]
# # New York Fed Markets Data API: 기준금리 거래량
# ## file name
# - nyfed_api_rate_volume.py
#
# ## 기능
# - 뉴욕 연준 Reference Rates(SOFR, TGCR, BGCR, EFFR, OBFR)의 일별 거래량을 받는다.
# - 캐시 없음
#
# ## 출처
# - https://markets.newyorkfed.org/static/docs/markets-api.html
# - API: `https://markets.newyorkfed.org/api/rates/all/search.json?type=volume`
# - API key 필요 없음
#
# ## fetch_all_secured_rates_vol()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from nyfed_api_rate_volume import fetch_all_secured_rates_vol
#
# df = fetch_all_secured_rates_vol(start_date="2025-09-01", end_date="2025-09-30")
# tgcr_vol = df[df["Type"] == "TGCR"]
# ```
#
# ## parameters
# | Parameter          | Type          | Description                                  |
# |--------------------|---------------|----------------------------------------------|
# | `start_date`       | `str`         | 시작일 `YYYY-MM-DD`                           |
# | `end_date`         | `str`         | 종료일 `YYYY-MM-DD`                           |
# | `rate_type_filter` | `str \| None` | 금리 유형 (소문자, 예: `tgcr`). None이면 전체  |
#
# ## returned columns and values
# `Type`, `Date` 순으로 정렬
#
# | Column   | Type     | Description                                 |
# |----------|----------|---------------------------------------------|
# | `Date`   | datetime | 기준일                                       |
# | `Type`   | str      | `SOFR`, `TGCR`, `BGCR`, `EFFR`, `OBFR`, `SOFRAI` |
# | `Volume` | float    | 거래량 (십억 달러, SOFRAI는 NaN)              |
#
# ## 사용하는 곳
# - `wallstreet/` 6개 (예: `f_tgcr_vol.py`, `f_effr_iorb.py`), `graphs_python_code/` 2개
# - 아래 셀부터는 책 원고용 설명이다.

# %% [markdown]
# 이번에는 NY Fed에서 제공하는 Markets Data를 API로 불러오는 함수를 소개한다.
# 뉴욕 연준 API는 key를 발급받지 않아도 누구나 접속해서 조회할 수 있다.
# 그리고, Markets Data 웹페이지에서 API를 이용할 때 필요한 endpoint, parameter 등에 대한 정보를 자세히 알려주고 있다.
#
# 우선, secured rates의 거래량을 호출하는 함수를 살펴본다.
# 이 코드는 nyfed_api_rate_volume.py라는 파일로 저장해 놓았고 함수의 이름은 fetch_all_secured_rate_vol()이다.
# '[그림 10] MMF의 RRP와 TGCR 거래 규모'를 그릴 때 이 함수로 자료를 호출했다.
# [그림 10]을 그려주는 코드는 f10_tgcr_vol.py이다. Github에 올려놓은 파일을 참고하면 된다.
#
# 지금부터 nyfed_api_rate_volume.py 코드의 내용을 개략적으로 소개한다.
# 먼저 필요한 패키지를 호출한다. requests와 pandas 패키지가 필요하다.
# %%
import pandas as pd
import requests


# %% [markdown]
# 다음은 fetch_all_secured_rate_vol()함수를 정의한 부분이다.
# 입력 파라미터는 start_date, end_date, rate_type_filter이며,
# 각각 자료 시작일, 자료 종료일, 그리고 불러올 이자율 type이 할당된다.
# start_date, end_date는 YYYY-MM-DD 형식으로 입력한다.
# rate_type_filter는 tgcr, bcgr, sofr 등 가져올 금리 유형을
# 소문자로 입력한다. rate_type_filter를 할당하지 않으면 모든 rate type의 자료가 출력되도록 했다.
# rate_type_filter = None이 그런 의미이다.
# rate_type_filter = 'tgcr' 로 할당하면 TGCR에 대한 자료만 가져온다.
# url이 이번에 가져올 Market Data API의 주소, endpoint이다.
# json 포맷으로 불러와서 data라는 변수에 먼저 할당한다.
# 이어서 json 형식의 자료 안에 "refRates"로 시작하는 대괄호 속 자료를 모두 가져온다.
# %%
def fetch_all_secured_rates_vol(start_date, end_date, rate_type_filter=None):

    url = "https://markets.newyorkfed.org/api/rates/all/" "search.json?type=volume"
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "type": rate_type_filter if isinstance(rate_type_filter, str) else None,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch all rates: "
            f"{response.status_code}"
            f"\n{response.text}"
        )

    data = response.json()
    df = pd.DataFrame(data.get("refRates", []))

    if df.empty:
        return pd.DataFrame(
            columns=[
                "Date",
                f"{rate_type_filter.upper()}",
                "Rate",
                "Percentile1",
                "Percentile25",
                "Percentile75",
                "Percentile99",
            ]
        )

    # %% [markdown]
    # 열의 이름을 직관적이고 간단하게 바꾸고 자료 순서를 정렬해서 보내주는 부분이다.
    # effectiveDate는 파이썬의 datetime 형식으로 바꿔준 다음 Date라는 열에 넣는다.
    # 호출되는 자료는 Date, Type, Volume이며 Type, Date 순서로 정렬한다.
    # %%

    df["Date"] = pd.to_datetime(df["effectiveDate"])
    df = df.rename(columns={"type": "Type", "volumeInBillions": "Volume"})

    return df[["Date", "Type", "Volume"]].sort_values(["Type", "Date"])


# %% [markdown]
# 예시를 위해 뉴욕 연준의 Markets Data API에서 secured rate의 거래량 자료를 불러와서 data_all이라는 변수에 할당하고 출력해보자.
# 먼저 함수를 import 해아하지만 지금 함수가
# 같은 코드 안에 들어 있어서 import 과정을 생략할 수 있었다.
# 만약 fetch_all_secured_rates_vol() 함수가 다른 파일에
# 저장되어 있다면, 아래와 같이 import 문을 앞에 써야 한다.
# ```python
# from nyfed_api_rate_volume.py import fetch_all_secured_rates_vol
# data_all = fetch_all_secured_rates_vol(start_date="2025-09-01",
#        end_date="2025-09-03")
# ```
#
# 확인을 위해 자료를 출력했다.
# 열의 이름은 각각, Date, Type, Volume이 되었다.
# rate_type_filter에 지정을 하지 않아서 모든 rate type이 다 조회되었다.
# 모든 줄에 인덱스가 있다. 이번에는 인덱스 순서로 정렬이 되어 있지 않고,
# Type, Date 순서로 정렬되어 있음을 알 수 있다.
# start_date를 2025-09-01로 했는데 가져온 자료의 시작은 2025-09-01이다.
# 2025-09-01에 자료가 없기 때문에 2025-09-02부터
# 시작된다.
#
# ```python
# print(data_all)
#    Date          Type  Volume
# 9  2025-09-02    BGCR  1142.0
# 3  2025-09-03    BGCR  1146.0
# 6  2025-09-02    EFFR   120.0
# 0  2025-09-03    EFFR   119.0
# 7  2025-09-02    OBFR   220.0
# 1  2025-09-03    OBFR   218.0
# 10 2025-09-02    SOFR  2947.0
# 4  2025-09-03    SOFR  2880.0
# 11 2025-09-02  SOFRAI     NaN
# 5  2025-09-03  SOFRAI     NaN
# 8  2025-09-02    TGCR  1118.0
# 2  2025-09-03    TGCR  1118.0
# ```
# %%
