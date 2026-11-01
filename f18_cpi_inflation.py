# %% [markdown]
# # [그림 18] 소비자물가와 근원물가
#
# ## 이 코드가 하는 일
# FRED에서 소비자물가지수(CPI)와 근원물가지수를 받아 상승률을 계산하고 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# - 소비자물가(CPI): 가계가 사는 상품과 서비스의 가격 수준
# - 근원물가: CPI에서 가격이 크게 출렁이는 식료품과 에너지를 뺀 것. 물가의 기조적인 흐름을 보여준다.
# - 왼쪽: 1년 전 같은 달과 비교한 상승률(전년동월대비). 흔히 말하는 '물가상승률'이다.
# - 오른쪽: 바로 전 달과 비교한 상승률(전월대비). 최근 흐름을 빨리 보여준다.
# 2021년 이후를 그리고, 책 본문에서 다룬 2024년 8월 값을 점으로 강조한다.
#
# ## 결과물
# pic_jpg/f18_cpi_inflation.jpg, pic_tif/f18_cpi_inflation.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
#
# ## 자료 받기 (FRED)
# - 전년동월대비용(계절조정 전): 소비자물가 CPIAUCNS, 근원물가 CPILFENS. pct_change(12)로 12개월 전 대비 상승률을 구한다.
# - 전월대비용(계절조정): 소비자물가 CPIAUCSL, 근원물가 CPILFESL. pct_change()로 1개월 전 대비 상승률을 구한다.
#   전월대비는 계절에 따른 움직임(예: 연초 가격 인상)을 걸러 낸 계절조정 자료를 써야 비교가 정확하다.
# - WTI 유가(WTISPLC)도 불러오지만 그림에는 쓰지 않는다.
# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

df_cpins = fetch_fred_series("CPIAUCNS", start_date=start, end_date=end)

df_corens = fetch_fred_series("CPILFENS", start_date=start, end_date=end)

# Load WTI spot
df_wti = fetch_fred_series("WTISPLC", start_date=start, end_date=end)

#
df_cpis = fetch_fred_series("CPIAUCSL", start_date=start, end_date=end)
df_cores = fetch_fred_series("CPILFESL", start_date=start, end_date=end)

# ---------------------

# Calculate YoY inflation rate

df_cpins["YoY_Inflation"] = (
    df_cpins["CPIAUCNS"].pct_change(periods=12, fill_method=None) * 100
)
df_corens["YoY_Inflation"] = (
    df_corens["CPILFENS"].pct_change(periods=12, fill_method=None) * 100
)

df_cpins["YoY_Inflation"] = pd.to_numeric(df_cpins["YoY_Inflation"], errors="coerce")
df_corens["YoY_Inflation"] = pd.to_numeric(df_corens["YoY_Inflation"], errors="coerce")

# Filter for
df_cpins = df_cpins[(df_cpins["observation_date"] >= "2021-01-01")].copy()
df_corens = df_corens[(df_corens["observation_date"] >= "2021-01-01")].copy()

# Convert the observation_date to datetime
df_cpis["observation_date"] = pd.to_datetime(df_cpis["observation_date"])
df_cores["observation_date"] = pd.to_datetime(df_cores["observation_date"])

# Calculate month-to-month inflation rate (as percentage)
df_cpis["MOM_Inflation"] = df_cpis["CPIAUCSL"].pct_change(fill_method=None) * 100
df_cores["MOM_Inflation"] = df_cores["CPILFESL"].pct_change(fill_method=None) * 100

df_cpis = df_cpis[(df_cpis["observation_date"] >= "2021-01-01")].copy()
df_cores = df_cores[(df_cores["observation_date"] >= "2021-01-01")].copy()

# Identify the specific date
highlight_date = "2024-08"

# Convert date format to match DataFrame
highlight_date = pd.to_datetime(highlight_date)

# Find the corresponding data point in dff

highlight_point_cpins = df_cpins[df_cpins["observation_date"] == highlight_date]
highlight_point_corens = df_corens[df_corens["observation_date"] == highlight_date]

highlight_point_cpis = df_cpis[df_cpis["observation_date"] == highlight_date]
highlight_point_cores = df_cores[df_cores["observation_date"] == highlight_date]


# Plot
# 전년동월비 (왼쪽그림), 전월비(오른쪽)
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

ax[0].plot(df_cpins["observation_date"], df_cpins["YoY_Inflation"], lw=2, color="blue")
ax[0].plot(
    df_corens["observation_date"], df_corens["YoY_Inflation"], lw=2, color="black"
)

# Add horizontal line at y = 2
ax[0].axhline(y=2, color="gray", linestyle="--", linewidth=1)

# Plot the highlighted point with a larger marker
ax[0].scatter(
    highlight_point_cpins["observation_date"],
    highlight_point_cpins["YoY_Inflation"],
    color="blue",
    marker="o",
    s=100,
    linewidth=2,
    label="2024년 8월 소비자물가",
)
ax[0].scatter(
    highlight_point_corens["observation_date"],
    highlight_point_corens["YoY_Inflation"],
    color="black",
    marker="x",
    s=100,
    linewidth=2,
    label="2024년 8월 근원물가",
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

# X축 눈금 표시를 1년 간격으로 설정
ax[0].xaxis.set_major_locator(mdates.YearLocator())  # 1년 간격으로 눈금 표시
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))  # 연도만 표시

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

ax[1].plot(df_cpis["observation_date"], df_cpis["MOM_Inflation"], lw=2, color="blue")
ax[1].scatter(
    highlight_point_cpis["observation_date"],
    highlight_point_cpis["MOM_Inflation"],
    color="blue",
    marker="o",
    s=100,
    linewidth=2,
    label="2024년 8월 소비자물가",
)
ax[1].plot(df_cores["observation_date"], df_cores["MOM_Inflation"], lw=2, color="black")
ax[1].scatter(
    highlight_point_cores["observation_date"],
    highlight_point_cores["MOM_Inflation"],
    color="black",
    marker="x",
    s=100,
    linewidth=2,
    label="2024년 8월 근원물가",
)

# Add horizontal line at y = 2
ax[1].axhline(y=0, color="gray", linestyle="--", linewidth=1)
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

# X축 눈금 표시를 1년 간격으로 설정
ax[1].xaxis.set_major_locator(mdates.YearLocator())  # 1년 간격으로 눈금 표시
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))  # 연도만 표시

plt.grid(False)
plt.legend()


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
