# Open API를 이용한 그래프 작성

## 개요

제공된 코드는 세인트루이스 연방준비은행의 FRED, 뉴욕 연방준비은행의 Markets Data, 미국 재무부의 Fiscal Data, Yahoo Finance, 국제통화기금 IMF의 IMF Dataset의 자료를 Open API로 가져와 그래프를 그리는 Python 코드입니다. 
자료를 fetch하는 함수를 응용하면 다른 분석에도 이용할 수 있습니다.

책자 "이야기로 풀어가는 현실 국제금융론"에 포함된 [그림]을 그리는 py 파일 모두와 
자료 fetch에 필요한 모든 함수가 있습니다. 
파일 이름은 책자의 그림 번호와 그림의 내용을 의미합니다. 예를 들면, 
'[그림 1] 은행 예금잔액과 은행업 ETF가격'을 그리는 코드는 'f1_bank_deposits.py'입니다.

'f숫자_'로 시작하는 py 파일은 그래프를 작성하는 코드이고 그 밖의 py 파일은 함수를 정의한 파일이다. 예를 들어 fred_api.py는 FRED에서 data를 fetch하는 def 함수가 정의된 파일입니다. 
함수 파일은 'f숫자_'로 시작하는 파일과 같은 디렉토리에 있어야합니다.  
각 파일의 기능은 아래와 같습니다. 그래프 작성 파일은 [그림1] 경우만 설명하였습니다.

모든 코든 python 3.13으로 작성하였습니다. 
jupyter notebook에서도 실행가능하지만 그래프 저장 관련 코드라인에서 오류가 생길수 있습니다.
jupyter notebook 사용자를 위해 같은 코드를 .ipynb 확장자 형태로도 올려놓았습니다. pyCharm 이용자들은 .py 확장자를 사용하면 됩니다.

함수를 정의한 py 파일에 포함된 코멘트 들은 책자에도 수록하였습니다.

모든 파일은 자유롭게 사용할 수 있습니다.

## plot을 위한 파일

'f숫자_'로 시작하는 py 파일이 그래프를 작성하는 파일입니다. 그래프를 그리는
파일의 이름이 모두 같은 방식의 이름으로 시작합니다. 

### f1_bank_deposits.py
'[그림1] 은행예금 잔액과 은행업 ETF가격'을 그린 파일입니다. fred_api.py 파일에 있는
fetch_fred_series() 함수와 yfinance package가 이용됩니다.

## def 정의 파일

그래프를 그리는 코드 안에 사용된 함수 파일들입니다. 
주로 data를 fetch하는 함수입니다. 필요한 함수를 사용해서 불러온 data로 
그래프를 그리게 됩니다.
그림을 정해진 규칙의 이름으로 저장하는 함수도 있습니다.

### bok_ecos_api.py

한국은행 경제통계시스템, ECOS에서 자료를 불러옵니다.
stat_code, item_code, cycle은 ECOS가 정한 id로 적어야 하여, ECOS 홈피에서 검색해서 확인해야 합니다.
```python
from bok_ecos_api import fetch_ecos_series
df = fetch_ecos_series(name, stat_code, item_code, cycle, start_date=start, end_date=end)
```

#### Parameters
| Parameter    | Type  | Description                                               |
|--------------|-------|-----------------------------------------------------------|
| `name`       | `str` | Key name of your choice for a series id, example ['Gold'] |
| `stat_code`  | `str` | ECOS series code, example ["902Y003"]                     |
| `item_code`  | `str` | ECOS item code, example ["040101"]                        |
| `cyle`       | `str` | ECOS timeseries cycle, one of ['Y', 'Q', 'M', 'D']        |
| `start_date` | `str` | ECOS timeseries start date, 'YYYY-MM-DD'                  |
| `end_date`   | `str` | ECOS timeseries end date, 'YYYY-MM-DD'                    |

#### Return
pd.DataFrame for a ecos series with datetime

### fred_api.py

