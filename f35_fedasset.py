# [그림 35] 연준의 총자산 규모

# 같은 디렉토리에 있어야 하는 함수 파일

#
# plot_def.py
# fred_api.py

import pandas as pd

import matplotlib.pyplot as plt

import matplotlib.ticker as ticker
#import matplotlib.dates as mdates

# Set font depending on the platform
from plot_def import *
set_fonts()


# api를 이용해 FRED 자료를 호출하기 위한 루틴

start='2018-01-01'
end='2025-12-31'

# FRED api로 한번에 1개의 시리즈만 호출 가능
# Fetch series
# S&P 500 (SP500)
df0 = fetch_fred_series('RESPPANWW', start_date=start, end_date=end)
df1 = fetch_fred_series('WSHOTSL', start_date=start, end_date=end)
df2 = fetch_fred_series('WSHOMCB', start_date=start, end_date=end)


df_filtered=pd.merge(df0, df1, on='observation_date')
df_filtered=pd.merge(df_filtered, df2, on='observation_date').copy()

df_filtered['RESPPANWW'] = pd.to_numeric(df_filtered['RESPPANWW'], errors='coerce') / 1e6
df_filtered['WSHOTSL'] = pd.to_numeric(df_filtered['WSHOTSL'], errors='coerce') / 1e6
df_filtered['WSHOMCB'] = pd.to_numeric(df_filtered['WSHOMCB'], errors='coerce') / 1e6


#df_filtered['WSHOMCB'] = pd.to_numeric(df_filtered['WSHOMCB'], errors='coerce') / 1e6 + df_filtered['WSHOTSL']
df_filtered['Other'] = df_filtered['RESPPANWW'] - (df_filtered['WSHOMCB']  + df_filtered['WSHOTSL'])


# Custom labels for Korean legend
label_map = {
#    'RESPPANWW': '총자산',
    'WSHOTSL': '미국채',
    'WSHOMCB': '모기지증권',
    'Other': '기타'
}


df_all = df_filtered[label_map.keys()].copy()

df_all.rename(columns=label_map, inplace=True)
print(df_all)
print(df_all.info())


# Plot
fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True )


df_all.plot.area(ax=ax, stacked=True, alpha=0.6)
ax.plot(df_filtered.index, df_filtered['RESPPANWW'], label='총자산', lw=2, color='green')

# Formatting
# ax.set_title('Level of Fed Total Asset')
ax.set_xlabel('')

ax.text(0, 1.00, '(조 달러)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)


# Turn off scientific notation on y-axis
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))


ax.grid(False)
ax.legend()


ax.text(0.0, -0.15, "출처: Federal Reserve Bank of St. Louis", transform=ax.transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
# Last executed at: 2025-09-20 23:03:26