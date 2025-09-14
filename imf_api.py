'''
코드를 설명하기 전에 IMF Data에서 API로 자료를 fetch하기 위한 기본적 준비사항을 알아보자.
우선 IMF Data 홈페이지에서 회원가입을 하는 것을 권장한다.
Api key는 요구하지 않지만 사용자로 가입하고 로그인해야 API 이용에 필요한 세부 내용을 열람할 수 있다. 참고로,
2025년 하반기 IMF Data의 API 형식과 필드 이름 등이 전면 개편되었다. 따라서 IMF API 자료 fetch를 도와주던
기존의 많은 python package가 제대로 작동하지 않는다.
//
IMF API는 endpoint가 Dataset 마다 다르다. data id도 직접 확인해야 한다.
IMF Data 홈페이지에서 샘플 자료를 받아서 열여보고 확인하는 것이 가장 확실하다.
먼저 원하는 자료를 검색해서 csv 파일로 받아서 indicator id, country id 등을 확인한다.
다음 DATASET로 가서 원하는 dataset을 찾아 가면 자료의 API 형식을 확인할 수 있다.
//
예를 들어보자. DATASET에서 international reserve를 검색한다. 이 자료는 dataset
가운데 Composition of Official Foreign Currency Reserves(COFER) dataset에 있다.
COFER dataset 링크를 타고 가면 API, VIEW DATA, DOWNLOAD 아이콘이 있다.
DOWNLOAD에 들어가면 자료를 csv 형태로 나의 컴퓨터로 받을 수 있다.
VIEW DATA에 들어가면 화면에 자료를 보여준다.
API에 들어가서 SDMX 2.1 API와 SDMX 3.0 API 가운데 하나를 선택해 들어간다.
IMF data는 SDMX 2.1 API와 SDMX 3.0 API로 자료를 제공한다.
SDMX1 API 방식은 이제 제공되지 않는다.
각각의 endpoint와 형식이 다르기 때문에
어떤 것을 사용할 지 정해야 한다.
SDMX 2.1 API를 선택해 들어간다.
왼쪽 중간에 GET Data Query [Flow, Key]를 선택한다.
들어가면 오른쪽에 Try it 녹색 아이콘이 있다.
클릭하고 들어가면, 입력이 필요한 박스들이 있고 IMF.STA,CPI 데이터셋에서 미국의 CPI를 조회하는 parameter 들이 채워져 있다.
그 아래 노란색 아이콘 SEND를 클릭하면 결과가 화면에 나온다. 중간에 GET로 시작하는 부분이 endpoint 형식을
보여주는 부분이다. 이제 본인이 원하는 dataset id와 indicator id를 찾아 같은 방식으로 try해보면 된다.
//
아래 코드는 IMF IFS COFER Dataset에서 외환보유액의 통화별 구성 자료를 가져오는 함수이다.
imf_api.py 파일로 저장해 놓았다.
'[그림 49] 전세계 외환보유액의 주요 통화별 구성'을 그릴 때 fetch_cofer_data() 함수로 자료를 호출했다.
//
SDMX 2.1 API endpoint에서 자료를 가져온다.
다른 Dataset에서 자료를 가져오려면 endpoint와 field 등을 그 Dataset에 맞게 수정해야 한다.
앞의 내용과 중복되는 부분은 설명을 생략하였다.
//
특징적인 부분은 다음과 같다. endpoint url이 있고, 들어가는 parameter는 currency_code, param, start_period,
end_period이다.
호출된 자료는 'Date', param의 실제값이 열의 이름인 dataframe이다.
currency_code는 IMF가 쓰는 코드를 사용해야 한다. DATA EXPLORER에서 미리 확인이 필요하다.
param은 통화별 달러표시 총액(NV_USD)과 통화별 비중(SHRO_PT)이다. 이 이름도 미리 확인해 두어야 한다.
//
IMF Data는 날짜 표시 형식이 FRED나 NY FED Markets Data와 다르다.
convert_period_to_date() 함수는 IMF Date의 분기 표기방식을 FRED 방식으로
바꿔준다. IMF Data는 분기를 2025-Q2로 표시한다. 아래 함수는 이것을 2025-04-01로 바꿔준다.
IMF Data의 월간 데이터 표시는 2025-M05로 표시한다. 아래 함수가 이것을 2025-05-01로 바꾼다.
//
'''


import pandas as pd
import requests
from lxml import etree


def convert_period_to_date(period_str):

    if "-M" in period_str:
        year, month = period_str.split("-M")
        return f"{year}-{month}-01"
    elif "-Q" in period_str:
        year, quarter = period_str.split("-Q")
        month_map = {"1": "01", "2": "04", "3": "07", "4": "10"}
        return f"{year}-{month_map[quarter]}-01"
    else:
        return f"{period_str}-01-01"

def fetch_cofer_data(currency_code, param, start_period, end_period):

    base_url = ("https://api.imf.org/external/sdmx/2.1/data/"
                "IMF.STA,COFER/"
                "G001.AFXRA.{currency}.{param}.Q")
    url = base_url.format(currency=currency_code, param=param)
    params = {
        "startPeriod": start_period,
        "endPeriod": end_period,
        "detail": "full"
    }
    response = requests.get(url, params=params)
    tree = etree.fromstring(response.content)
    obs_nodes = tree.xpath('//*[local-name()="Obs"]')

    data = []
    for obs in obs_nodes:
        time = obs.attrib.get("TIME_PERIOD")
        value = obs.attrib.get("OBS_VALUE")
        if value:
            date = pd.to_datetime(convert_period_to_date(time))
            data.append((date, float(value)))

    return pd.DataFrame(data, columns=["Date", param])

