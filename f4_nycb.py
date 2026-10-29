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
# # [그림4] NYCB 주가와 은행업주가
# # [그림5] 2년물 국채금리
# ## required file
#   - fred_api.py
#   - plot_def.py
# ## required packages
# ```python
# pip install yfinance
# ```
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import yfinance as yf

##폰트 설정

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

set_fonts()

from fred_api import fetch_fred_series

start = "2022-01-01"
end = "2025-10-01"

# %% [markdown]
# ## Fetch data from FRED
#   - Market Yield on U.S. Treasury Securities at 2-Year Constant Maturity, Quoted on an Investment Basis (DGS2)
# ## Fetch from Yahoo Finance, Bank Stock Prices
#   - bkx = yf.Ticker("^BKX") # KBW Nasdaq Bank Index (optional)
# %%
df0 = fetch_fred_series("DGS2", start_date=start, end_date=end)

nycb = yf.Ticker("FLG")  # NYCB
kbe = yf.Ticker("KBE")  # KBE
data = nycb.history(start="2022-01-01", end="2025-12-31")
data1 = kbe.history(start="2022-01-01", end="2025-12-31")
data = data[(data.index >= "2022-01-01") & (data.index <= "2025-12-31")].copy()
data1 = data1[(data1.index >= "2022-01-01") & (data1.index <= "2025-12-31")].copy()

# 데이터 기간 확인
print(data.index.min(), data.index.max())
# 데이터 열과 행 확인
print(data.head(10))
# ---------------------

# Plotting
fig, ax = plt.subplots(1, 2, figsize=(8, 4.5), constrained_layout=True)

ax_left = ax[0]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(data.index, data["Close"], label="Flagstar Financial", color="black", lw=2)
ax_right.plot(data1.index, data1["Close"], label="S&P Banks ETF", color="blue", lw=2)


ax[0].xaxis.set_major_locator(mdates.YearLocator())
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
# ax[0].set_xlim([data.index.min(),data.index.max()])

# 단위 표시 및 출처
ax_left.legend(loc="upper left", bbox_to_anchor=(0.2, 1.0))
ax_right.legend(loc="upper left", bbox_to_anchor=(0.2, 0.94))
ax_left.yaxis.label.set_visible(True)

ax_left.text(
    0,
    1.00,
    "(달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax_right.text(
    1.0,
    1.00,
    "(달러)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax[0].text(
    0.0,
    -0.15,
    "출처: Yahoo Finance, NYSE",
    transform=ax[0].transAxes,
    fontsize=10,
    ha="left",
)
ax[0].grid(False)


# Plotting

ax[1].plot(
    df0["observation_date"], df0["DGS2"], label="2년만기 국채", color="blue", lw=2
)

ax[1].legend(loc="upper left", bbox_to_anchor=(0.3, 1))
ax[1].xaxis.set_major_locator(mdates.YearLocator())
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
ax[1].text(
    0,
    1.00,
    "(%)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)
ax[1].text(0.0, -0.15, "출처: FRED", transform=ax[1].transAxes, fontsize=10, ha="left")
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
