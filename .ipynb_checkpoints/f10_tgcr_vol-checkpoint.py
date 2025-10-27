# %% [markdown]
# # [그림 10] MMF의 RRP와 TGCR 거래 규모
# ## required file
#   - fred_api.py
#   - plot_def.py
#   - nyfed_api_rate_volume.py
#   - nyfed_rrp_vol.py
# ## required packages
# ```python
# pip install datetime
# ```
# %%
import matplotlib.dates as mdates
from plot_def import *
set_fonts()

# %% [markdown]
# ## New York Fed Markets Data API 에서 자료 추출
#   - tgcr, sofr, bgcr, effr
# ## Fetch RRP data from FRED
#   - Liabilities and Capital: Liabilities: Reverse Repurchase Agreements: Week Average (WLRRAA)
#       - Units: Millions of U.S. Dollars,
#       - Not Seasonally Adjusted
#       - Frequency: Weekly,
# %%
from nyfed_api_rate_volume import fetch_all_secured_rates_vol
from nyfed_rrp_vol import fetch_rrp_vol
from fred_api import fetch_fred_series

# 사용자 정의 기간

start = "2020-01-01"
end = "2025-10-01"

# Fetch Volume data from NY FED Markets Data
df_all = fetch_all_secured_rates_vol(start_date=start, end_date=end)

tgcr = df_all[df_all["Type"] == "TGCR"].copy()
bgcr = df_all[df_all["Type"] == "BGCR"].copy()
sofr = df_all[df_all["Type"] == "SOFR"].copy()
effr = df_all[df_all["Type"] == "EFFR"].copy()

df_rrp = fetch_fred_series('WLRRAA', start_date=start, end_date=end)

# Fetch Total RRP data from NY FED Markets Data,
ny_rrp = fetch_rrp_vol(start_date=start, end_date=end)[0]

# Fetch MMF's RRP data from NY FED Markets Data,
mmf_rrp = fetch_rrp_vol(start_date=start, end_date=end)[1]
mmf_rrp = mmf_rrp[mmf_rrp['Counterparty Type']=='mmf'].copy()


# 시각화
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)


ax_left = ax
ax_right = ax_left.twinx()  # Create right-side y-axis

#왼쪽 TGCR volume
ax_left.plot(tgcr['Date'], tgcr['Volume']/1e3, label='TGCR trading volume', lw=2, color='black')

# 오른쪽: FED RRP total volume, FED RRP with mmf volume
ax_right.plot(ny_rrp['Date'], ny_rrp['Total Volume']/1e12, label='RRP Total', linestyle=':', lw=2, color='black')
ax_right.plot(mmf_rrp['Date'], mmf_rrp['Amount Accepted']/1e12, label='MMF RRP', linestyle='-', lw=2, color='blue')

ax_right.set_ylim(-0.1,3)
ax_left.set_ylim(-0.1,3)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

ax_left.text(0, 1.00, '(조 달러)', ha='left', va='bottom',transform=ax.transAxes, fontsize=12, color='black')
ax_right.text(1, 1, '(조 달러)', ha='right', va='bottom', transform=ax.transAxes, fontsize=12, color='black')
ax_left.legend(loc='upper left',bbox_to_anchor=(0.0, 0.85))
ax_right.legend(loc='upper left',bbox_to_anchor=(0.0, 0.99))

ax.text(0, -0.15, '출처: NY FED', transform=ax.transAxes, fontsize=10)
ax.grid(True, linestyle='--', color='gray', alpha=0.3)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
plot_save()