# %% [markdown]
# # [그림 19] 수입물가와 생산자물가
#
# ## 이 코드가 하는 일
# FRED에서 수입물가지수와 생산자물가지수를 받아 상승률을 계산하고 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# - 수입물가: 미국이 외국에서 사 오는 상품의 가격. 달러 가치와 국제 원자재 가격의 영향을 받는다.
# - 생산자물가: 기업이 생산해 파는 상품의 가격. 시간이 지나 소비자물가에 반영되는 경우가 많아 소비자물가의 선행지표로 본다.
# - 왼쪽: 전년동월대비 상승률, 오른쪽: 전월대비 상승률
# 2021년 이후를 그리고, 2024년 8월 값을 점으로 강조한다.
#
# ## 결과물
# pic_jpg/f19_imp_and_ppi.jpg, pic_tif/f19_imp_and_ppi.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
#
# ## 자료 받기 (FRED)
# - 수입물가지수, 전체 상품 (IR)
# - 생산자물가지수, 전체 상품 (PPIACO)
# - pct_change(12)로 전년동월대비, pct_change()로 전월대비 상승률을 구한다.
# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# 한글 폰트 설정
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

start = "2020-01-01"
end = "2025-12-31"

# Fetch series

from fred_api import *

# Fetch series
# Import Price Index (End Use): All Commodities (IR)
df0 = fetch_fred_series("IR", start_date=start, end_date=end)

# Producer Price Index by Commodity: All Commodities (PPIACO)
df1 = fetch_fred_series("PPIACO", start_date=start, end_date=end)

df = pd.merge(df0, df1, on="observation_date", how="inner").copy()

# ---------------------

# Calculate YoY inflation rate

df["YoY_IMP"] = df["IR"].pct_change(periods=12, fill_method=None) * 100
df["YoY_PPI"] = df["PPIACO"].pct_change(periods=12, fill_method=None) * 100

df["MoM_IMP"] = df["IR"].pct_change(fill_method=None) * 100
df["MoM_PPI"] = df["PPIACO"].pct_change(fill_method=None) * 100

df = df[(df["observation_date"] >= "2021-01-01")].copy()

df["YoY_IMP"] = pd.to_numeric(df["YoY_IMP"], errors="coerce").copy()
df["YoY_PPI"] = pd.to_numeric(df["YoY_PPI"], errors="coerce").copy()
df["MoM_IMP"] = pd.to_numeric(df["MoM_IMP"], errors="coerce").copy()
df["MoM_PPI"] = pd.to_numeric(df["MoM_PPI"], errors="coerce").copy()


# Identify the specific date
highlight_date = "2024-08"

# Convert date format to match DataFrame
highlight_date = pd.to_datetime(highlight_date)

# Find the corresponding data point in dff

highlight_point_imp_yoy = df[df["observation_date"] == highlight_date]
highlight_point_ppi_yoy = df[df["observation_date"] == highlight_date]

highlight_point_imp_mom = df[df["observation_date"] == highlight_date]
highlight_point_ppi_mom = df[df["observation_date"] == highlight_date]


# Plot
# 전년동월비 (왼쪽그림), 전월비(오른쪽)
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

ax[0].plot(df["observation_date"], df["YoY_IMP"], lw=2, color="blue")
ax[0].plot(df["observation_date"], df["YoY_PPI"], lw=2, color="black")

# Add horizontal line at y = 2
ax[0].axhline(y=0, color="gray", linestyle="--", linewidth=1)

# Plot the highlighted point with a larger marker
ax[0].scatter(
    highlight_point_imp_yoy["observation_date"],
    highlight_point_imp_yoy["YoY_IMP"],
    color="blue",
    marker="o",
    s=100,
    linewidth=2,
    label="2024년 8월 수입물가",
)
ax[0].scatter(
    highlight_point_ppi_yoy["observation_date"],
    highlight_point_ppi_yoy["YoY_PPI"],
    color="black",
    marker="x",
    s=100,
    linewidth=2,
    label="2024년 8월 생산자물가",
)

# Add a legend for clarity
ax[0].legend()


# Formatting

ax[0].text(
    0,
    1.00,
    "(%, 전년동월대비)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)

# Turn off scientific notation on y-axis
ax[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
# Set major ticks to years
ax[0].xaxis.set_major_locator(mdates.YearLocator())  # Every year

ax[0].grid(False)

ax[0].text(
    0.0,
    -0.15,
    "출처: BLS, FRED",
    transform=ax[0].transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)


# Plotting the inflation rate 전월비 (오른쪽)

ax[1].plot(df["observation_date"], df["MoM_IMP"], lw=2, color="blue")
ax[1].plot(df["observation_date"], df["MoM_PPI"], lw=2, color="black")

ax[1].scatter(
    highlight_point_imp_mom["observation_date"],
    highlight_point_imp_mom["MoM_IMP"],
    color="blue",
    marker="o",
    s=100,
    linewidth=2,
    label="2024년 8월 수입물가",
)
ax[1].scatter(
    highlight_point_ppi_mom["observation_date"],
    highlight_point_ppi_mom["MoM_PPI"],
    color="black",
    marker="x",
    s=100,
    linewidth=2,
    label="2024년 8월 생산자물가",
)

# Add horizontal line at y = 0
ax[1].axhline(y=0, color="gray", linestyle="--", linewidth=1)

# Set major ticks to years
ax[1].xaxis.set_major_locator(mdates.YearLocator())  # Every year

# 단위 표시
ax[1].text(
    0,
    1.00,
    "(%, 전월대비)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)
# 출처표시
ax[1].text(
    0.0,
    -0.15,
    "출처: BLS, FRED",
    transform=ax[1].transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)


plt.grid(False)
plt.legend()


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
