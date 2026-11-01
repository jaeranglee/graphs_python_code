# %% [markdown]
# # [그림 49] TPU, 소비자심리지수, 구글트렌드
#
# ## 이 코드가 하는 일
# FRED에서 무역정책 불확실성지수와 소비자심리지수를 받고, 구글 트렌드 csv를 읽어 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# - 왼쪽: TPU(무역정책 불확실성지수)는 신문 기사에 무역정책 관련 불확실성 단어가 얼마나 나오는지로 만든 지수이다.
#   2025년 관세 정책이 쏟아지자 크게 뛰었고, 같은 시기 미시건대 소비자심리지수는 떨어졌다.
# - 오른쪽: 구글에서 'recession'(경기침체)을 검색한 정도. 경기에 대한 사람들의 걱정을 보여준다.
#
# ## 결과물
# pic_jpg/f49_tpu.jpg, pic_tif/f49_tpu.tif
#
# ## 필요한 파일
# - plot_def.py (defs): 한글 폰트 설정, 그림 저장
# - fred_api.py (defs): FRED 자료 받기
# - data/f_google_trend_recession.csv: 구글 트렌드에서 'recession'(미국) 검색 지수를 내려받은 파일
#
# ## 자료 받기 (FRED)
# - 무역정책 불확실성지수 (EPUTRADE): 왼쪽 y축
# - 미시건대 소비자심리지수 (UMCSENT): 오른쪽 y축
# - 경제정책 불확실성지수 (USEPUINDXD): 불러오지만 그림에는 쓰지 않는다.
#
# ## 그리기
# - 왼쪽 그림은 두 축의 범례를 하나로 합친다. 범례를 놓을 빈자리가 없어서 y축 위쪽을 넓혀
#   (왼쪽 11,000, 오른쪽 88까지) 비운 자리(왼쪽 위)에 범례를 둔다.
# - 오른쪽 그림은 2024년 이후 구글 트렌드 지수이다.
# %%
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib.dates as mdates


# Set font depending on the platform
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

# FRED data fetch def 호출

from fred_api import fetch_fred_series

start = "2024-01-01"
end = "2025-12-31"

# Fetch FRED series

# University of Michigan: Consumer Sentiment (UMCSENT)
df_m = fetch_fred_series("UMCSENT", start_date=start, end_date=end)

# Economic Policy Uncertainty Index for United States (USEPUINDXD), Daily
df_u = fetch_fred_series("USEPUINDXD", start_date=start, end_date=end)

# Economic Policy Uncertainty Index: Categorical Index: Trade policy (EPUTRADE), Monthly
df2 = fetch_fred_series("EPUTRADE", start_date=start, end_date=end)


# Plot the First Plot for TPU, Michigan

fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# First subplot: two y-axes
ax_left = ax[0]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(
    df2["observation_date"],
    df2["EPUTRADE"],
    label="무역정책 불확실성지수(좌측)",
    color="blue",
    lw=2,
)
ax_left.text(
    0,
    1.00,
    "(불확실성지수)",
    ha="left",
    va="bottom",
    color="blue",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax_left.yaxis.label.set_visible(True)


ax_right.plot(
    df_m["observation_date"],
    df_m["UMCSENT"],
    label="미시건대 소비자심리지수(우측)",
    color="black",
    lw=1.5,
)
ax_right.text(
    1,
    1.00,
    "(심리지수)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)

ax_right.text(
    0.0,
    -0.15,
    "출처: Baker, Scott R. 외, FRED",
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
    transform=ax[0].transAxes,
)

# 두 축의 범례를 하나로 합치고, y축 위쪽을 넓혀 비운 자리에 범례를 둔다.
ax_left.set_ylim(top=11000)
ax_right.set_ylim(top=88)
h1, l1 = ax_left.get_legend_handles_labels()
h2, l2 = ax_right.get_legend_handles_labels()
ax_left.legend(h1 + h2, l1 + l2, loc="upper left")

plt.grid(False)
# plt.tight_layout()

# the Second plot for google trend in recession
# Load the CSV file

file_path = "data/f_google_trend_recession.csv"
df2 = pd.read_csv(file_path)

# Clean and prepare the data
df2 = df2.iloc[1:].copy()  # Remove the first row (in-data header)
df2.columns = ["Date", "Google_Trend"]

# Convert columns to appropriate data types
df2["Date"] = pd.to_datetime(df2["Date"])
df2["Google_Trend"] = pd.to_numeric(df2["Google_Trend"], errors="coerce")


# Filter data from 2020 to April 2025
df_filtered = df2[(df2["Date"] >= "2024-01-01")]

# Plot the Second plot.

ax[1].plot(
    df_filtered["Date"],
    df_filtered["Google_Trend"],
    label="Google Trend",
    color="blue",
    lw=2,
)

ax[1].text(
    0,
    1.00,
    "(구글트렌드=recession, 미국기준)",
    ha="left",
    va="bottom",
    color="blue",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)
ax[1].text(
    0,
    -0.15,
    "출처: Google",  # transform=plt.gcf().transFigure,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
    rotation=0,
    transform=ax[1].transAxes,
)
plt.grid(False)

for i in [0, 1]:
    ax[i].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
