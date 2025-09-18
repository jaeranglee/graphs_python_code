# [그림 22] M2 증가율, 연방기금금리, 소비자물가 상승률

# 필요한 file

# fred_api.py : FRED에서 data fetch
# plot_def.py : 한글폰트 추가, 그래프 저장, recession 구간 표시

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 폰트 설정
from plot_def import *
set_fonts()

# fetch fred series

start='1968-01-01'
end='1980-01-01'

from fred_api import *

## M2, EFFR 데이터 준비
df0 = fetch_fred_series('MYAGM2USM052N', start_date=start, end_date=end)

df1 = fetch_fred_series('RIFSPFFNB', start_date=start, end_date=end)

df_cpins = fetch_fred_series('CPIAUCNS', start_date=start, end_date=end)
#---------------------

df0['yoy_m2'] = df0['MYAGM2USM052N'].pct_change(periods=12) * 100

# 필요한 열 추출
m2 = df0[['observation_date', 'yoy_m2']].copy()

df1.set_index('observation_date', inplace=True)

df1 = df1.resample('ME').mean().copy()
ffr = df1.copy()

# YoY 계산
df_cpins['yoy_cpi'] = df_cpins['CPIAUCNS'].pct_change(periods=12) * 100
cpi=df_cpins.copy()

# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: M2, EFFR

ax_left = ax[0]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(m2['observation_date'], m2['yoy_m2'], label='M2', lw=2, color='red')
ax_right.plot(ffr.index, ffr['RIFSPFFNB'], label='연방기금금리', lw=2, color='blue')

ax_left.legend(loc='upper left',bbox_to_anchor=(0, 1.0))
ax_right.legend(loc='upper left',bbox_to_anchor=(0, 0.94))
ax_left.yaxis.label.set_visible(True)

ax_left.text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)
ax_right.text(1, 1.00, '(%)', ha='right', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)

ax[0].xaxis.set_major_locator(mdates.YearLocator(2))
#ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[0].text(0.0, -0.15, "출처: FRED, 음영은 경기침체 기간", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(False)

# 오른쪽: CPI

ax[1].plot(cpi['observation_date'], cpi['yoy_cpi'], label='소비자물가', lw=2, color='red')

ax[1].legend(loc='upper left',bbox_to_anchor=(0, 1))

ax[1].xaxis.set_major_locator(mdates.YearLocator(2))

# 단위 표시 및 출처
ax[1].text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(0.0, -0.15, "출처: FRED, 음영은 경기침체 기간", transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)

# USREC 기준으로 recession 음영 처리 (확장기: 0, 침체기: 1)

recession_periods = nber_recesssion(start=start, end=end)

# 두 그래프에 음영 처리
for peak, trough in recession_periods:
    ax[0].axvspan(peak, trough, color='gray', alpha=0.3)
    ax[1].axvspan(peak, trough, color='gray', alpha=0.3)



# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()