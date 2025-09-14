# Open API를 이용한 그래프 작성

## 개요

제공된 코드는 세인트루이스 연방준비은행의 FRED, 뉴욕 연방준비은행의 Markets Data, 미국 재무부의 Fiscal Data, Yahoo Finance, 국제통화기금 IMF의 IMF Dataset의 자료를 Open API로 가져와 그래프를 그리는 Python 코드이다. 자료를 fetch하는 함수를 응용하면 다른 분석에도 이용할 수 있다.

책자 "이야기로 풀어가는 현실 국제금융론"에 포함된 [그림]을 그리는 py 파일 모두와 자료 fetch에 필요한 모든 함수가 들어있다. 파일 이름은 책자의 그림 번호와 그림의 내용을 의미한다. 예를들어 '[그림 1] 은행 예금잔액과 은행업 ETF가격'을 그리는 코드의 이름은 'f1_bank_deposits.py'이다.

'fxx_xxx'로 시작하는 py 파일은 그래프를 작성하는 코드이고 다른 py 파일은 함수를 정의한 파일이다. 예를 들어 fred_api.py는 FRED에서 data를 fetch하는 def 함수가 정의된 파일이다. 모든 def 함수 파일은 'fxx_xx'로 시작하는 파일과 같은 디렉토리에 있어야한다.  파일별 역할을 아래 설명하였다.

python 3.13으로 작성하였다. jupyter notebook에서도 실행가능하지만 os와 관련된 코드라인에서 오류가 생길수 있다.

def 함수를 정의한 py 파일에 포함된 코멘트 라인은 책자의 부록과 동일하다.

모든 파일은 자유롭게 사용할 수 있다.

## def 정의 파일

#### fred_api.py
def fetch_fred_series()가 정의된 곳이다.
St. Louise Fed FRED Open API에서 자료를 fetch 한다.
#### nyfed_api_vol_rate.py
def fetch_secured_series()가 정의된 곳이다.
New York Fed Markets Data API에서 secured volume 또는 rate(1일물 증권담보대출금리 거래의 거래량)을 fetch한다. parameter에서 "type":을 'volume'과 'rate' 가운데 하나를 넣는다. 
"rate_type"으로 all, tgcr, bgcr, sofr, sofrai 가운데 하나를 넣는다. all을 쓰면 모두 호출된다.
"type"으로 volume, 또는 rate 하나를 선택한다.
#### nyfed_rrp_vol.py
def fetch_rrp_vol() 이 정의된 곳이다.
New York Markets Data API에서 뉴욕 연준의 rp 거래 또는 rrp 거래의 거래량을 fetch한다.
#### imf_api.py
def fetch_cofer_data()  
def fetch_gold_data()  
def convert_period_to_date()  
세 개의 def가 있다. 각각 IMF COFER Dataset에서 통화별 외환보유액 구성자료 fetch,
IMF IL Dataset에서 국가별 금보유량, 금보유액, 외환보유액 자료 fetch
IMF Dataset의 날짜 형식을 FRED 날짜형식으로 전환을 위한 함수이다.




