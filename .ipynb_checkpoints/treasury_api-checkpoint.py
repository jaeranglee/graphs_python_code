'''
미국 재무부 Fiscal Data API에서 Treasury Securities, DTS, MSPD, data를 가져와서 처리하는 코드입니다.
request url을 매번 사용하면 시간이 오래 걸려 불편하기 때문에 직접 Fiscal Data 페이지에서
json file 로 다운 받아 처리하는 용도입니다.

사용 예시는 다음과 같습니다.

Public Debt issuance, DTS 자료
저장해 둔 json file 사용
# file_path ="data/DTS_PubDebtTrans_20051003_20250814.json"
# def fetch_debt_issues_json(start_date=start, end_date=end, json_path = file_path):

#---------------------------
# Public Debt Outstanding, Monthly Statement of the Public Debt
# 받아놓은 jason file에서
# file_path="data/MSPD_SumSecty_20010131_20250731.json"
# def fetch_debt_outstanding_json(start_date=start, end_date=end, json_path=file_path):
'''


import requests
import pandas as pd
import matplotlib.dates as mdates


'''
# 아래 endpoint에서 request 할 수 있습니다. 그러나 fetch 시간이 너무 오래 걸려 홈피에서 파일로 다운 받기를 권장합니다.

url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/public_debt_transactions"

params = {
    'filter': 'record_date:gte:2020-01-01,record_date:lte:2025-12-31,security_market:eq:Marketable',
    'fields': 'record_date,transaction_type,security_market,security_type,transaction_today_amt,transaction_mtd_amt',
    'page[size]': 1000,
    'page[number]': 1
}
'''


'''
# 홈피에서 CSV 파일로 다운 받을 수도 있습니다. csv 파일의 경우를 위한 코드입니다.
# 활성화 해서 사용할 수 있습니다.

file_path="data/marketable_debt_transactions.csv"
def fetch_debt_issues_csv(start_date="2005-01-01", end_date="2025-12-31",
                          file_path=file_path):

    df=pd.read_csv(file_path)
'''

# Public Debt issuance, DTS 갸운데
# Public Debt Transactions
# 테이블
# 자료를 json 포맷으로 다운 받습니다.
# 미국 국채 일별 발행 자료가 들어있는데 이를 parsing 하는 함수입니다.

# 저장해 둔 json file을 parsing 하는 함수가 시작됩니다.
# start_date, end_date, json_path는 원 코드에서 이 함수를 호술할 때 넣어줍니다.

