# %% [markdown]
# # [그림 11] 1일물 금리
# ## required file
#   - fred_api.py
#   - plot_def.py
#   - nyfed_api_rate_volume.py
# ## required packages
# ```python
# pip install datetime
# ```
# %%
import matplotlib.dates as mdates
from plot_def import *
set_fonts()

# %% [markdown]
# ## Fetch RRP data from FRED
#   - IORB, SOFR, EFFR,
#   - Fed Target upper bound and lower bound
#   - O/N RRP rates: Overnight Reverse Repurchase Agreements Award Rate: Treasury Securities Sold by the Federal Reserve in the Temporary Open Market Operations (RRPONTSYAWARD)
# ## New York Fed Markets Data API 에서 자료 추출
#   - tgcr, effr
# %%
from fred_api import fetch_fred_series

start='2024-08-01'
end='2025-10-31'

# fetch IORB and SOFR from FRED
iorb = fetch_fred_series('IORB', start_date=start, end_date=end)
sofr = fetch_fred_series('SOFR', start_date=start, end_date=end)

# Effective Federal Funds Rate (EFFR)
effr = fetch_fred_series('EFFR', start_date=start, end_date=end)

target_u = fetch_fred_series('DFEDTARU', start_date=start, end_date=end)
target_l = fetch_fred_series('DFEDTARL', start_date= start, end_date=end)  # Lower Target 추가
target_u['DFEDTARL'] = target_l['DFEDTARL']  # 상하한 결합

rrp = fetch_fred_series("RRPONTSYAWARD", start_date=start, end_date=end)

# New York Fed Markets Data fetch
from nyfed_api_all_rates import fetch_all_secured_rates

# fetch secured over night rates
df_all = fetch_all_secured_rates(start_date=start, end_date=end, rate_type_filter=None)

# tgcr, sofr, bgcr, sofrai, effr, obfr 등 선택가능
tgcr = df_all[df_all["Type"] == 'TGCR'].copy()
effr1 = df_all[df_all["Type"] == "EFFR"].copy()

# 그래프 그리기
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

# 왼쪽:
ax.plot(iorb['observation_date'], iorb['IORB'], label='IORB', lw=1, ls= '-', color='blue')
ax.plot(sofr['observation_date'], sofr['SOFR'], label='SOFR', lw=2, ls=':', color='black')
ax.plot(tgcr['Date'], tgcr['Rate'], label='TGCR', lw=2, color='blue')

ax.plot(effr1['Date'], effr1['Rate'], label='EFFR', lw=2, color='black')
ax.plot(rrp['observation_date'], rrp['RRPONTSYAWARD'], label="O/N RRP", lw=1, ls="--", color='black')

# target rate bound in filled lines
ax.fill_between(target_u['observation_date'], target_u['DFEDTARU'], target_u['DFEDTARL'], color='gray', alpha=0.2, label='Target Range')

ax.legend(loc='upper right', bbox_to_anchor=(1, 1))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.text(0, 1.00, '(%)',  ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
ax.text(0, -0.15, '출처: FRED, NY FED', transform=ax.transAxes, fontsize=10)

# grid with dashed lines
ax.grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.7)

# 저장 및 출력
plot_save()