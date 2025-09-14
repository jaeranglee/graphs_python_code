import requests
import pandas as pd


def fetch_secured_series(rate_type="tgcr", start_date="2000-01-01", end_date="2025-12-31"):
    """
    NY Fed secured rate에서 금리와 거래량(volume)을 모두 가져와 병합한 DataFrame 반환.

    Parameters:
        rate_type (str): 'tgcr', 'sofr', 'bgcr'
        start_date (str): 시작일 (YYYY-MM-DD)
        end_date (str): 종료일 (YYYY-MM-DD)

    Returns:
        pd.DataFrame: [Date, Rate, Volume] 컬럼을 가진 DataFrame
    """
    rate_type = rate_type.lower()
    base_url = f"https://markets.newyorkfed.org/api/rates/secured/{rate_type}/search.json"

    def fetch_data(query_type):
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "type": query_type  # 'rate' 또는 'volume'
        }
        r = requests.get(base_url, params=params)
        r.raise_for_status()
        data = r.json().get("refRates", [])
        df = pd.DataFrame(data)
        return df

    # Fetch rate
    df_rate = fetch_data("rate")
    if df_rate.empty:
        df_rate = pd.DataFrame(columns=["Date", f"{rate_type.upper()}"])

    else:
        df_rate = df_rate[["effectiveDate", "percentRate"]].rename(columns={
            "effectiveDate": "Date",
            "percentRate": rate_type.upper()
        })
        df_rate["Date"] = pd.to_datetime(df_rate["Date"])

    # Fetch volume
    df_vol = fetch_data("volume")
    if df_vol.empty:
        df_vol = pd.DataFrame(columns=["Date", f"{rate_type.upper()}_VOLUME"])
    else:
        df_vol = df_vol[["effectiveDate", "volume"]].rename(columns={
            "effectiveDate": "Date",
            "volume": f"{rate_type.upper()}_VOLUME"
        })
        df_vol["Date"] = pd.to_datetime(df_vol["Date"])

    # Merge both
    df = pd.merge(df_rate, df_vol, on="Date", how="outer").sort_values("Date").reset_index(drop=True)
    return df
