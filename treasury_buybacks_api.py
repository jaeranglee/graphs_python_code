# %% [markdown]
# 미국 재무부 Fiscal Data API에서 buybacks data를 가져오는 코드를 알아보자. Fiscal Data는 하나의 형식으로 모든 자료를 제공하지 않고, 데이터베이스별로
# 다르다. 지금부터 설명하는 것은 Treasury Securities Buybacks 데이터에 있는 자료를 호출하는 코드에 대한 것이다. Treasury Securities Auctions Data를
# 포함해서 본문에 있는 그래프에 활용한 자료 호출하는 코드는 따로 만들어서 Github에 올려두었다.
# Fiscal Data API에 접속할 때 key가 없어도 된다. 사용자 계정을 만들 필요도 없다.
# Markets Data 웹페이지에서 API를 이용할 때 필요한 endpoint, parameter 등에 대한 정보를 자세히 알려주고 있다.
# 
# 아래 코드가 '[그림 47] 월별 미재무부 국채 바이백 낙찰규모'에 필요한 자료를 얻기 위해 이용한 코드이다. 
# %%
#%config InlineBackend.close_figures = False
import requests
import pandas as pd

# %% [markdown]
# 함수의 이름을 fetch_buybacks()로 했다. start_date, end_date를 지정해야 한다.
# Fiscal Data API는 한번에 호출할 수 있는 자료의 크기를 제한하고 있는데, 하나의 page[size]를 1000 이내로
# 해야 하고 한 번에 한 페이지 씩 호출해야 한다.
# %%

def fetch_buybacks(start_date, end_date):

    url = ("https://api.fiscaldata.treasury.gov/services/api"
           "/fiscal_service/v1/accounting/od/buybacks_security_details")

    params = {
        'filter': f'operation_date:gte:{start_date},'
                  f'operation_date:lte:{end_date}',
        'fields': 'operation_date,cusip_nbr,coupon_rate_pct,'
                  'maturity_date,'
                  'par_amt_accepted,weighted_avg_accepted_price',

        'page[size]': 1000,
        'page[number]': 1
    }

    all_data = []
    print("데이터 가져오기를 시작합니다...")

    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status() # 요청 실패 시 예외 발생

            print(f"페이지 {params['page[number]']} 가져오는 중 - 상태 코드: {response.status_code}")
            page_data = response.json().get("data", [])

            if not page_data:
                print("더 이상 가져올 데이터가 없습니다.")
                break

            all_data.extend(page_data)
            params['page[number]'] += 1

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP 오류가 발생했습니다: {http_err}")
            print(f"응답 내용: {response.text}")
            break
        except requests.exceptions.RequestException as req_err:
            print(f"요청 중 오류가 발생했습니다: {req_err}")
            break
# %% [markdown]
# 데이터가 다 호출되면 dataframe 형식으로 지정하고, 날짜 데이터는 datetime 형식으로
# 숫자 데이터는 numeric으로 변환한다.
# 불러오는 자료의 내용은 df의 column 이름으로 짐작할 수 있다.
# 이 함수는 두 개의 return 값을 가지고 있다.
# 첫 번째 return은 csv 형식으로 지정한 자료 파일이고,
# 두 번째 return은 dataframe 형식이다.
# 데이터를 불러오는데 시간이 걸리기 때문에 한번 호출해서
# output_path에 정한 treasury_buybacks.csv 파일로 저장해서 사용할 수 있도록 만들었다.
# 그래프를 그릴 때 이 csv 파일을 불러와서 그리면 API를 호출할 때보다 속도가 빠르다.
# csv file 대신 두 번째 return 값인 dataframe을 이용할 수도 있다.
# %%

    if all_data:
        df = pd.DataFrame(all_data)

        print("\n데이터 샘플 (처음 5개):")
        df['operation_date'] = pd.to_datetime(df['operation_date'])
        df['coupon_rate_pct'] = pd.to_numeric(df['coupon_rate_pct'],
                                        errors='coerce')
        df['maturity_date'] = pd.to_datetime(df['maturity_date'])
        df['par_amt_accepted'] = pd.to_numeric(df['par_amt_accepted'],
                                        errors='coerce')
        df['weighted_avg_accepted_price'] = pd.to_numeric(
                                    df['weighted_avg_accepted_price'],
                                        errors='coerce')
        # 디렉토리 없으면 자동 생성
        os.makedirs("data", exist_ok=True)
        output_path = "data/treasury_buybacks.csv"
        
        csv_file = df.to_csv(output_path, index=False)

    return  csv_file, df

# %% [markdown]
# 이 함수를 이용해서 자료를 호출하는 방법은 아래와 같다.
# 
# 첫 번째 return 값을 data 디렉토리 안에 treasury_buybacks.csv 이라는 파일로 저장하거나,
# 두 번째 return 값을 dataframe으로 호출하면 된다. 
#  
# ```python
#  from treasury_buybacks_api import fetch_buybacks
#  fetch_buybacks(start_date='2025-01-01', 
#             end_date='2025-09-01')[0]
#  df = fetch_buybacks(start_date='2025-01-01', 
#             end_date='2025-09-01')[1]
# ```
# %%

