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

### fred_api.py

fetch_fred_series()가 정의된 곳입니다.
St. Louise Fed FRED Open API에서 자료를 fetch 합니다.

### imf_api.py
세 개의 def가 있습니다. 각각 IMF COFER Dataset에서 통화별 외환보유액 구성자료 fetch,
IMF IL Dataset에서 국가별 금보유량, 금보유액, 외환보유액 자료 fetch,
IMF Dataset의 날짜 형식을 FRED 날짜형식으로 전환하는 함수입니다.

#### fetch_cofer_data()
#### fetch_gold_data() 
#### convert_period_to_date()  

### nfp_revision.py

세인트루이스 연준의 ALFRED(ArchivaL Federal Reserve Economic Data) Open API에서 NFP(Total Nonfarm Payrolls)
과거 자료(vintages)를 불러온 다음 수정치(revisions)를
계산한 후 csv 파일로 저장합니다. 파일이름은
"data/nfp_revisions.csv"로 지정했습니다. 
'[그림15] NFP 고용 수정전후 비교', '[그림16] 직전 2개월 NFP 수정치'에 csv 파일을 
이용합니다. 매번 api로 자료를 불러와서 계산하면 속도가 느리기 때문에 필요시 자료를 불러와 계산하고 저장한 다음
분석에 이용하는 것이 좋습니다. 1990년 vintage부터 불러오기 때문에 코드 실행후 완료까지 5분이상 소요됩니다.

### nyfed_api_all_rates.py
fetch_all_secured_rates()가 정의된 곳입니다. 뉴욕 연준에서 아래의 자룔를 fetch합니다.
New York Fed Markets Data, Reference Rates, Secured Rates, rates and percentile

### nyfed_api_vol_rate.py
fetch_secured_series()가 정의된 곳입니다.
New York Fed Markets Data API에서 secured volume 또는 rate(1일물 증권담보대출금리 거래의 거래량)을 fetch합니다. 
parameter에서 "type":을 'volume'과 'rate' 가운데 하나를 선택합니다. 
"rate_type"으로 all, tgcr, bgcr, sofr, sofrai 가운데 하나를 입력합니다. all은 모든 자료를 호출합니다.
"type"으로 volume, 또는 rate 하나를 선택합니다.

### nyfed_rrp_vol.py
fetch_rrp_vol() 이 정의된 곳입니다.
New York Fed Markets Data API에서 뉴욕 연준의 rp 거래 또는 rrp 거래의 거래량을 fetch합니다.

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

from plot_def import nber_recession  
recession_periods = nber_recesssion(start=start, end=end)  
for peak, trough in recession_periods:  
    ax.axvspan(peak, trough, color='gray', alpha=0.3)
  

#### plot_save(i=None):  

그래프를 파일로 저장하는 함수입니다.
그래프를 그리는 코드의 이름을 파일 이름으로 사용합니다.
현재보다 하위에 있는 'pic_jpg' 디렉토리에 '파일이름.jpg, 그리고
'pic_tif' 디렉토리에 '파일이름.tif'파일로 저장합니다. jupyter notebook 형식의 코드에서 오류가 날 수 있습니다.
입력 파라미터 i는 그림의 번호입니다.
그림을 한 개만 그리는 코드에는 i 값을 지정하지 않아도 됩니다.
for 루프로 그림을 여러개 그리는 코드에는 코드의 루핑 횟수 값 지징변수를 가져와서 넣어야
그림별로 다른 파일로 저장됩니다.

그림이 한개 일 때  
plot_save()  
  
그림이 여러개 일 경우   
plot_save(i=i)  
  





