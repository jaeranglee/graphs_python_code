# %% [markdown]
# # New York Fed Markets Data API: 기준금리 전체
# ## file name
# - nyfed_api_all_rates.py
#
# ## 기능
# - 뉴욕 연준 Reference Rates(SOFR, TGCR, BGCR, EFFR, OBFR, SOFRAI)의 금리와 분위수를 한 번에 받는다.
# - 캐시 없음
#
# ## 출처
# - https://markets.newyorkfed.org/static/docs/markets-api.html
# - API: `https://markets.newyorkfed.org/api/rates/all/search.json`
# - API key 필요 없음
#
# ## fetch_all_secured_rates()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from nyfed_api_all_rates import fetch_all_secured_rates
#
# df_all = fetch_all_secured_rates(start_date="2024-01-01", end_date="2026-10-30")
# tgcr = df_all[df_all["Type"] == "TGCR"]
#
# # Type을 열로 펼치기
# wide = df_all[df_all["Type"].isin(["SOFR", "TGCR"])].pivot(index="Date", columns="Type", values="Rate")
# ```
#
# ## parameters
# | Parameter          | Type          | Description                                     |
# |--------------------|---------------|-------------------------------------------------|
# | `start_date`       | `str`         | 시작일 `YYYY-MM-DD`                              |
# | `end_date`         | `str`         | 종료일 `YYYY-MM-DD`                              |
# | `rate_type_filter` | `str \| None` | API `type` 인자 (None이면 전체)                  |
#
# ## returned columns and values
# `Type`, `Date` 순으로 정렬
#
# | Column         | Type     | Description                                       |
# |----------------|----------|---------------------------------------------------|
# | `Date`         | datetime | 기준일 (effectiveDate)                             |
# | `Type`         | str      | `SOFR`, `TGCR`, `BGCR`, `EFFR`, `OBFR`, `SOFRAI`   |
# | `Rate`         | float    | 금리 (%)                                           |
# | `Percentile1`, `Percentile25`, `Percentile75`, `Percentile99` | float | 거래 금리 분위수 (%) |
#
# ## 사용하는 곳
# - `wallstreet/` 8개 (예: `f_effr.py`, `f_on_rates.py`), `graphs_python_code/` 4개, `gold/gold_sofr_spread.py` 등 15개
# %%
import pandas as pd
import requests


def fetch_all_secured_rates(start_date, end_date, rate_type_filter=None):

    url = "https://markets.newyorkfed.org/api/rates/all/search.json"
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "type": rate_type_filter,  # if isinstance(rate_type_filter, str) else None
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch all rates: {response.status_code}\n{response.text}"
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

    df["Date"] = pd.to_datetime(df["effectiveDate"])
    df = df.rename(
        columns={
            "type": "Type",
            "percentRate": "Rate",
            "percentPercentile1": "Percentile1",
            "percentPercentile25": "Percentile25",
            "percentPercentile75": "Percentile75",
            "percentPercentile99": "Percentile99",
        }
    )

    return df[
        [
            "Date",
            "Type",
            "Rate",
            "Percentile1",
            "Percentile25",
            "Percentile75",
            "Percentile99",
        ]
    ].sort_values(["Type", "Date"])
