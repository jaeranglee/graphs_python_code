##[그림4] NYCB 주가와 은행업주가
##[그림5] 2년물 국채금리

import requests

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform

import yfinance as yf

##폰트 설정
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

##FRED 자료 불러오기

from fred_api import fetch_fred_series
start='2022-01-01'
end='2025-12-31'

# Fetch series
# Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity, Quoted on an Investment Basis (DGS2)
df0 = fetch_fred_series('DGS2', start_date=start, end_date=end)

#--------
#Fetch from Yahoo Finance, Bank Stock Prices
#bkx = yf.Ticker("^BKX") # KBW Nasdaq Bank Index
nycb = yf.Ticker('FLG') # NYCB
kbe = yf.Ticker('KBE') #KBE
data = nycb.history(start="2022-01-01", end="2025-12-31")
data1 = kbe.history(start="2022-01-01", end="2025-12-31")
data = data[(data.index >= "2022-01-01") & (data.index <= "2025-12-31")].copy()
data1 = data1[(data1.index >= "2022-01-01") & (data1.index <= "2025-12-31")].copy()

#데이터 기간 확인
print(data.index.min(), data.index.max())
#데이터 열과 행 확인
print(data.head(10))
#---------------------


# Plotting
fig, ax = plt.subplots(1,2, figsize=(8, 4.5), constrained_layout=True)

ax_left = ax[0]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(data.index, data['Close'], label='Flagstar Financial', color='red', lw=2)
ax_right.plot(data1.index, data1['Close'], label='S&P Banks ETF', color='blue', lw=2)


ax[0].xaxis.set_major_locator(mdates.YearLocator())
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
#ax[0].set_xlim([data.index.min(),data.index.max()])

# 단위 표시 및 출처
ax_left.legend(loc='upper left',bbox_to_anchor=(0.2, 1.0))
ax_right.legend(loc='upper left',bbox_to_anchor=(0.2, 0.94))
ax_left.yaxis.label.set_visible(True)

ax_left.text(0, 1.00, '(달러)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)
ax_right.text(1.0, 1.00, '(달러)', ha='right', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)
ax[0].text(0.0, -0.15, "출처: Yahoo Finance, NYSE", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(False)


# Plotting

ax[1].plot(df0['observation_date'], df0['DGS2'], label='2년만기 국채', color='red', lw=2)

ax[1].legend(loc='upper left',bbox_to_anchor=(0.3, 1))
ax[1].xaxis.set_major_locator(mdates.YearLocator())
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[1].text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(0.0, -0.15, "출처: FRED", transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
import os
from PIL import Image


## 현재 작업 중인 파일 이름 추출 (확장자 제거)

try:
    base_filename = os.path.splitext(os.path.basename(__file__))[0]
except NameError:
    base_filename = "default_filename"

# 저장 경로 설정
image_path_tif = f"pic_tif/{base_filename}.tif"
image_path_jpg = f"pic_jpg/{base_filename}.jpg"

# 디렉토리 없으면 자동 생성
os.makedirs("pic_tif", exist_ok=True)
os.makedirs("pic_jpg", exist_ok=True)

# 그래프 저장
plt.savefig(image_path_tif, dpi=300)
plt.savefig(image_path_jpg, dpi=300)

# JPEG → CMYK 변환 후 덮어쓰기
img = Image.open(image_path_jpg).convert("CMYK")
img.save(image_path_jpg, "JPEG")
plt.show()