# New York Fed Markets Data 에서 시계열 데이터를 받아 pandas DataFrame으로 반환

# 아래와 같은 식으로 파라미터 입력 하여 사용
#=======================================

# 함수 호출
# from nyfed_api_rp import fetch_rp


# Fetch series



import requests
import pandas as pd


'''
    NY Fed rp, rrp 결과 가져오는 함수

    Parameters:
        start_date:
        end_date: 


    Returns:
        pd.DataFrame: [Date, and other values in df ] 형식의 DataFrame
'''

def fetch_rp_operation(start_date, end_date):
#    url = f"https://markets.newyorkfed.org/api/rp/all/all/results/last/{last_number}.json"
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