'''
다른 py 파일에서 이 함수를 다음과 같이 import한다.
imf_api 파일에 함수가 두개 있어서 함수를 모두 호출하도록 * 표시했다.
currency의 key 값은 저자가 쓴 것이고 value 값은 IMF Data가 정한 통화별 코드이다.
다른 통화에 대한 자료를 fetch하려면 IMF Data 홈페이지에서 검색해서 입력한다.
//

from imf_api import *///

currencies = {///
    "USD": "CI_USD",///
    "EUR": "CI_EUR",///
    "JPY": "CI_JPY",///
    "GBP": "CI_GBP",///
    "CNY": "CI_CNY"///
}///

start = "1999-Q1"///
end = "2025-Q1"///

한 번의 fetch로 한 가지 통화의 자료만 가져오기 때문에
dictionary에 있는 다섯 통화의 자료를 순차적으로 fetch해서
하나의 dataframe으로 만든다. 'Date' column을 index로 한다.
//

dfs_usd = []///
dfs_share = []///

for name, code in currencies.items():///
    df_usd = fetch_data(code, "NV_USD", start_period=start, end_period=end)///
    df_usd.rename(columns={"NV_USD": name}, inplace=True)///
    dfs_usd.append(df_usd.set_index("Date"))///

    df_share = fetch_data(code, "SHRO_PT", start_period=start, end_period=end)///
    df_share.rename(columns={"SHRO_PT": name}, inplace=True)///
    dfs_share.append(df_share.set_index("Date"))///
'''

'''
아래 코드는 IMF IL(International Liquidity) Dataset에서 세계 각국의 금보유 자료를 가져오는 함수이다.
imf_api.py 파일 안에 저장해 놓았다.
'[그림 50] 전세계 금 보유량, 국가별 보유량'을 그릴 때 fetch_gold_data() 함수로 자료를 호출했다.
Dataset이 바뀌면서 endpoint도 달라졌다.
//
'''

def fetch_gold_data(country_id, indicator_id, unit_id, start_period, end_period):

    base_url = ("https://api.imf.org/external/sdmx/2.1/data/"
                "IMF.STA,IL/"
                f"{country_id}.{indicator_id}.{unit_id}.M")

    url = base_url.format(indicator_id=indicator_id, unit_id=unit_id)
    params = {
        "startPeriod": start_period,
        "endPeriod": end_period,
        "dimensionAtObservation": "TIME_PERIOD",
        "detail": "dataonly",
        "includeHistory": "false"
    }

    response = requests.get(url,params=params)
    response.raise_for_status()

    tree = etree.fromstring(response.content)
    obs_nodes = tree.xpath('//*[local-name()="Obs"]')

    data = []

    for obs in obs_nodes:
        time = obs.attrib.get("TIME_PERIOD")
        value = obs.attrib.get("OBS_VALUE")
        if value:
            date = pd.to_datetime(convert_period_to_date(time))
            data.append((date, country_id, indicator_id, float(value)))

    return pd.DataFrame(data, columns=["Date", country_id, indicator_id, "OBS_VALUE"])

'''

사용 사례는 아래와 같다. 먼저 imf_api에서 모든 함수를 import한다.
//
IMF IL Dataset에서 사용하는 data id를 확인해서 필요한 id를 변수에 할당하는 코드이다.
indicator_id는 각각 금보유량(온스), 금보유량(금액), 외환보유액(금액)을 의미한다.
자료를 불러올 해당 국가코드를 country_idl로 할당했다. G001은 전세계를 의미한다.
단위를 표시하는 id가운데 FTO는 금의 무게를 재는 단위인 troy oz를, XDR은 IMF 특별인출권 SDR을 의미한다.
//

from imf_api import *///
indicator_id = ['RGV_REVS', 'RGOLDMV_REVS', 'TRGMV_REVS']///

country_id = ['G001','USA','DEU','ITA', 'FRA',///
              'CHN', 'CHE','IND','JPN','TUR']///
unit_id = ['FTO', 'XDR']///


world total gold volume을 불러와서 df_world_gold로 할당하는 코드이다.
//
df_world_gold = fetch_gold_data(country_id[0], indicator_id[0],///
    unit_id[0], start_period=start, end_period=end)///
df_world_gold = df_world_gold.rename(columns={"OBS_VALUE":"World Holdings"}).copy()///

나라별 금보유량을 불러와서 df_pivot이라는 dataframe에 할당하는 코드이다.
한 국가씩 fetch_gold_data로 자료를 불러와서 all_data라는 dictionary에 차곡, 차곡 모은다음
df_pivot이라는 dataframe으로 변환한다. indicator_id[0]는 'RGV_REVS'이며 금보유량을 의미한다.
unit_id[0]는 'FTO'이며 troy oz를 의미한다. 'Date'를 index로 설정하고, 호출된 금보유량이 들어있는 
열의 이름을 나라이름 코드로 바꾼다.
//

countries = ['DEU', 'CHN', 'IND', 'JPN', 'TUR']///
///
all_data = {}///
for country in countries:///
    df = fetch_gold_data(country, indicator_id[0],///
        unit_id[0], start_period=start, end_period=end)///
///
    df.rename(columns={df.columns[-1]: "value"}, inplace=True)///
    all_data[country] = df.set_index("Date")['value'].to_dict()///
df_pivot = pd.DataFrame(all_data)///
'''