import requests
import pandas as pd
import platform
import json



def fetch_debt_limit(start_date, end_date):
    """
    Fiscaldata.treasury 에서 데이터을 직접 최신 자료로 모두 가져와 병합한 DataFrame 반환.
    시간이 많이 걸림.
    한 페이지로 가져올 수 있는 자료 수 제한이 있기 때문에 여러번 가져와서 합치기 때문
    """

    base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/debt_subject_to_limit"

    params = {
        'filter': f'record_date:gte:{start_date},record_date:lte:{end_date}',
        'sort': '-record_date',
        'fields': 'record_date,debt_catg,close_today_bal',
        'format': 'json',
        'page[size]': 1000,
        'page[number]': 1
    }

    all_data = []

    while True:
        response = requests.get(base_url, params=params)
        print(f"Fetching page {params['page[number]']} - Status code: {response.status_code}")
        if response.status_code != 200:
            break

        page_data = response.json().get("data", [])
        if not page_data:
            break

        all_data.extend(page_data)
        params['page[number]'] += 1

    df = pd.DataFrame(all_data)


    df["record_date"] = pd.to_datetime(df["record_date"])
    df = df.rename(columns={
        "record_date": "Record Date",
        "debt_catg": "Debt Category",
        "close_today_bal": "Closing Balance Today",
    })

    df["Closing Balance Today"] = pd.to_numeric(df['Closing Balance Today'], errors='coerce')

    return df

#Test
#print(fetch_debt_limit().info())


#--------
#데이터를 한번에 json 으로 받은 다음 \data 디렉토리에 저장후 추출
# fetch_debt_limit 으로 받으면 여러 번 나눠 받기 때문에 시간이 오래 걸림

def fetch_debt_limit_json(start_date, end_date, base_url):

    data = pd.read_json(base_url)
    # Expand the list of dicts inside "data"
    df = pd.json_normalize(data.get("data", []))

    print(df.head())

    df["record_date"] = pd.to_datetime(df["record_date"])
    df = df.rename(columns={
        "record_date": "Record Date",
        "debt_catg": "Debt Category",
        "close_today_bal": "Closing Balance Today",
    })

    df["Closing Balance Today"] = pd.to_numeric(df['Closing Balance Today'], errors='coerce')

    df=df[(df['Record Date']>=start_date)&(df['Record Date']<=end_date)]
    df=df[['Record Date', 'Debt Category', 'Closing Balance Today']]
    return df

#Test
#print(fetch_debt_limit_json().info())



#-------------------
# 정부부채
# cvs 파일로 저장했을 때 불러오는 루틴

def fetch_debt_limit_cvs(start_date, end_date,
                         file_path):
    na_vals = ['null', 'NULL', 'Null', ' null', 'null ']
    # CSV 파일 불러오기
    df = pd.read_csv(file_path, na_values=na_vals)

    # 날짜를 datetime 형식으로 변환
    df["Record Date"] = pd.to_datetime(df["Record Date"])

    # Filter for
    df = df[(df['Record Date'] >= start_date)].copy()
    df = df[(df['Record Date'] <= end_date)].copy()

    return df

#Test
#print(fetch_debt_limit_cvs())






