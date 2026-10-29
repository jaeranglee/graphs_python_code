# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # [그림 8] MMF의 단기국채 투자잔액, 연준과 MMF의 RRP
# ## required file
#   - fred_api.py
#   - plot_def.py
#   - nyfed_rrp_vol.py
# ## required packages
# ```python
# pip install datetime
# ```
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 공통 함수 폴더(codes/defs)를 import 경로에 추가
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
_defs = next(
    d
    for p in (_here, *_here.parents)
    for d in (p / "defs", p / "codes" / "defs")
    if d.is_dir()
)
sys.path.insert(0, str(_defs))

from plot_def import *

# 폰트 설정
set_fonts()

# Fetch series
# ---------------------

from fred_api import fetch_fred_series
from nyfed_rrp_vol import fetch_rrp_vol

start = "2021-01-01"
end = "2025-10-01"
op_type = "Reverse Repo"

# %% [markdown]
# ## FRED series fetched
#   - Liabilities and Capital: Liabilities: Reverse Repurchase Agreements: Week Average (WLRRAA)
#       - Millions of U.S. Dollars,Not Seasonally Adjusted
#       - Frequency:Weekly,Ending Wednesday
#   - Money Market Funds; Treasury Bills; Asset, Level (BOGZ1FL633061110Q)
#       - Units:Millions of Dollars, Not Seasonally Adjusted
#       - Frequency: Quarterly
#   - Federal Debt: Total Public Debt (GFDEBTN)
#       - Units: Millions of Dollars, Not Seasonally Adjusted
#       - Frequency: Quarterly,End of Period
# %%

df_rrp = fetch_fred_series("WLRRAA", start_date=start, end_date=end)
df_mmf = fetch_fred_series("BOGZ1FL633061110Q", start_date=start, end_date=end)
df_debt = fetch_fred_series("GFDEBTN", start_date=start, end_date=end)

# %% [markdown]
# ## Fetch MMF's RRP data from NY FED Markets Data,
# %%
mmf_rrp = fetch_rrp_vol(start_date=start, end_date=end)[1]
mmf_rrp = mmf_rrp[mmf_rrp["Counterparty Type"] == "mmf"]

# total MMF Treasury Bills outstanding to Total US government debt outstanding
df_mmf["ratio"] = df_mmf["BOGZ1FL633061110Q"] / df_debt["GFDEBTN"] * 100

# %% [markdown]
# ## Plot
#   - 그림 0: 첫번째 그림
#       - MMF T-Bill Asset Level
#   - 그림 1: 2번째 그림
#       - MMF Total RRP transaction from NY FED Markets Data
# %%
fig, ax = plt.subplots(1, 2, figsize=(8, 4.5), constrained_layout=True)

ax[0].plot(
    df_mmf["observation_date"],
    df_mmf["BOGZ1FL633061110Q"] / 1e6,
    color="blue",
    lw=2,
    label="MMF 단기국채 투자잔액",
)

# 단위 표시 및 출처:

ax[0].text(
    0,
    1.00,
    "(조 달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)

ax[0].text(
    0.0,
    -0.15,
    "출처: FRED, 음영은 2023년 1월~5월",
    transform=ax[0].transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)

# 범례 (하나만 표시하거나 합칠 수도 있음)
ax[0].legend(loc="upper left")
ax[0].grid(False)

# 2 번째 그림 시작
ax[1].plot(
    mmf_rrp["Date"],
    mmf_rrp["Amount Accepted"] / 1e12,
    label="MMF RRP",
    linestyle="-",
    lw=2,
    color="blue",
)

# 단위 표시 및 출처:

ax[1].text(
    0,
    1.00,
    "(조 달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)

ax[1].text(
    0.0,
    -0.15,
    "출처: NY FED, 음영은 2023년 1월~5월",
    transform=ax[1].transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)

# 범례
ax[1].legend(loc="upper left")
ax[1].grid(False)
ax[1].set_ylim(0.0, 2.5)


# X축 눈금
for i in [0, 1]:
    ax[i].xaxis.set_major_locator(mdates.YearLocator())
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 음영 구간 추가
# 2023.1.1 - 2023.6.1
from datetime import datetime

shaded_periods = [(datetime(2023, 1, 1), datetime(2023, 6, 1))]

for i in [0, 1]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color="gray", alpha=0.2)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
plot_save()
