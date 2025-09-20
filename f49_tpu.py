# [그림 49] TPU, 소비자심리지수, 구글트렌드

# 같은 디렉토리에 필요한 파일

# plot_def.py
# fred_api.py               : FRED, api key required

# data 디렉토리에 필요한 파일
# f_google_trend_recession.csv

import pandas as pd
import matplotlib.pyplot as plt

import matplotlib.dates as mdates
import platform


# Set font depending on the platform
from plot_def import *
set_fonts()

# FRED data fetch def 호출

from fred_api import fetch_fred_series

start = '2024-01-01'
end = '2025-12-31'

# Fetch FRED series

# University of Michigan: Consumer Sentiment (UMCSENT)
df_m = fetch_fred_series('UMCSENT', start_date=start, end_date=end)

# Economic Policy Uncertainty Index for United States (USEPUINDXD), Daily
df_u = fetch_fred_series('USEPUINDXD', start_date=start, end_date=end)

#Economic Policy Uncertainty Index: Categorical Index: Trade policy (EPUTRADE), Monthly
df2 = fetch_fred_series('EPUTRADE', start_date=start, end_date=end)


# Plot the First Plot for TPU, Michigan

fig, ax = plt.subplots(1,2, figsize=(9, 4.5), constrained_layout=True )

# First subplot: two y-axes
ax_left = ax[0]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(df2['observation_date'], df2['EPUTRADE'], label='경제정책 불확실성지수(좌측)', color='blue', lw=2)
ax_left.text(0, 1.00, '(불확실성지수)', ha='left', va='bottom', color='blue',
         fontsize=12, rotation=0, transform=ax[0].transAxes)
ax_left.yaxis.label.set_visible(True)


ax_right.plot(df_m['observation_date'], df_m['UMCSENT'], label='미시건대 소비자심리지수(우측)', color='red', lw=1.5)
ax_right.text(1, 1.00, '(심리지수)', ha='right', va='bottom', color='red',
         fontsize=12, rotation=0, transform=ax[0].transAxes)

ax_right.text(0.0, -0.15, "출처: Baker, Scott R. 외, FRED",
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black', transform=ax[0].transAxes)

ax_left.legend(loc='upper left',bbox_to_anchor=(0, 0.5))
ax_right.legend(loc='upper left',bbox_to_anchor=(0, 0.44))

plt.grid(False)
#plt.tight_layout()

# the Second plot for google trend in recession
# Load the CSV file

file_path = "data/f_google_trend_recession.csv"
df2 = pd.read_csv(file_path)

# Clean and prepare the data
df2 = df2.iloc[1:].copy()  # Remove the first row (in-data header)
df2.columns = ['Date', 'Google_Trend']

# Convert columns to appropriate data types
df2['Date'] = pd.to_datetime(df2['Date'])
df2['Google_Trend'] = pd.to_numeric(df2['Google_Trend'], errors='coerce')


# Filter data from 2020 to April 2025
df_filtered = df2[(df2['Date'] >= '2024-01-01')]

# Plot the Second plot.

ax[1].plot(df_filtered['Date'], df_filtered['Google_Trend'], label='Google Trend', color='blue', lw=2)

ax[1].text(0, 1.00, '(구글트렌드=recession, 미국기준)', ha='left', va='bottom', color='blue',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(0, -0.15, "출처: Google", #transform=plt.gcf().transFigure,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black', rotation=0, transform=ax[1].transAxes)
plt.grid(False)

for i in [0,1]:
    ax[i].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))



# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()