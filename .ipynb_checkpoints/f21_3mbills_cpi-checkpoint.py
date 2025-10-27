# [그림 21] 제2차 세계대전 전후 국채 수익률, 소비자물가 상승률

# 같은 디렉토리에 필요한 파일

# plot_def.py
# fred_api.py


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 폰트 설정
from plot_def import *
set_fonts()


# API를 이용해 자료를 요청하기 위한 라이브러리
start='1941-01-01'
end='1952-01-01'

from fred_api import *


# FRED api로 한번에 1개의 시리즈만 호출 가능
# Fetch series
# CPI (not seasonally adjusted)
df_cpins = fetch_fred_series('CPIAUCNS', start_date=start, end_date=end)

# Load 3 Month T-bill
df0 = fetch_fred_series('TB3MS', start_date=start, end_date=end)
#---------------------

# CPI YoY 계산
df_cpins['yoy_cpi'] = (df_cpins['CPIAUCNS'].pct_change(periods=12) * 100).copy()
cpi = df_cpins


# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽:

ax[0].plot(df0['observation_date'], df0['TB3MS'], label='T-bill 3개월', lw=2, color='blue')


ax[0].legend(loc='upper left',bbox_to_anchor=(0, 1.0))
ax[0].text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)

ax[0].xaxis.set_major_locator(mdates.YearLocator(2))
#ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[0].text(0.0, -0.15, "출처: FRED, 음영은 경기침체 기간", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(False)

# 오른쪽: CPI

ax[1].plot(cpi['observation_date'], cpi['yoy_cpi'], label='소비자물가', lw=2, color='blue')

ax[1].legend(loc='upper left',bbox_to_anchor=(0, 1))
ax[1].xaxis.set_major_locator(mdates.YearLocator(2))

# 단위 표시 및 출처
ax[1].text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(0.0, -0.15, "출처: FRED, 음영은 경기침체 기간", transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)

# recession 기간표시
recession_periods = nber_recession(start=start, end=end)

# 두 그래프에 음영 처리
for peak, trough in recession_periods:
    ax[0].axvspan(peak, trough, color='gray', alpha=0.3)
    ax[1].axvspan(peak, trough, color='gray', alpha=0.3)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()