# [그림 55] 트럼프 대통령 재임기간 소비자물가, WTI, 달러인덱스 상승률

# 같은 디렉토리에 필요한 파일

# plot_def.py
# fred_api.py       : FRED, api key required


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 한글 폰트 설정
from plot_def import *
set_fonts()

start='2015-01-01'
end='2026-01-01'

# Fetch series
#---------------------
from fred_api import fetch_fred_series

# 각 시리즈에서 필요한 열 추출
bopimp = fetch_fred_series('BOPTIMP', start_date=start, end_date=end)
imp0004 = fetch_fred_series('IMP0004', start_date=start, end_date=end)
businv = fetch_fred_series('BUSINV', start_date=start, end_date=end)



# Load the Excel file
# 소비자물가지수, 근원물가지수, not seasonally adjusted
df_cpins = fetch_fred_series('CPIAUCNS', start_date=start, end_date=end)
df_corens = fetch_fred_series('CPILFENS', start_date=start, end_date=end)

# 달러인덱스
bdxy_df = fetch_fred_series('DTWEXBGS', start_date=start, end_date=end)

# 소비자물가지수, 근원물가지수, seasonally adjusted
df_cpis = fetch_fred_series('CPIAUCSL', start_date=start, end_date=end)
df_cores= fetch_fred_series('CPILFESL', start_date=start, end_date=end)

# WTI spot
df_wti = fetch_fred_series('MCOILWTICO', start_date=start, end_date=end)


# Set it as index
bdxy_df.set_index('observation_date', inplace=True)

#resample daily dollar index to monthly average
bdxy_df = bdxy_df.resample('ME').mean().copy()
bdxy_df = bdxy_df.reset_index()

# Calculate YoY inflation rate

df_cpins['YoY_Inflation'] = df_cpins['CPIAUCNS'].pct_change(periods=12) * 100
df_corens['YoY_Inflation'] = df_corens["CPILFENS"].pct_change(periods=12) * 100
bdxy_df['YoY_Inflation'] = bdxy_df["DTWEXBGS"].pct_change(periods=12) * 100

df_cpins['YoY_Inflation'] = pd.to_numeric(df_cpins['YoY_Inflation'], errors='coerce')
df_corens['YoY_Inflation'] = pd.to_numeric(df_corens['YoY_Inflation'], errors='coerce')
bdxy_df['YoY_Inflation'] = pd.to_numeric(bdxy_df['YoY_Inflation'], errors='coerce')

# Calculate month-to-month inflation rate (as percentage)
df_cpis['MOM_Inflation'] = df_cpis['CPIAUCSL'].pct_change() * 100
df_cores['MOM_Inflation'] = df_cores['CPILFESL'].pct_change() * 100

# Filter for >=2016

df_cpis = df_cpis[(df_cpis['observation_date'] >= '2016-01-01')].copy()
df_cores = df_cores[(df_cores['observation_date'] >= '2016-01-01')].copy()

# Calculate Year over Year WTI rate (as percentage)
df_wti['YoY_Inflation'] = df_wti['MCOILWTICO'].pct_change(12) * 100
df_wti['YoY_Inflation'] = pd.to_numeric(df_wti['YoY_Inflation'], errors='coerce')

# Filter for
df_wti = df_wti[(df_wti['observation_date'] >= '2016-01-01')].copy()


# Plot
# 전년동월비 (왼쪽그림), 전월비(오른쪽)
fig, ax = plt.subplots(1,2, figsize=(9, 4.5), constrained_layout=True )

ax[0].plot(df_cpins['observation_date'], df_cpins['YoY_Inflation'], color='blue', lw=2, label='소비자물가')
ax[0].plot(df_corens['observation_date'], df_corens['YoY_Inflation'], color='r', lw=2, label='근원물가')

# Add horizontal line at y = 2
ax[0].axhline(y=2, color='gray', linestyle='--', linewidth=1)

# Add a legend for clarity
ax[0].legend(loc='upper left')


# Formatting

ax[0].text(0, 1.00, '(%, 전년동월대비)', ha='left', va='bottom', color='blue',
         fontsize=12, rotation=0, transform=ax[0].transAxes)


# X축 눈금 표시를 1년 간격으로 설정
ax[0].xaxis.set_major_locator(mdates.YearLocator(2))  # 1년 간격으로 눈금 표시
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 연도만 표시

ax[0].grid(False)

ax[0].text(0.0, -0.15, "출처: BLS, FRED; 음영은 트럼프 태통령 재임기", transform=ax[0].transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')


# 두 번째 subplot (WTI + Dollar Index)

ax2 = ax[1].twinx()  # 오른쪽 y축

# WTI (왼쪽 축)
ax[1].plot(df_wti['observation_date'], df_wti['YoY_Inflation'], lw=2, color='blue', label='WTI')
ax[1].axhline(y=0, color='gray', linestyle='--', linewidth=1)

# X축 눈금
ax[1].xaxis.set_major_locator(mdates.YearLocator(2))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Dollar Index (오른쪽 축)
ax2.plot(bdxy_df['observation_date'], bdxy_df['YoY_Inflation'], lw=2, color='red', label='달러인덱스')
ax2.set_ylim(-10, 31.4)

# 음영 구간 추가
from datetime import datetime
shaded_periods = [
    (datetime(2017, 1, 1), datetime(2020, 12, 31)),
    (datetime(2025, 1, 1), datetime(2025, 12, 31))]

for i in [0,1]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color='gray', alpha=0.2)

# 단위 표시 및 출처
ax[1].text(0, 1.00, '(%, 전년동월대비)', ha='left', va='bottom', color='blue',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(1, 1.0, '(%, 전년동월대비)', ha='right', va='bottom', color='red',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(0.0, -0.15, "출처: FRED; 음영은 트럼프 태통령 재임기", transform=ax[1].transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')

# 범례 (하나만 표시하거나 합칠 수도 있음)
ax[1].legend(loc='upper left')
ax2.legend(loc='upper right')
ax[1].grid(False)
ax2.grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()