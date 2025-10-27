# %% [markdown]
# # [그림 51] 실질 달러인덱스, 금 현물가격, 실질실효 유로인덱스
# ## 같은 디렉토리에 필요한 file
#   - plot_def.py : 한글폰트 추가, 그래프 저장
#   - fred_api.py       : FRED, api key required
#   - bok_ecos_api.py   : Bank of Korea, ECOS Data, api key required
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정
from plot_def import *
set_fonts()

start='2000-01-01'
end='2025-12-31'

# Fetch series from FRED
from fred_api import fetch_fred_series

# %% [markdown]
# ## FRED 자료 추출
# - Nominal Broad U.S. Dollar Index (DTWEXBGS)
# - Real Broad Dollar Index (RTWEXBGS)
# - Real Broad Effective Exchange Rate for Euro Area (RBXMBIS)
# %%
dbxy_df = fetch_fred_series('DTWEXBGS', start_date=start, end_date=end)

df0 = fetch_fred_series('RTWEXBGS', start_date=start, end_date=end)

df2 = fetch_fred_series('RBXMBIS', start_date=start, end_date=end)

# %% [markdown]
# ## ECOS 자료 추출
# - ["Gold", "902Y003", "040101", "M"]  # Gold Spot Price
# %%
from bok_ecos_api import fetch_ecos_series

series_list = [
    ["Gold", "902Y003", "040101", "M"]  # Gold data
]


dfs = {}

for name, stat_code, item_code, cycle in series_list:
    dfs[name] = fetch_ecos_series(name, stat_code, item_code, cycle,
                                 start_date=start, end_date=end)


# 중복 검증


for name in dfs:
    dfs[name] = dfs[name].drop_duplicates(subset='Date').reset_index(drop=True)

for name, df in dfs.items():
    dup_count = df.duplicated().sum()
    print(f"{name}: {dup_count} duplicates")

# %% [markdown]
# ## IMF 자료 추출
# - Gold Price from IMF Data (optional)
# ```python
# from imf_api import fetch_imf_data
#
# gold = fetch_imf_data(data_set='IMF.RES,PCPS', country_id='G001',
#                       indicator_id='PGOLD',unit_id='USD',
#                       start_period=start, end_period=end,
#                       cycle='M')
# gold = gold.rename(columns={'OBS_VALUE': 'Value'})
# ```
# %%
# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: 달러인덱스
ax[0].plot(df0['observation_date'], df0['RTWEXBGS'], label='실질 달러인덱스', lw=2, color='blue')
ax[0].plot(dbxy_df['observation_date'], dbxy_df['DTWEXBGS'], label='명목 달러인덱스', lw=1, color='black')

ax[0].legend()
ax[0].xaxis.set_major_locator(mdates.YearLocator(3))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[0].text(0, 1.00, '(2006=100)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)
ax[0].text(0.0, -0.15, "출처: FRED", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(False)


#오른쪽, y축이 2개

ax_left = ax[1]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(dfs['Gold']['Date'], dfs['Gold']['Value'], label='금', lw=2, color='blue', alpha=1.0)
ax_right.plot(df2['observation_date'], df2['RBXMBIS'], label='실질실효 유로인덱스', lw=2, color='black')

ax_left.legend(loc='upper left',bbox_to_anchor=(0.4, 1.0))
ax_right.legend(loc='upper left',bbox_to_anchor=(0.4, 0.93))

# 단위 표시
ax_left.text(0.12, 1.00, '($/oz)', ha='right', va='bottom', color='red',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax_right.text(1, 1.00, '(2020=100)', ha='right', va='bottom', color='orange',
         fontsize=12, rotation=0, transform=ax[1].transAxes)


ax[1].xaxis.set_major_locator(mdates.YearLocator(3))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))


# 출처

ax[1].text(0.0, -0.15, "출처: BOK ECOS, FRED", transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()