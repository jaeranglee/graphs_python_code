# %% [markdown]
# - New York Fed Markets Data 에서 시계열 데이터를 받아 pandas DataFrame으로 반환
# %%
import requests
import pandas as pd


def fetch_all_secured_rates(start_date, end_date, rate_type_filter=None):
    """
    NY Fed에서 제공하는 모든 secured rates (TGCR, SOFR, BGCR 등)를 호출하는 함수.

    Parameters:
        start_date (str): 조회 시작일 (YYYY-MM-DD)
        end_date (str): 조회 종료일 (YYYY-MM-DD)
        rate_type_filter (str or list): "tgcr", "sofr", "bcgr" 중 필터링할 금리 유형 (선택사항)

    Returns:
        pd.DataFrame: 날짜, 금리 유형(type), 금리(percentRate), 분위(percentiles) 포함된 DataFrame
    """
    url = "https://markets.newyorkfed.org/api/rates/all/search.json"
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "type": rate_type_filter #if isinstance(rate_type_filter, str) else None
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch all rates: {response.status_code}\n{response.text}")

    data = response.json()

    df = pd.DataFrame(data.get("refRates", []))

    if df.empty:
        return pd.DataFrame(columns=[
            "Date", f"{rate_type_filter.upper()}", "Rate", "Percentile1", "Percentile25", "Percentile75", "Percentile99"
        ])

    # 컬럼 정리 및 변환
    df["Date"] = pd.to_datetime(df["effectiveDate"])
    df = df.rename(columns={
        "type": "Type",
        "percentRate": "Rate",
        "percentPercentile1": "Percentile1",
        "percentPercentile25": "Percentile25",
        "percentPercentile75": "Percentile75",
        "percentPercentile99": "Percentile99"
    })

    return df[[
        "Date", "Type", "Rate", "Percentile1", "Percentile25", "Percentile75", "Percentile99"
    ]].sort_values(["Type", "Date"])
