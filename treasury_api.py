#fiscaldata.treasury.gov API format
# request url takes so long time.
# json file 로 저장해서 사용하는 def

#---------------------------
# Public Debt issuance, DTS 자료
# 저장해 둔 json file 사용
# file_path ="data/DTS_PubDebtTrans_20051003_20250814.json"
#
# def fetch_debt_issues_json(start_date=start, end_date=end, json_path = file_path):

#---------------------------
# Public Debt Outstanding, Monthly Statement of the Public Debt
# 받아놓은 jason file에서
# file_path="data/MSPD_SumSecty_20010131_20250731.json"
# def fetch_debt_outstanding_json(start_date=start, end_date=end, json_path=file_path):




import requests
import pandas as pd
import matplotlib.dates as mdates


'''
# 데이터 불러와서 저장(시간 오래 걸림)
url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/public_debt_transactions"

params = {
    'filter': 'record_date:gte:2020-01-01,record_date:lte:2025-12-31,security_market:eq:Marketable',
    'fields': 'record_date,transaction_type,security_market,security_type,transaction_today_amt,transaction_mtd_amt',
    'page[size]': 1000,
    'page[number]': 1
}
'''


'''
# 저장해 둔 CSV 파일 사용
file_path="data/marketable_debt_transactions.csv"
def fetch_debt_issues_csv(start_date="2005-01-01", end_date="2025-12-31",
                          file_path=file_path):

    df=pd.read_csv(file_path)
'''

# Public Debt issuance, DTS 자료
# 저장해 둔 json file 사용

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

    return monthly_issues, monthly_redemptions, monthly_total, net, yearly_net, issues


# Public Debt Outstanding, Monthly Statement of the Public Debt
# 받아놓은 jason file에서


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
    return df

