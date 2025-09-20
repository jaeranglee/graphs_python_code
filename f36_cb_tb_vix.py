# [그림 36] 단기 자금시장 유동성과 주식시장 변동성

# 같은 디렉토리에 있어야 하는 함수 파일

# fred_api.py
# plot_def.py


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform

# 한글 폰트 설정

# Set font depending on the platform
from plot_def import *
set_fonts()


start = '2021-01-01'
end = '2025-12-31'

from fred_api import fetch_fred_series

# Fetch series
# Import Price Index (End Use): All Commodities (IR)
df0 = fetch_fred_series('DTB3', start_date=start, end_date=end)

df2 = fetch_fred_series('RIFSPPFAAD90NB', start_date=start, end_date=end)


# CBOE DJIA Volatility Index (VXDCLS)
df4 = fetch_fred_series('VXDCLS', start_date=start, end_date=end)

#---------------------

# CP - TB

df0= pd.merge(df0, df2, on='observation_date', how='inner').copy()
df0= pd.merge(df0, df4, on='observation_date', how='inner').copy()

selected_terms_to_plot = ['observation_date', 'DTB3', 'RIFSPPFAAD90NB', 'VXDCLS']
df0 =df0.dropna(subset=selected_terms_to_plot)[selected_terms_to_plot].copy()

df0['cp'] = df0['RIFSPPFAAD90NB'] - df0['DTB3']


# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: cp, sofr
ax[0].plot(df0['observation_date'], df0['cp'], label='3개월 CP-TB', lw=2, color='blue')

ax[0].axhline(y=0, color='gray', linestyle='--')
ax[0].legend()
ax[0].xaxis.set_major_locator(mdates.YearLocator(1))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[0].text(0, 1.00, '(%p)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)
ax[0].text(0.0, -0.15, "출처: FRED", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(False)

# 오른쪽: VIX

ax[1].plot(df0['observation_date'], df0['VXDCLS'], label='VIX', lw=2, color='red')

ax[1].legend()
ax[1].xaxis.set_major_locator(mdates.YearLocator(1))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))



# 단위 표시 및 출처

ax[1].text(0.0, -0.15, "출처: FRED", transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()