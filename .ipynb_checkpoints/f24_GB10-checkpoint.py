# %% [markdown]
# # [그림 24] 10년물 미국채 수익률과 S&P500
# ## required file
#   - plot_def.py
#   - fred_api.py
# %%
from plot_def import *
set_fonts()

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from fred_api import fetch_fred_series

start='2023-01-01'
end='2025-09-30'
# %% [markdown]
# ## Fetch data from FRED
#   - S&P 500 (SP500)
#   - T-Bill 10y (DGS10)
# %%
dgs10_df = fetch_fred_series('DGS10', start_date=start, end_date=end)
sp500_df = fetch_fred_series('SP500', start_date=start, end_date=end)

# 날짜 기준으로 두 데이터프레임 병합 (공통 날짜 기준)
merged_df = pd.merge(dgs10_df, sp500_df, on='observation_date', how='inner')

selected_terms_to_plot = ['observation_date', 'DGS10', 'SP500']
merged_df = merged_df.dropna(subset=selected_terms_to_plot)[selected_terms_to_plot].copy()


# 그래프 그리기
fig, ax1 = plt.subplots(figsize=(10, 5), constrained_layout=True)

# DGS10 (10년물 금리)
ax1.plot(merged_df['observation_date'], merged_df['DGS10'], color='blue', label='10년물 국채수익률(좌축)', lw=2)

#ax1.set_ylabel('TB10 (%)', color='blue', fontsize=12)
ax1.text(0, 1.00, '(10년물 국채수익률 ,%)', ha='left', va='bottom', color='blue',
         fontsize=12, rotation=0, transform=ax1.transAxes)
ax1.tick_params(axis='y', labelcolor='blue')

# 보조 y축: S&P 500
ax2 = ax1.twinx()
ax2.plot(merged_df['observation_date'], merged_df['SP500'], color='black', label='S&P 500(우축)')

ax2.set_ylim(3500,6700)

ax2.text(1, 1.00, '(S&P 500 지수)', ha='right', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax1.transAxes)

ax2.tick_params(axis='y', labelcolor='black')

# 출처

ax2.text(0.0, -0.15, "출처: FRED",
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black', transform=ax1.transAxes)
ax1.legend(loc='upper left',bbox_to_anchor=(0.04, 0.8))
ax2.legend(loc='upper left',bbox_to_anchor=(0.04, 0.74))

ax1.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)

# X축 눈금

ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
#ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

#fig.tight_layout()

plt.grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()