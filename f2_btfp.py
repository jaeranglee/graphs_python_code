# #[그림2] BTFP 잔액과 정책금리
'''
이제 세이트루이스 연준이 제공하는 FRED애서 API를 이용해서 자료를 불러오고 그래프를 그리는 방법을 알아보자.
먼저 FRED API 홈페이지에 접속한다. 검색 엔진에서 'fred api'를 키워드로 검색해서 찾아가는 것이 빠르다.
FRED API 홈페이지 오른 쪽에 'API Keys | Terms of Use' 항목이 있는데 'API Keys' 링크를 클릭한다.
'Request or view your API keys' 항목을 링크하고 보면 회원가입을 해야 함을 알 수 있다.
'Register' 항목을 클릭하고 회원가입 절차를 밟는다. 반드시 본인의 이메일 계정이 있어야 한다.
이메일 확인 과정을 거치면 계정이 생성된다. 계정을 만들고 'Sign in' 항목을 통해 로그인 한다.
다시 'Request or view your API keys' 링크를 타고 들어가서 API를 요청하는 양식을 채우고 제출하면 바로 API key가 발급된다.
상업적 목적으로 대량의 데이터를 요청하지 않는다면, 발급목적에 'Personal Study' 정도로 적으면 된다.
나의 계정에서 key를 확인하고 복사해 놓는다. 영어와 숫자가 포함된 긴 문자열이며 FRED API에 접속할 수 있는 비밀번호이다.
//
FRED API Key를 발급 받았다면, 지금부터 FRED API로 자료를 불러와서 본문의 '[그림2] BTFP 잔액과 정책금리' 그래프를 그리는 코드를 이용해 보자.
먼저 PyCharm 프로그램을 실행시켜서 f2_btfp.py 파일을 열어본다.
코드가 열렸으면 api_key = "FRED_API_KEY" 부분을 바꿔야 한다. "FRED_API_KEY"를 지우고 따옴표 안에 발급 받은 FRED API key를 넣어야 한다.
api_key = 'aaabbbbcccdddeeefff11122233344' 이런 식으로 넣는다.
윈도우 환경이라면 shift + control + f10 조합으로 동시에 키를 누르면 코드가 실행된다. 맥 환경에서는 상단 우측 선택메뉴에서
‘현재 파일’을 선택하고 그 바로 오른쪽에 있는 세모 표시를 클릭하면 실행된다. 정상적으로 실행이 완료되면 모니터에 그래프가 나타난다.
//
그래프를 그리는 코드는 크게 4단계로 구성되어 있다. 1단계는 준비단계이며 라이브러리를 불러오는 부분, 한글과 영문폰트를 정의하는 부분으로 되어 있다.
2단계는 자료호출 단계이며 FRED에서 자료를 호출해서 변수에 저장하는 역할을 한다. 자료의 시작과 끝을 정하고 필요한 가공을 하기도 한다.
3단계는 그래프를 그리는 부분이고, 마지막 4단계는 그래프를 파일로 저장하고 화면에 보여주는 코드이다. 이하 내용은 python을 사용하고, PyCharm을 코드 에디터로 설치하여 사용하는 것을
기준으로 설명하였다. 다른 코드들도 대체로 같은 구조로 되어 있다.
//
맨 처음은 그림을 그리기 위해 필요한 패키지들을 불러오는 부분이다. pandas는 자료를 다루는 패키지이다. 모든 그래프에서
사용한 자료는 dataframe이라는 형태를 이용한다. pandas가 dataframe를 다루는 도구이다. 첫 줄은 pandas를 불러와서 pd라는 이름으로 줄여서 정의한 것이다.
그 다음 줄은 그래프를 그리는 matplotlib.pypot을 불러 오고 이것을 plt로 줄여서 쓴다는 것이다. 세번 째 줄은 matplotlib.date를 불러 오는데 날짜 출력 양식을 제어하는 역할을 한다.
이것도 줄여서 mdates라고 정의했다. 필요할 때 마다 패키지를 설치하면 된다. 패키지 이름을 줄여서 쓰는 표현이 관행으로 굳어져 있으니 그대로 따라하면 된다.
//
'''

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform

'''
다음은 한글과 영문의 폰트를 정의하는 코드이다. 애플 컴퓨터를 사용하면 애플고딕체를 쓰고,
윈도우 기반 컴퓨터를 사용하면 맑은고딕체를 쓰도록 했다. 마지막 줄은 마이너스 부호가 깨져 보이는 것을 방지하는 코드이다.
//
'''

if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

'''
//
이제 자료호출 단계로 넘어 간다. Open API를 사용하여 FRED에서 원하는 자료를 불러오고 불러온 자료를 변수에 저장한다. 
이 때 사용할 requests 패키지를 먼저 불러 와야 한다.  
//
'''

import requests

'''
세인트루이스 연준의 FRED에 사용자 등록을 하고 api key를 받아서 api_key라는 변수에 할당한다. key 값은 
받드시 따옴표 안에 써야한다. 예시를 위해 "FRED_API_KEY"라고 가상의 key 값을 할당했다.
//
'''

