# %% [markdown]
# # [그림 12] 연방기금금리와 정책금리
# ## required file
#   - fred_api.py
#   - plot_def.py
#   - nyfed_api_rate_volume.py
# %%
from plot_def import *
set_fonts()
# %% [markdown]
# ## Fetch RRP data from FRED
#   - EFFR,
#   - Fed Target upper bound and lower bound
# ## New York Fed Markets Data API 에서 자료 추출
#   - TGCR, EFFR trading volume
# %%
start='2022-01-01'
end='2025-12-31'

from fred_api import fetch_fred_series

df0 = fetch_fred_series('RIFSPFFNB', start_date=start, end_date=end)
df1 = fetch_fred_series('DFEDTARU', start_date=start, end_date=end)
df2 = fetch_fred_series('DFEDTARL', start_date=start, end_date=end)

merged_df = df0.copy()
#---------------------

# 그래프 그리기
fig, ax = plt.subplots(figsize=(9, 4.5),constrained_layout=True)

# 보조 y축: Effective Federal Funds Rate
ax.plot(merged_df['observation_date'], merged_df['RIFSPFFNB'], label='실효연방기금금리', color='blue', lw=2)

ax.fill_between(df1['observation_date'],df1['DFEDTARU'], df2['DFEDTARL'],label='정책금리 범위', alpha=0.2)
ax.text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)

ax.tick_params(axis='y', labelcolor='b')

# 제목 및 레이아웃
ax.text(0.0, -0.15, "출처: FRED",transform=ax.transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')

plt.grid(False)
ax.legend()

# 저장 및 출력
plot_save()