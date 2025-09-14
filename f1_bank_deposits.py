
'''
이번에는 Yahoo Finance가 제공하는 주식가격 자료를 불러보는 법을 알아본다.
그리고 앞서 FRED API에서 자료를 호출하는 함수를 별도 파일로 저장했는데
이 함수를 다른 파일에서 호출해서 사용하는 사례를 알아본다.
f1_baknk_deposits.py 파일을 열어보자. '[그림 1] 은행 예금잔액과 은행업 ETF가격'을 그려주는 코드이다.
//
Yahoo Finance가 제공하는 주식가격 자료를 불러올 때 yfinance라는 파이썬 패키지를 활용한다.
yfinance는 Yahoo Finance API를 쉽게 이용할 수 있게 만들어 놓은 오픈소스 패키지이다.
yfinace 패키지를 호출하고 yf라고 정의한다. 다른 패키지들은 앞에 설명한 것과 동일하다.
파이썬 코드는 파일을 새로 만들 때마다 필요한 패키지를 호출해야 한다.
'''


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform
import yfinance as yf


# 애플컴퓨터와 윈도우 컴퓨너에서 쓸 수 있는 폰트를 설정해 준다.
# //


if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


'''
fred_api.py라는 이름의 파일에서 fetch_fred_series라는 함수를 불러온다.
'''
from fred_api import fetch_fred_series


'''
이용할 자료의 시작 시점과 마지막 시점을 정했다. 2022년 1월부터 가장 최신 자료까지 불러온다.
'''

start = "2022-01-01"
end = "2025-12-31"


'''
FRED API에서 자료를 불러온다. 은행 예금총액 'DPSACBM027NBOG'를 불러와서 df0에 할당하고,
소규모은행 예금총액 'DPSSCBM027NBOG'를 불러와서 df1에 할당했다. 각각
Deposits, All Commercial Banks 그리고, Deposits, Small Domestically Chartered Commercial Banks에 해당한다.
fetch_fred_serie() 함수에는 파라미터가 3개 들어간다. 맨앞에 series_id 값을 적고, start_date, end_date 순서로 적는다.
//
'''


df0 = fetch_fred_series('DPSACBM027NBOG',
                        start_date=start, end_date=end)
df1 = fetch_fred_series('DPSSCBM027NBOG',
                        start_date=start, end_date=end)

'''
yfince 패키지에서 S&P Banks ETF 주가를 불러오는 곳이다.
S&P Banks ETF의 ticker, KBE를 yfinance 패키지에 주고 결과를 받아서, bkx라는 변수에 할당한다.
개별 주식의 ticker는 검색엔진으로 미리 검색해 놓아야 한다. 정확한 ticker를 넣어야 오류없이 주식가격을 불러온다.
ticker는 미국 주식시장에 상장된 주식마다 붙어있는 식별기호이다. 
//
bkx에 할당된 자료중에 2022년 1월 1일부터 가장 최신 자료를 선별해서 data라는 변수에 할당한다.
data에 들어있는 자료에서 한번 더 2022년 1월 1일부터 2024년 12월 31일까지 자료를 선별했다.
다음에 data변수에 있는 자료의 시작시기와 최종시기를 점검하고,
자료의 처음 10개를 출력해서 확인한다. 
//
다른 주식가격을 알고 싶으면 해당 ticker를 KEB자리에 교체해서 넣으면 된다.
자료 구간을 달리하려면 start, end 날짜를 바꾸면 된다. ticker와 날짜 모두 따옴표 또는 작은따옴표 안에 넣어야 한다.
날짜는 yyyy-mm-dd 형식으로 넣어야 한다.  
'''


bkx = yf.Ticker("KBE")
data = bkx.history(start="2022-01-01", end="2025-12-31")
data = data[(data.index >= "2022-01-01") & (data.index <= "2024-12-31")]

'''
자료가 잘 호출되었는지 확인하기 위해 data로 들어온 자료의 시작일과 종료일을 출력하고,
data에 들어있는 처음 5개 자료를 출력해 본다.
'''

print(data.index.min(), data.index.max())
print(data.head(10))

'''
//
//
자료가 잘 들어왔다면, 자료의 시작일은 2022-01-01, 종료일은 2024-12-31로 나온다.
data의 첫 번째 열의 이름은 Close이며 그 날짜의 주식 종가를 의미한다. data에는 날짜가 인덱스로 사용되었음을 확인할 수 있다.
//
 
'''


'''
지금부터 선그래프를 그리는 코드라인이다. 먼저 그림을 정의해 준다. 1줄에 2개의 그래프가 그려진다. 첫째 그래프에 '은행 예금' 잔액과 '중소은행 예금' 잔액을 선그래프로 그리고,
둘째 그래프에 'S&P Banks ETF'의 가격을 그린다. 
'''


fig, ax = plt.subplots(1,2, figsize=(8, 4.5), constrained_layout=True)

