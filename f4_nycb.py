# %% [markdown]
# # [그림 4] NYCB 주가와 은행업주가
# # [그림 5] 2년물 국채금리
#
# ## 이 코드가 하는 일
# Yahoo Finance에서 주가 두 개를, FRED에서 2년만기 국채금리를 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# - 왼쪽(그림 4): 뉴욕커뮤니티뱅크(NYCB)는 2024년 1월 말 CRE 대출 손실에 대비해 충당금을 크게 쌓는다고 발표했고,
#   주가가 급락했다. 은행주 전체(S&P Banks ETF)와 비교하면 이 은행만 크게 떨어졌음을 알 수 있다.
#   NYCB는 2024년 Flagstar Financial로 이름을 바꿔 지금은 종목기호 FLG로 거래된다.
# - 오른쪽(그림 5): 2년만기 국채금리는 앞으로 1~2년 동안의 정책금리 예상을 반영한다.
#
# ## 결과물
# pic_jpg/f4_nycb.jpg, pic_tif/f4_nycb.tif
#
# ## 필요한 파일 (defs 폴더)
# - fred_api.py: FRED 자료 받기(fetch_fred_series)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# ## 필요한 패키지
# ```python
# pip install yfinance
# ```
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import yfinance as yf

##폰트 설정

# 공통 함수 폴더(defs)를 import 경로에 추가
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
# ## 자료 받기
# - FRED: 2년만기 국채금리 (DGS2)
# - Yahoo Finance: Flagstar Financial(FLG), S&P Banks ETF(KBE)의 하루 종가
#   2022년 1월 1일부터 2025년 12월 31일까지 받아 같은 기간으로 한 번 더 골라내고, 처음 10줄을 출력해 확인한다.
#
# ## 그리기
# - 왼쪽: Flagstar 주가(왼쪽 y축)와 S&P Banks ETF(오른쪽 y축). 주가 수준이 달라서 축을 둘로 나눈다.
#   두 축의 범례를 하나로 합친다. 범례를 놓을 빈자리가 없어서 y축 아래쪽을 넓혀(왼쪽 0~42, 오른쪽 15~63)
#   선이 없는 띠를 만들고, 그곳(왼쪽 아래)에 범례를 둔다.
# - 오른쪽: 2년만기 국채금리. 범례는 선이 없는 오른쪽 아래에 둔다.
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
# 두 축의 범례를 하나로 합치고, y축 아래쪽을 넓혀 비운 자리에 범례를 둔다.
ax_left.set_ylim(0, 42)
ax_right.set_ylim(15, 63)
h1, l1 = ax_left.get_legend_handles_labels()
h2, l2 = ax_right.get_legend_handles_labels()
ax_left.legend(h1 + h2, l1 + l2, loc="lower left")
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

ax[1].legend(loc="lower right")
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
