'''
NY FED Markets Data 가운데 뉴욕 연준의 RP 거래와 RRP 경매결과 자료를 가져오는 코드를 소개한다.
이 코드는 nyfed_api_rrp_vol.py라는 파일로 저장해 놓았고 함수의 이름은 fetch_rrp_vol()이다.
'[그림 10] MMF의 RRP와 TGCR 거래 규모'를 그릴 때 이 함수로 자료를 호출했다.
[그림 10]을 그려주는 코드는 f10_tgcr_vol.py이다.
//
지금부터 nyfed_api_rrp_vol.py 코드의 내용을 개략적으로 소개한다.
NY FED Markets Data의 API는 자료마다 endpoint가 다르고 json 형식도 약간씩 다르다. 그래서 다른 함수로 정의한 것이다.
Markets Data API 웹페이지에 데이터 별 endpoint와 필요한 parameter, 형식 등이 잘 정리되어 있으니 참고하면 된다.
앞의 내용과 중복되는 부분은 설명을 생략하였다.
//
특징적인 부분은 다음과 같다. endpoint url이 달라졌다. 들어가는 parameter도 rate volume을 호출하는 API와 다르다.
json 포맷으로 불러오는 데이터의 구조가 다층구조로 바뀌었다. "repo", {} 형식의 상위구조 아래,
"operations", []로 된 하위구조의 자료를 가져온다.
'''

import requests
import pandas as pd

def fetch_rrp_vol(start_date, end_date):

    url = f"https://markets.newyorkfed.org/api/rp/results/search.json"
    params = {
        "startDate": start_date,
        "endDate": end_date,
        "method": 'fixed',
        "securityType": 'tsy',
        "term": 'overnight',
        "details": 'details',
        "propositions": 'propositions'
        }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch all rates: "
                           f"{response.status_code}\n{response.text}")

    # 날짜별 RP, RRP 경매결과를 가져와서 dataframe에 담는 과정이다.
    # Type에는 RP 또는 RRP가 표시되고, Total Volume에는 그날의 낙찰총액이, Accepted Cpty에는 낙찰기관의 갯수,
    # Participating Cpty에는 응찰기관의 개수, Date에 날짜 자료가 담기고,
    # Date는 datetime 형식으로 변환한다.
    # 총액 데이터는 첫 번째 dataframe으로 돌려준다.
    # //

    data = response.json()
    df = pd.DataFrame(data.get("repo", {}).get("operations", []))

    df["Date"] = pd.to_datetime(df["operationDate"])
    df = df.rename(columns={
        "operationType": "Type",
        "totalAmtAccepted": 'Total Volume',
        "acceptedCpty": 'Accepted Cpty',
        "participatingCpty": 'Participating Cpty'
    })

    # RP, RRP 거래 데이터를 거래 Counterparty, Accepted Volume 별로 가져오는 코드가 시작된다.
    # Counterparty Type, "Amount Accepted, Date 자료가 담기고, Date는 datetime 형식으로 변환한다.
    # 거래상대방별 데이터는 두 번째 dataframe으로 돌려준다. 거래상대방은 금융기관을 기관 성격에 따라 그룹화한 것이다.
    # 개별 기관에 대한 내용은 아니다.
    # 거래상대방별 데이터는 두 번째 dataframe으로 돌려준다.
    #//

    prop_list = []
    for i, props in enumerate(df["propositions"]):
        if isinstance(props, list) and len(df) > 0:
            temp_df = pd.json_normalize(props)
            temp_df["Date"] = df.loc[i, "Date"]
            prop_list.append(temp_df)

    if prop_list:
        propositions_df = pd.concat(prop_list, ignore_index=True)
        propositions_df = propositions_df.rename(columns={
            "counterpartyType": "Counterparty Type",
            "amtAccepted": "Amount Accepted"
        })
        propositions_df["Date"] = pd.to_datetime(propositions_df["Date"])
    else:
        propositions_df = pd.DataFrame(columns=
                                       ["Counterparty Type",
                                        "Amount Accepted", "Date"])
        propositions_df["Date"] = pd.to_datetime(
                                        propositions_df["Date"])
    return df, propositions_df

'''
확인을 위해 총액을 보여주는 첫 번째 자료를 df_total로 할당하고 csv파일로 저장했다. 
양이 많아서 파일의 내용은 수록하지 않았다. 
Type 가운데 RRP의 낙찰총액, Total Volume을 [그림10]에 이용했다. 
두 번째 자료는 낙찰기관 타입별 자료이며 화면에 결과를 출력했다. 
Counter Party 가운데 mmf의 낙찰규모를 [그림 10]에 이용했다.
//
'''

df_total = fetch_rrp_vol(start_date="2024-01-01",
                         end_date='2024-02-01')[0]
df_total.to_csv("total.csv", index=False)
df_cpt = fetch_rrp_vol(start_date="2024-01-01",
                       end_date='2024-02-01')[1]
print(df_cpt)

'''
   Counterparty Type  Amount Accepted       Date///
0               bank                0 2024-02-01///
1                gse      25855000000 2024-02-01///
2                mmf     477693000000 2024-02-01///
3                 pd                0 2024-02-01///
4               bank                0 2024-01-31///
..               ...              ...        ...///
83                pd                0 2024-01-03///
84              bank                0 2024-01-02///
85               gse      27250000000 2024-01-02///
86               mmf     677614000000 2024-01-02///
87                pd                0 2024-01-02///
                                                ///
[88 rows x 3 columns]///
//
'''



