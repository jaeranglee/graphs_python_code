# %% [markdown]
# # New York Fed Markets Data API
# ## file name
# - nyfed_api_all_rates.py
# ## example
# ```python
# from nyfed_api_all_rates import fetch_all_secured_rates
#
# df_all = fetch_all_secured_rates(start_date=start, end_date=end)
#
# rate_type_filter = "tgcr"
# dftr = df_all[df_all["Type"] == rate_type_filter.upper()].copy()
# ```
#
# ## parameters
# | Parameter    | Type  | Description                               |
# |--------------|-------|-------------------------------------------|
# | `start_date` | `str` | start date, 'YYYY-MM-DD'                  |
# | `end_date`   | `str` | end date, 'YYYY-MM-DD'                    |
#
# ## "Type" in returned df
# - 'tgcr', 'sofr', 'bgcr', 'sofrai', 'effr', 'obfr'
# ## returned columns and values
# - df["Date", "Type", "Rate", "Percentile1", "Percentile25",
# "Percentile75", "Percentile99"]
# %%
import requests
import pandas as pd

def fetch_all_secured_rates(start_date, end_date, rate_type_filter=None):

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
