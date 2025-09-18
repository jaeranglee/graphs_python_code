# [그림 18] 소비자물가와 근원물가

# 같은 디렉토리에 필요한 파일

# plot_def.py
# fred_api.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정
from plot_def import *
set_fonts()

start='2020-01-01'
end='2025-12-31'

# Fetch series

from fred_api import *

df_cpins = fetch_fred_series('CPIAUCNS', start_date=start, end_date=end)

df_corens = fetch_fred_series('CPILFENS', start_date=start, end_date=end)

# Load WTI spot
df_wti = fetch_fred_series('WTISPLC', start_date=start, end_date=end)

#
df_cpis = fetch_fred_series('CPIAUCSL', start_date=start, end_date=end)
df_cores = fetch_fred_series('CPILFESL', start_date=start, end_date=end)

#---------------------

# Calculate YoY inflation rate

df_cpins['YoY_Inflation'] = df_cpins['CPIAUCNS'].pct_change(periods=12) * 100
df_corens['YoY_Inflation'] = df_corens["CPILFENS"].pct_change(periods=12) * 100

df_cpins['YoY_Inflation'] = pd.to_numeric(df_cpins['YoY_Inflation'], errors='coerce')
df_corens['YoY_Inflation'] = pd.to_numeric(df_corens['YoY_Inflation'], errors='coerce')

# Filter for
df_cpins = df_cpins[(df_cpins['observation_date'] >= '2021-01-01')].copy()
df_corens = df_corens[(df_corens['observation_date'] >= '2021-01-01')].copy()

# Convert the observation_date to datetime
df_cpis['observation_date'] = pd.to_datetime(df_cpis['observation_date'])
df_cores['observation_date'] = pd.to_datetime(df_cores['observation_date'])

# Calculate month-to-month inflation rate (as percentage)
df_cpis['MOM_Inflation'] = df_cpis['CPIAUCSL'].pct_change() * 100
df_cores['MOM_Inflation'] = df_cores['CPILFESL'].pct_change() * 100

df_cpis = df_cpis[(df_cpis['observation_date'] >= '2021-01-01')].copy()
df_cores = df_cores[(df_cores['observation_date'] >= '2021-01-01')].copy()

# Identify the specific date
highlight_date = '2024-08'

# Convert date format to match DataFrame
highlight_date = pd.to_datetime(highlight_date)

# Find the corresponding data point in dff

highlight_point_cpins = df_cpins[df_cpins['observation_date'] == highlight_date]
highlight_point_corens = df_corens[df_corens['observation_date'] == highlight_date]

highlight_point_cpis = df_cpis[df_cpis['observation_date'] == highlight_date]
highlight_point_cores = df_cores[df_cores['observation_date'] == highlight_date]


# Plot
# 전년동월비 (왼쪽그림), 전월비(오른쪽)
fig, ax = plt.subplots(1,2, figsize=(9, 4.5), constrained_layout=True )

ax[0].plot(df_cpins['observation_date'], df_cpins['YoY_Inflation'], lw=2, color='blue')
ax[0].plot(df_corens['observation_date'], df_corens['YoY_Inflation'], lw=2, color='r')

# Add horizontal line at y = 2
ax[0].axhline(y=2, color='gray', linestyle='--', linewidth=1)

# Plot the highlighted point with a larger marker
ax[0].scatter(highlight_point_cpins['observation_date'], highlight_point_cpins['YoY_Inflation'],
           color='blue', marker='o', s=100, linewidth=2, label="2024년 8월 소비자물가")
ax[0].scatter(highlight_point_corens['observation_date'], highlight_point_corens['YoY_Inflation'],
           color='r', marker='x', s=100, linewidth=2, label="2024년 8월 근원물가")

# Add a legend for clarity
ax[0].legend()

# Formatting

ax[0].text(0, 1.00, '(%, 전년동월대비)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)

# X축 눈금 표시를 1년 간격으로 설정
ax[0].xaxis.set_major_locator(mdates.YearLocator())  # 1년 간격으로 눈금 표시
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 연도만 표시

ax[0].grid(False)

ax[0].text(0.0, -0.15, "출처: BLS, FRED", transform=ax[0].transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')

# Plotting the inflation rate 전월비 (오른쪽)

ax[1].plot(df_cpis['observation_date'], df_cpis['MOM_Inflation'], lw=2, color='blue')
ax[1].scatter(highlight_point_cpis['observation_date'], highlight_point_cpis['MOM_Inflation'],
           color='blue', marker='o', s=100, linewidth=2, label="2024년 8월 소비자물가")
ax[1].plot(df_cores['observation_date'], df_cores['MOM_Inflation'], lw=2, color='r')
ax[1].scatter(highlight_point_cores['observation_date'], highlight_point_cores['MOM_Inflation'],
           color='r', marker='x', s=100, linewidth=2, label="2024년 8월 근원물가")

# Add horizontal line at y = 2
ax[1].axhline(y=0, color='gray', linestyle='--', linewidth=1)
# 단위 표시
ax[1].text(0, 1.00, '(%, 전월대비)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
# 출처표시
ax[1].text(0.0, -0.15, "출처: BLS, FRED", transform=ax[1].transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')

# X축 눈금 표시를 1년 간격으로 설정
ax[1].xaxis.set_major_locator(mdates.YearLocator())  # 1년 간격으로 눈금 표시
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 연도만 표시

plt.grid(False)
plt.legend()


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()