St. Louise Fed FRED Open API에서 자료를 fetch 합니다. series_id는 FRED 홈피에서 직접 검색해야 합니다.
```python
from fred_api import fetch_fred_series
df = fetch_fred_series(series_id=series, start_date=start, end_date=end)
```
#### Parameters
| Parameter    | Type  | Description                                        |
|--------------|-------|----------------------------------------------------|
| `seires_id`  | `str` | FRED series id, example ['EFFR']                   |
| `start_date` | `str` | FRED timeseries start date, 'YYYY-MM-DD'           |
| `end_date`   | `str` | FRED timeseries end date, 'YYYY-MM-DD'             |
#### Return
pd.DataFrame with datatime 'observation_date', 'series_id'

### imf_api.py
세 개의 def가 있습니다. 각각 IMF COFER Dataset에서 통화별 외환보유액 구성자료 fetch,
IMF IL Dataset에서 국가별 금보유량, 금보유액, 외환보유액 자료 fetch,
IMF Dataset의 날짜 형식을 FRED 날짜형식으로 전환하는 함수입니다.

```python
from imf_api import *
df1 = fetch_cofer_data(currency_code, param, start_period, end_period)
df2 = fetch_gold_data(country_id, indicator_id, unit_id, start_period, end_period) 
df3 = convert_period_to_date(period_str)  
```
#### Parameters
| Parameter       | Type  | Description                                                |
|-----------------|-------|------------------------------------------------------------|
| `currency_code` | `str` | Key name of your choice for a currency id, example ['USD'] |
| `param`         | `str` | COFER series currency id, example ["CI_USD"]               |
| `start_period`  | `str` | IMF timeseries start date, example, 'YYYY-Q1', 'YYYY-M01'  |
| `end_period`    | `str` | IMF timeseries end date, example, 'YYYY-Q1', 'YYYY-M01'    |
| `country_id`    | `str` | IMF country id, example, 'G001' for world, 'USA' for USA   |
| `indicator_id`  | `str` | IMF indicator id, example, 'RGV_REVS' for gold volume      |
| `unit_id`       | `str` | IMF unit id, example, 'FTO' for troy ounce, 'XDR' for SDR  |
#### Return
pd.DataFrame with datatime 'Date', and other params.

### nfp_revision.py

세인트루이스 연준의 ALFRED(ArchivaL Federal Reserve Economic Data) Open API에서 NFP(Total Nonfarm Payrolls)
과거 자료(vintages)를 불러온 다음 수정치(revisions)를
계산한 후 csv 파일로 저장합니다. 파일이름은
"data/nfp_revisions.csv"로 지정했습니다. 
'[그림15] NFP 고용 수정전후 비교', '[그림16] 직전 2개월 NFP 수정치'에 csv 파일을 
이용합니다. 매번 api로 자료를 불러와서 계산하면 속도가 느리기 때문에 필요시 자료를 불러와 계산하고 저장한 다음
분석에 이용하는 것이 좋습니다. 1990년 vintage부터 불러오기 때문에 코드 실행후 완료까지 10분이상 소요됩니다.
코드 안의 자료 시작, 종료 일자를 변경할 수 있습니다. PyCharm, 현재 파일 실행 버튼을 눌러 실행합니다.
```python
start = '1990-01-01'
end = '2025-09-04'
```
#### Parameters
입력하지 않아도 지정한 기간내의 모든 자료를 다 불러 옵니다.

#### Return
'data/nfp_revisions.csv'

### nyfed_api_all_rates.py
fetch_all_secured_rates()가 정의된 곳 입니다. 뉴욕 연준에서 아래의 자룔를 fetch합니다.
New York Fed Markets Data, Reference Rates, Secured Rates, rates and percentile

```python
start = '2025-01-01'
end = '2025-02-01'
from nyfed_api_all_rates import fetch_all_secured_rates
df = fetch_all_secured_rates(start_date=start, end_date=end, rate_type_filter=None):
```
#### Parameters