api_key = "FRED_API_KEY"

'''
다음은 자료 불러오는 함수를 정의한 부분이다. 함수의 이름은 fetch_fred_series()이다. 괄호 안에 함수에 필요한 변수가 있다.
series_id가 호출할 자료인데, FRED에서 사용하는 이름을 써야한다. FRED에서 사용하는 데이터의 이름은 FRED API 홈페이지에서 검색해서 찾아야 한다.
돋보기가 그려진 검색창에 'BTFP'라는 키워드로 찾으면 결과를 보여준다. 검색 결과중에 원하는 데이터를 클릭하면 데이터에 대한 설명과 그래프가 보인다.
이 때 보여주는 데이터의 이름을 복사해서 넣는다. 그렇게 찾은 'H41RESPPALDKNWW'는 연준의 BTFP 프로그램 지원 잔액이다. 
start는 자료의 시작, end는 자료의 마지막이다. end는 2025년 말로 정했다. 미래의 날짜를 end로 정하면 FRED에 수록된 자료료 중에 이용 가능한 자료까지만 불러온다.
//   
def는 함수라는 뜻이고 fetch_fred_series()는 함수의 이름이다. 괄호안은 함수에 이용되는 파라미터 값이 들어 간다.
series_id, start_date, end_date를 정해주어야 한다. start_date는 '2022-01-01'이며 start라는 변수에 할당했다.
FRED는 일간자료, 월별자료, 분기별자료, 연간자료 모두 같은 형식으로 날짜를 표시한다. 모두 해당 기간의 첫 날로 쓴다. 예를 들면
2022년 1분기는 '2021-01-01', 2분기는 '2022-04-01'이 된다. 연간자료라면 2023년 자료는 '2023-01-01'로 표시된다. 
def 함수의 마지막 줄에서 불러온 자료를 df라는 dataframe으로 내주는데, df의 첫번 째 열이 'date', 두번 째 열이 series_id이다.
//
'''

start = '2022-01-01'
end = '2025-12-31'

def fetch_fred_series(series_id, start_date=start, end_date=end):
    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json',
        'observation_start': start_date,
        'observation_end': end_date
    }
    r = requests.get(url, params=params)
    data = r.json()

    df = pd.DataFrame(data['observations'])
    df['date'] = pd.to_datetime(df['date'])
    df[series_id] = pd.to_numeric(df['value'], errors='coerce')
    return df[['date', series_id]]

'''
다음은 fetch_fred_series() 함수를 이용해서 데이터를 불러와 dataframe에 할당하는 부분이다. 
FRED에서 'H41RESPPALDKNWW'를 불러와서 df0라는 이름의 dataframe에 할당한다. 'H41RESPPALDKNWW'가 series_id이며 api_key는 앞에서 정의한 사용자의 api_key 값이다. 
FRED에서 검색해보면 'H41RESPPALDKNWW'는 Bank Term Funding Program의 매주 수요일 잔액이라고 되어 있다.  
df0의 첫째 열은 'date', 둘째 열은 'H41RESPPALDKNWW'이 된다. 같은 방식으로 'RIFSPFFNB'를 불러와서 df1이라는 dataframe에 할당한다. 'RIFSPFFNB'이 바로
Federal Funds Effective Rate이다. df1의 첫째 열은 'date', 둘째 열은 'RIFSPFFNB'이 된다.
// 
'''

df0 = fetch_fred_series('H41RESPPALDKNWW',
                        start_date=start, end_date=end)
df1 = fetch_fred_series('RIFSPFFNB',
                        start_date=start, end_date=end)
'''
df0에 자료가 잘 들어왔는지 확인하기 위해 df0의 처음 다섯 줄만 출력해 본다.
dataframe의 구조를 이해하는 데에도 도움이 된다. 자료가 잘 들어왔다면 첫 번째 열의 이름은 date, 두 번째 열의
이름은 H41RESPPALDKNWW로 나온다. 두 번째 줄부터 자료가 나오는데 먼저 인덱스가 나온다. 첫 번째 줄의 인덱스는 0,
날짜는 2022-01-05, 자료는 0.0이다. 인덱스는 각 줄의 페이지 번호 같은 것이다. 현재의 첫 번째 열인 date를 인덱스로
만들기도 한다. 
//

'''

print(df0.head())

