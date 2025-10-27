# %% [markdown]
# # New York Fed Markets Data API
# ## file name
# - nyfed_api_rp.py
# ## example
# ```python
# from nyfed_api_rp import fetch_rp
#
# df_rp = fetch_rp(start_date=start, end_date=end)
# ```
#
# ## parameters
# | Parameter    | Type  | Description                               |
# |--------------|-------|-------------------------------------------|
# | `start_date` | `str` | start date, 'YYYY-MM-DD'                  |
# | `end_date`   | `str` | end date, 'YYYY-MM-DD'                    |
#
# ## "Type" in returned df
# - 'rp', 'rrp'
# ## "Term" in returned df
# - 'overnight', 'term'
# ## returned columns and values
#```python
# df = df[["operationDate", "operationLimit",
#         "totalAmtSubmitted", "totalAmtAccepted", "operationType"]].rename(columns={
#         "operationDate": "Date",
#         "operationLimit": "Limit",
#         "totalAmtSubmitted": "Sumbitted",
#         "totalAmtAccepted": "Accepted",
#         "operationType": "Type",
#         "term": 'Term'
#         })
#```
# %%
import requests
import pandas as pd

def fetch_rp_operation(start_date, end_date):

    url =(f"https://markets.newyorkfed.org/api/rp/results/search.json?"
          f"startDate={start_date}&endDate={end_date}&operationTypes=Repo&term=overnight")

    params = { 'startDate': 'start_date',
               'endDate' : 'end_date'
             }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch all: {response.status_code}\n{response.text}")

    data = response.json()
    records = data.get("repo", {}).get("operations", [])

    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=["Date", "Type"])

    df["operationDate"] = pd.to_datetime(df["operationDate"])
    df = df[["operationDate", "operationLimit", "totalAmtSubmitted", "totalAmtAccepted", "operationType"]].rename(columns={
        "operationDate": "Date",
        "operationLimit": "Limit",
        "totalAmtSubmitted": "Sumbitted",
        "totalAmtAccepted": "Accepted",
        "operationType": "Type",
        "term": 'Term'
        })
    df['Date'] = pd.to_datetime(df['Date']).copy()
    return df