'''
첫 번째 그림이 그려지는 라인이 시작되었. FRED가 제공하는 예금잔액이 10억달러 단위로 되어 있어서 1e3 즉, 1,000으로
나누어 1조 달러 단위로 바꾸어 그렸다. 첫 번째 그림은 y축을 왼쪽과 오른쪽에 그렸다. 전체 은행의 예금 잔액과
중소은행의 예금잔액의 크기가 너무 차이가 나서 하나의 축만 사용하면 모양이 잘 안나오기 때문이다.
첫째 줄이 의미하는 것은 다음과 같다. 
ax_left는 왼쪽 y축이며 ax[0]의 왼쪽 y축에 할당된다.
ax_right는 오른쪽 y 축이하며 ax[0]의 ax_left와 쌍을 이룬다.
첫째 그래프의 x 축에는 df0의 날짜가, 왼쪽 y축에는 df0에 할당된 전체 은행 예금이 그려진다. 
첫째 그래프의 오른 쪽 y축에는 df1에 할당된 중소은행 예금이 그려진다. x축에는 df1의 날짜가 사용된다.
//    
'''


ax_left = ax[0]
ax_right = ax_left.twinx()

ax_left.plot(df0['observation_date'], df0['DPSACBM027NBOG']/1e3,
             label='은행 예금', color='red', lw=2)
ax_right.plot(df1['observation_date'], df1['DPSSCBM027NBOG']/1e3,
              label='중소은행 예금', color='blue', lw=2)


'''
첫 번째 그래프의 x축 날짜 간격, 선그래프 라벨, 단위표시, 자료출처 표시를 지정하는 곳이다. 
'''


ax[0].xaxis.set_major_locator(mdates.YearLocator())
ax_left.legend(loc='upper left',bbox_to_anchor=(0.2, 1.0))
ax_right.legend(loc='upper left',bbox_to_anchor=(0.2, 0.94))
ax_left.yaxis.label.set_visible(True)
ax_left.text(0, 1.00, '(조 달러)', ha='left', va='bottom', color='black',
             fontsize=12, rotation=0, transform=ax[0].transAxes)
ax_right.text(1.0, 1.00, '(조 달러)', ha='right', va='bottom', color='black',
             fontsize=12, rotation=0, transform=ax[0].transAxes)
ax[0].text(0.0, -0.15, "출처: FRED", transform=ax[0].transAxes,
             fontsize=10, ha='left')
ax[0].grid(False)


'''
두 번째 그래프를 그려보는 라인이다. 첫 번째 그래프의 오른쪽에 나오게 된다. yfinance 패키지로 불러온 S&P Banks ETF 가격을 그려준다.
x축이 날짜, y축이 주식가격이다. 앞에서 print()로 확인했듯이 yfinance 패키지로 불러온 자료의 날짜는 
열(column)에 저장되어 있지 않고 각 행의 index로 지정되어 있다. 그래서 x축을 data.index로 할당한 것이다. 
1개의 자료만 그리기 때문에 y축도 당연히 1개이다.
//
'''

ax[1].plot(data.index, data['Close'], label='S&P Banks ETF', color='red', lw=2)



ax[1].legend(loc='upper left',bbox_to_anchor=(0.3, 1))
ax[1].xaxis.set_major_locator(mdates.YearLocator())
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax[1].text(0, 1.00, '(달러)', ha='left', va='bottom', color='black',
        fontsize=12, rotation=0, transform=ax[1].transAxes)

ax[1].text(0.0, -0.15, "출처: Yahoo Finance, S&P",
        transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)

'''
그림을 파일로 저장하는 단계이다. 먼저 그림을 저장하기 위해 필요한 os, Image 패키지가 호출된다. 
설치되어 있지 않다면, 이번에 새로 설치해야 한다. 이 파일의 이름을 base_filename 변수에 할당한다.
이 파일의 경우 f1_bank_deposits가 base_filename에 할당된다.
//
'''


import os
from PIL import Image

# 저장 경로를 설정하고 파일 이름을 정해준다. //
try:
    base_filename = os.path.splitext(os.path.basename(__file__))[0]
except NameError:
    base_filename = "default_filename"

# 저장 경로를 설정하고 파일 이름을 정해준다. //
image_path = f"pic_tif/{base_filename}.tif"
image_path_jpg = f"pic_jpg/{base_filename}.jpg"

# 저장 경로가 없으면 자동으로 생성하도록 했다. //
os.makedirs("pic_tif", exist_ok=True)
os.makedirs("pic_jpg", exist_ok=True)


# 그래프를 파일로 저장한다. //
plt.savefig(image_path, dpi=300)
plt.savefig(image_path_jpg, dpi=300)

# 그래프를 저장한 그림파일의 색공간을 JPEG와 CMYK로 각각 변환한다. JPEG는 주로 모니터 출력용, CMYK는 인쇄용으로 사용된다.
# 마지막 줄이 그래프를 모니터로 보여준다.
# //
img = Image.open(image_path_jpg).convert("CMYK")
img.save(image_path_jpg, "JPEG")
plt.show()