'''
        date  H41RESPPALDKNWW///
0 2022-01-05              0.0///
1 2022-01-12              0.0///
2 2022-01-19              0.0///
3 2022-01-26              0.0///
4 2022-02-02              0.0///
//
'''
'''
이제부터 3단계, 그래프를 그리는 부분이다. fig는 그림이라는 정의이고 그림의 이름은 ax인데 괄호안의 1,2는 한 줄에 2개의 그림이 있다는 뜻이다.
그림의 크기는 가로가 8, 세로가 4.5이고 constrained_layout=True는 그림이 꽉차게 보이도록 한다.
//
ax[0]는 첫 번째 그림이며, plot은 선그래프를 의미하고 가로 축에는 df0['date']를, 세로축에 df0['H41RESPPALDKNWW']/1e2를 놓고 선그래프를 그린다. /1e2는 1x10의 제곱 즉 100으로 나누었다는 의미이다.
백만 달러 단위를 억 달러 단위로 바꾸기 위해서이다. 선그래프의 가로 축에 날짜가 들어가고 세로 축에 BTFP잔액이 들어간다. 선그래프에 'BTFP'라는 라벨을 달았고, 붉은 색으로 했고, 선의 굵기는 2이다. 
//
ax[0], 즉 첫 번째 그림에 가로로 선을 하나 그렸는데 y=0에 해당하는 부분이고, 회색이며, 라인스타일이 점선이다. 
다음에 x축에 날짜를 표시하는데 연도만 표시한다. 라벨을 박스에 넣어 표시하고, 박스 좌상단 꼭지점이 비례적으로 가로 0.2, 
세로 0.7쯤에 위치하게 했다. y축의 축 라벨이 숫자로 보이게 했다. 그림의 상단 왼쪽에 (억 달러)라는 단위 표시를 달았고 그래프 왼쪽으로 정렬했으며,
글자의 바닥이 그림 바로 위에 붙도록 했고, 글자색은 검정, 폰트 크기는 12이다. 글자를 비스듬하게 쓰지 않고 가로 쓰기로 했다. 출처를 FRED로 명시했고,
음영구간이 BTFP를 실시한 시기를 의미한다고 표시했다. 가로 세로로 그리드를 그리지 않아서 깔금한 모양이 나오게 했다.
//
'''

fig, ax = plt.subplots(1,2, figsize=(8, 4.5), constrained_layout=True)

ax[0].plot(df0['date'], df0['H41RESPPALDKNWW']/1e2,
           label='BTFP', color='red', lw=2)
ax[0].axhline(y=0, color='gray', linestyle='--')

ax[0].xaxis.set_major_locator(mdates.YearLocator())
ax[0].legend(loc='upper left',bbox_to_anchor=(0.2, 0.7))
ax[0].yaxis.label.set_visible(True)
ax[0].text(0, 1.00, '(억 달러)', ha='left', va='bottom', color='black',
           fontsize=12, rotation=0, transform=ax[0].transAxes)

ax[0].text(0.0, -0.15, "출처: FRED, 음영은 BTFP 실시기간",
           transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(False)

'''
ax[1]이 두 번째 그림인데 가로축에 날짜, 세로축에 실효연방기금금리를 그리도록 했고, 선의 이름을 'Effective Federal Funds Rate'로 달았다.
붉은 선이고 선의 굵기는 2이다. 나머지는 ax[0]에 설명한 것과 유사하다.
'''
ax[1].plot(df1['date'], df1['RIFSPFFNB'],
           label='Effective Federal Funds Rate', color='red', lw=2)
ax[1].axhline(y=0, color='gray', linestyle='--')
ax[1].legend(loc='upper left',bbox_to_anchor=(0.35, 0.7))
ax[1].xaxis.set_major_locator(mdates.YearLocator())

ax[1].text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
           fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(0.0, -0.15, "출처: FRED, 음영은 BTFP 실시기간",
           transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)

'''
첫 번째, 두 번째 그림에 음영구간을 추가했다. 음영의 시작은 2023년 3월 12일이고, 끝은 2024년 3월 11일이다. 연준이 BTFP를 실시했던 시기를 의미한다.
//
'''

from datetime import datetime
shaded_periods = [(datetime(2023, 3, 12),datetime(2024, 3, 11))]

for i in [0,1]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color='gray', alpha=0.2)

'''
그림을 파일로 저장하는 단계이다. 먼저 그림을 저장하기 위해 필요한 os, Image 패키지가 호출된다. 
설치되어 있지 않다면, 이번에 새로 설치해야 한다. 이 파일의 이름을 base_filename 변수에 할당한다.
이 파일의 경우 f2_btfp가 base_filename에 할당된다.

//
'''

import os
from PIL import Image

try:
    base_filename = os.path.splitext(os.path.basename(__file__))[0]
except NameError:
    base_filename = "default_filename"

# 저장 경로를 설정하고 파일 이름을 정해준다. //
image_path_tif = f"pic_tif/{base_filename}.tif"
image_path_jpg = f"pic_jpg/{base_filename}.jpg"

# 저장 경로가 없으면 자동으로 생성하도록 했다. //
os.makedirs("pic_tif", exist_ok=True)
os.makedirs("pic_jpg", exist_ok=True)

# 그래프를 파일로 저장한다. //
plt.savefig(image_path_tif, dpi=300)
plt.savefig(image_path_jpg, dpi=300)

# 그래프를 저장한 그림파일의 색공간을 JPEG와 CMYK로 각각 변환한다. JPEG는 주로 모니터 출력용, CMYK는 인쇄용으로 사용된다.
# 마지막 줄이 그래프를 모니터로 보여준다.
# //

img = Image.open(image_path_jpg).convert("CMYK")
img.save(image_path_jpg, "JPEG")
plt.show()

# //