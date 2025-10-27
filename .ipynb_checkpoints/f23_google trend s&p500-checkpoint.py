# %% [markdown]
# # [그림 23] 미국 예외주의에 대한 구글 트렌드와 S&P500
# ## required file
#   - plot_def.py
#   - fred_api.py
# ## data 디렉토리에 필요한 파일
#   - f_google_trend.csv : 구글 트렌드
# %%
from plot_def import *
set_fonts()

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform

start='2000-01-01'
end='2025-12-31'

from fred_api import fetch_fred_series
# %% [markdown]
# ## Fetch data from FRED
#   - S&P 500 (SP500)
# %%
df_sp = fetch_fred_series('SP500', start_date=start, end_date=end)

# Load the CSV file
file_path = "data/f_google_trend.csv"
df = pd.read_csv(file_path, skiprows=2)


df = df.rename(columns={
    '월': 'Date',
    'American Exceptionalism: (전 세계)': 'Google_Trend'
})


# Convert columns to appropriate data types
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m')

# Filter data from 2020 to April 2025

selected_terms_to_plot = ['observation_date', 'SP500']
df_sp = df_sp.dropna(subset=selected_terms_to_plot)[selected_terms_to_plot].copy()

df_filtered = df[(df['Date'] >= '2021-01-01') &
                 (df['Date'] <= '2025-06-01')].copy()
df_sp_filtered = df_sp[(df_sp['observation_date'] >= '2021-01-01') &
                       (df_sp['observation_date'] <= '2025-06-01')].copy()

# bplot: two y-axes

fig, ax = plt.subplots(figsize=(9, 4.5),constrained_layout=True)

ax_left = ax
ax_right = ax_left.twinx()  # Create right-side y-axis
ax_left.plot(df_filtered['Date'], df_filtered['Google_Trend'], label='Google Trend: American Exceptionalism(좌측)', color='blue', lw=2)
ax_left.text(0, 1.00, '(구글트렌드, 전세계)', ha='left', va='bottom', color='blue',
         fontsize=12, rotation=0, transform=ax.transAxes)
ax_left.yaxis.label.set_visible(True)

ax_right.plot(df_sp_filtered['observation_date'], df_sp_filtered['SP500'], label='S&P500(우측)', color='black', lw=1.5)

ax.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)

ax_right.text(1, 1.00, '(S&P 500 지수)', ha='right', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)

ax_right.text(0, -0.15, "출처: Google, FRED", #transform=plt.gcf().transFigure,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black', rotation=0, transform=ax.transAxes)

ax_left.legend(loc='upper left',bbox_to_anchor=(0.4, 0.99))
ax_right.legend(loc='upper left',bbox_to_anchor=(0.4, 0.899))

ax.xaxis.set_major_locator(mdates.YearLocator())

plt.grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()