def fetch_debt_issues_json(start_date, end_date, json_path):

    data = pd.read_json(json_path)
    # Expand the list of dicts inside "data"
    df = pd.json_normalize(data.get("data", []))

    #print(df.info())

    df["record_date"] = pd.to_datetime(df["record_date"])
    df = df[df['record_date'] >= start_date].copy()
    df = df[df['record_date'] <= end_date].copy()

    # 날짜, 숫자 변환
    df['record_date'] = pd.to_datetime(df['record_date'])
    df['transaction_today_amt'] = pd.to_numeric(df['transaction_today_amt'], errors='coerce')/1e6
    df['transaction_mtd_amt'] = pd.to_numeric(df['transaction_mtd_amt'], errors='coerce')/1e6
    df['transaction_fytd_amt'] = pd.to_numeric(df['transaction_fytd_amt'], errors='coerce')/1e6

    # 필요한 security_type만 필터링
    filtered_df = df[df['security_type'].isin(['Bills', 'Bonds', 'Notes'])]

    # Issues와 Redemptions로 분리
    issues = filtered_df[filtered_df['transaction_type'] == 'Issues'].copy()
    redemptions = filtered_df[filtered_df['transaction_type'] == 'Redemptions'].copy()

    # 날짜 인덱스 설정
    issues.set_index('record_date', inplace=True)
    redemptions.set_index('record_date', inplace=True)


    yearly_issues = (issues[['security_type','transaction_fytd_amt']]
                     .rename(columns={'transaction_fytd_amt': 'issues'})
                     .copy())
    yearly_redemptions = (redemptions[['security_type','transaction_fytd_amt']]
                          .rename(columns={'transaction_fytd_amt': 'redemptions'})
                          .copy())

    # merge하여 Net Issuance 계산
    yearly_net = pd.merge(yearly_issues, yearly_redemptions, on=['record_date', 'security_type'], how='outer')
    yearly_net.fillna(0, inplace=True)

    yearly_net['net_issues'] = yearly_net['issues'] - yearly_net['redemptions']


    # 월별 합계 계산 (security_type별)
    monthly_issues = (issues.groupby(['security_type', pd.Grouper(freq='ME')])['transaction_today_amt']
        .sum()
        .reset_index(name="issues")
        .copy()
        ).reset_index()
    monthly_issues=monthly_issues.set_index('record_date')
    # Remove last row if last value is 0
    if monthly_issues["issues"].iloc[-1] <1e-4:
        monthly_issues = monthly_issues.iloc[:-1]

    monthly_redemptions = (redemptions.groupby(['security_type', pd.Grouper(freq='ME')])['transaction_today_amt']
        .sum()
        .reset_index(name="redemptions")
        .copy()
        ).reset_index()
    monthly_redemptions=monthly_redemptions.set_index('record_date')
    # Remove last row if last value is 0
    if monthly_redemptions["redemptions"].iloc[-1] < 1e-4:
        monthly_redemptions = monthly_redemptions.iloc[:-1]

    filtered_df = filtered_df.set_index('record_date')
    monthly_total = ((filtered_df.groupby(['transaction_type', pd.Grouper(freq='ME')])['transaction_today_amt'])
                 .sum().reset_index()
                 )

    # merge하여 Net Issuance 계산
    net = pd.merge(monthly_issues, monthly_redemptions, on=['record_date', 'security_type'], how='outer')
    net.fillna(0, inplace=True)

    #print(net.head())
    #print(net.columns)

    net['net_issues'] = net['issues'] - net['redemptions']
    net=net.reset_index()

    issues = issues.rename(columns={'transaction_today_amt': 'issues'}).copy()
    redemptions = redemptions.rename(columns={'transaction_today_amt': 'redemtions'}).copy()

    # 리턴 값은 순서대로 다음과 같습니다.
    # 월별 국채종류별 발행액, 월별 국채종류별 상환액, 월별 총발행액, 월별 국채종류별 순발행액(발행액-상환액), 연간 순발행액, 일간 자료

    return monthly_issues, monthly_redemptions, monthly_total, net, yearly_net, issues


#Public Debt Outstanding 금액을 월별, 국채 종류별로 리턴합니다.
#Monthly Statement of the Public Debt dataset 가운데
#Summary of Public Debt Outstanding 테이블 자료를 json 포맷으로 다운받습니다.
#받아놓은 jason file에서 parsing 합니다.


def fetch_debt_outstanding_json(start_date, end_date, json_path):

    data = pd.read_json(json_path)
    # Expand the list of dicts inside "data"
    df = pd.json_normalize(data.get("data", []))


    df["record_date"] = pd.to_datetime(df["record_date"])
    df = df[df['record_date'] >= start_date].copy()
    df = df[df['record_date'] <= end_date].copy()

    # 날짜, 숫자 변환
    df['record_date'] = pd.to_datetime(df['record_date'])
    df["total_mil_amt"] = pd.to_numeric(df["total_mil_amt"], errors='coerce') / 1e6

    df = df.rename(columns={
        "record_date": "Record Date",
        'security_class_desc': "Class",
        "total_mil_amt": "Amount"
    })
    # 필요한 security_type만 필터링
    print(df['Class'].unique())
    print(df.columns)
    df = df[df["Class"].isin(['Bills', 'Bonds', 'Notes', 'Treasury Inflation-Protected Securities', 'Floating Rate Notes'])]
    #df = df[df["Class"].isin(['Bills', 'Bonds'])]
    #print(df.head())

    # 날짜 인덱스 설정
    df.set_index('Record Date', inplace=True)
    #print(df.head())

    # 월별 국채 종류별 outstanding value를 리턴합니다.
    return df