| Parameter          | Type  | Description                                                              |
|--------------------|-------|--------------------------------------------------------------------------|
| `rate_type_filter` | `str` | Rate types, Available inputs   ['tgcr', 'bcgr', 'obfr', sofr', 'sofrai'] |
| `start_date`       | `str` | timeseries start date, 'YYYY-MM-DD'                                      |
| `end_date`         | `str` | timeseries end date, 'YYYY-MM-DD'                                        |

#### Return
pd.DataFrame with datatime 'Date', and other columns.
```python
df = df.rename(columns={
        "type": "Type",
        "percentRate": "Rate",
        "percentPercentile1": "Percentile1",
        "percentPercentile25": "Percentile25",
        "percentPercentile75": "Percentile75",
        "percentPercentile99": "Percentile99"})
```


### nyfed_api_rp.py
rp, rrp rate 자료를 불러옵니다.
```python
start = '2025-01-01'
end = '2025-02-01'
from nyfed_api_rp import fetch_rp_operation
df = fetch_rp_operation(start_date=start, end_date=end)
```
#### Return
pd.DataFrame with datatime 'Date', and other columns.
```python
df = df.rename(columns= {"operationDate", "operationLimit", "totalAmtSubmitted", "totalAmtAccepted", "operationType"]].rename(columns={
        "operationDate": "Date",
        "operationLimit": "Limit",
        "totalAmtSubmitted": "Sumbitted",
        "totalAmtAccepted": "Accepted",
        "operationType": "Type",
        "term": 'Term'
        })
```

### nyfed_api_rate_volume.py
fetch_secured_series()가 정의된 파일 입니다.
New York Fed Markets Data API에서 secured volume 또는 rate(1일물 증권담보대출금리 거래의 거래량)을 fetch합니다. 
"rate_type"으로 all, tgcr, bgcr, sofr, sofrai 가운데 하나를 입력합니다. all은 모든 rate type 자료를 호출합니다.
volume을 호출 할지 또는 rate을 호출할지 호출함수를 선택합니다.

```python
start = '2025-01-01'
end = '2025-02-01'
from nyfed_api_rate_volume import fetch_secured_series, fetch_all_secured_rates_vol
df = fetch_all_secured_rates_vol(start_date=start, end_date=end, , rate_type_filter=None)
```
#### Return
pd.DataFrame with datatime 'Date', and other columns.
```python
df = df.rename(columns={
        "type": "Type",
        "volumeInBillions": 'Volume'
    })
```

### nyfed_rrp_vol.py
fetch_rrp_vol() 이 정의된 곳입니다.
New York Fed Markets Data API에서 뉴욕 연준의 rp 거래 또는 rrp 거래의 거래량을 fetch합니다.
```python
start = '2025-01-01'
end = '2025-02-01'
from nyfed_rrp_vol import fetch_rrp_vol
df = fetch_rrp_vol(start_date=start, end_date=end)
```
#### Return
pd.DataFrame with datatime 'Date', and other columns.
```python
df = df.rename(columns={
        "operationType": "Type",
        "totalAmtAccepted": 'Total Volume',
        "acceptedCpty": 'Accepted Cpty',
        "participatingCpty": 'Participating Cpty'
    })
print(df['Type'].unique())
['RP','RRP']
```

### plot_def.py
그래프와 관련된 함수들이 정의된 파일입니다.  
  
#### set_fonts()
  
모든 그래프 코드 앞에 한글 폰트를 정의하는 코드가 들어갑니다.
애플 시스템 또는 윈도우 시스템인지 사용자 환경에 따라 맞는 폰트를 정합니다.
그래프마다 반복되는 코드여서 함수로 정의해 놓았습니다. 파라미터 입력값은 없습니다.
첫 10여 개의 그림에는 폰트 정의 코드라인을 직접 그래프 코드 파일에 
포함했습니다. 
  
#### nber_recession(start, end)  
  
기존 그래프에 미국의 경기침체기(NBER 기준)를 음영으로 넣어주는 함수입니다.
입력 파라미터 start, end가 반드시 있어야 합니다.
자료 시작일 start, 자료 종료일 end를 기존 그래프와 같게 하여야 합니다.
  
아래 코드를 plot code line 아래에 넣어야 합니다.

```python
from plot_def import nber_recession  
recession_periods = nber_recesssion(start=start, end=end)  

for peak, trough in recession_periods:  
    ax.axvspan(peak, trough, color='gray', alpha=0.3)
```

#### plot_save(i=None)  

그래프를 파일로 저장하는 함수입니다.
그래프를 그리는 코드의 이름을 파일 이름으로 사용합니다.
현재보다 하위에 있는 'pic_jpg' 디렉토리에 '파일이름.jpg, 그리고
'pic_tif' 디렉토리에 '파일이름.tif'파일로 저장합니다. jupyter notebook 형식의 코드에서 오류가 날 수 있습니다.
입력 파라미터 i는 그림의 번호입니다.
그림을 한 개만 그리는 코드에는 i 값을 지정하지 않아도 됩니다.
for 루프로 그림을 여러개 그리는 코드에는 코드의 루핑 횟수 지정변수를 가져와서 넣어야
그림별로 다른 파일로 저장됩니다.

그림이 한개 일 때
```python
from plot_def import *
plot_save()
```

그림이 여러개 일 경우
```python
from plot_def import *
plot_save(i=i)
```
  
### treasury_api.py

Treasury Fiscal Data-DTS, MSPD 홈페이지에서 json 파일을 직접
다운로드 한 다음, parsing 하는 함수가 들어있습니다.

#### fetch_debt_outstanding_json()
Public Debt Outstanding 금액을 월별 국채종류별로 리턴합니다.

#### Parameters

| Parameter    | Type  | Description                                                                                            |
|--------------|-------|--------------------------------------------------------------------------------------------------------|
| `json_path`  | `str` | Monthly Statement of the Public Debt dataset, Summary of Public Debt Outstanding 테이블 자료를 json 포맷으로 다운  |


```python
start="1990-01-01"
end = "2025-12-31"
file_path1="data/MSPD_SumSecty_20010131_20250731.json"
file_path ="data/DTS_PubDebtTrans_20051003_20250814.json"
from treasury_api import *
outstanding = fetch_debt_outstanding_json(start_date=start, end_date=end, json_path=file_path1)
issues = fetch_debt_issues_json(start_date=start, end_date=end, json_path=file_path)
```

### treasury_auctions_api.py
Fiscal Data, Treasury Securities Auctions data를 가져와서 파일로 저장하는 코드입니다.

```python
start = "2023-01-01"
end = "2025-12-31"
output_path = fetch_securities_auction(start_date=start, end_date=end)
```
#### Return
fetch 자료를 csv 파일로 저장합니다.

```python
output_path = "data/treasury_auctions_2024.csv"
```


### treasury_buy_backs_api.py

Treasury Fiscal Data, Treasury Buybacks data fetch
```python
start="2025-01-01"
end = "2025-12-31"
from treasury_buybacks_api import fetch_buybacks
df = fetch_buybacks(start_date, end_date)
```

### treasury_debt_limit_api.py

Treasury Fiscal Data, DTS, Debt Subject to Limit Table 에서 미리 다운로드한 파일을 parsing 합니다.

```python
start = "2021-01-01"
end = "2025-12-31"
base_url = "data/DTS_DebtSubjLim_20051003_20250902.json" 
df = fetch_debt_limit_json(start_date=start, end_date=end, base_url=base_url)
```
#### Return
pd.DataFrame with datatime 'Date', and other columns.

```python
df = df.rename(columns={
        "record_date": "Record Date",
        "debt_catg": "Debt Category",
        "close_today_bal": "Closing Balance Today",
    })
```
### treasury_tic_api.py

Treasury International Capital (TIC) System data parsing

파일이 없거나 강제로 업데이트할 때, force_update=True 일 때만 다운로드 합니다.

```python
path = 'your_file_path/your_file.xlxs'
# force_update = True if you want to update

from treasury_tic_api import *

df0=download_tic_holdings_soup(file_path=path, force_update=False)
df1=download_tic_holdings_html(file_path=path, force_update=False)
df2=download_tic_sales_soup(file_path=path, force_update=False)
df3=download_tic_sales_html(file_path=path, force_update=False)
```
