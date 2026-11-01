# %% [markdown]
# # [그림 23] 미국 예외주의에 대한 구글 트렌드와 S&P500
#
# ## 이 코드가 하는 일
# 구글 트렌드 csv 파일과 FRED의 S&P500 지수를 읽어 한 그림에 그린다(y축 두 개).
#
# ## 그림이 다루는 내용
# '미국 예외주의(American Exceptionalism)'는 미국 경제와 주식시장이 다른 나라보다 계속 앞설 것이라는 생각이다.
# 구글 트렌드는 어떤 단어가 얼마나 많이 검색됐는지를 0~100 지수로 보여준다.
# 이 말의 검색이 늘어난 시기와 미국 주가(S&P500)의 흐름을 비교한다.
#
# ## 결과물
# pic_jpg/f23_google_trend_sp500.jpg, pic_tif/f23_google_trend_sp500.tif
#
# ## 필요한 파일
# - plot_def.py (defs): 한글 폰트 설정, 그림 저장
# - fred_api.py (defs): FRED 자료 받기
# - data/f_google_trend.csv: 구글 트렌드에서 'American Exceptionalism'(전 세계) 월별 검색 지수를 내려받은 파일
# %%
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

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

start = "2000-01-01"
end = "2025-12-31"

from fred_api import fetch_fred_series

# %% [markdown]
# ## 자료 받기
# - FRED: S&P 500 지수 (SP500)
# - csv: 앞의 두 줄은 설명이라 skiprows=2로 건너뛰고 읽는다. 열 이름을 Date, Google_Trend로 바꾼다.
# ## 그리기
# - 두 자료 모두 2021년 1월부터 2025년 6월까지 골라낸다.
# - 왼쪽 y축에 구글 트렌드, 오른쪽 y축에 S&P500을 그린다.
# %%
df_sp = fetch_fred_series("SP500", start_date=start, end_date=end)

# Load the CSV file
file_path = "data/f_google_trend.csv"
df = pd.read_csv(file_path, skiprows=2)


df = df.rename(
    columns={"월": "Date", "American Exceptionalism: (전 세계)": "Google_Trend"}
)


# Convert columns to appropriate data types
df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m")

# Filter data from 2020 to April 2025

selected_terms_to_plot = ["observation_date", "SP500"]
df_sp = df_sp.dropna(subset=selected_terms_to_plot)[selected_terms_to_plot].copy()

df_filtered = df[(df["Date"] >= "2021-01-01") & (df["Date"] <= "2025-06-01")].copy()
df_sp_filtered = df_sp[
    (df_sp["observation_date"] >= "2021-01-01")
    & (df_sp["observation_date"] <= "2025-06-01")
].copy()

# bplot: two y-axes

fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)

ax_left = ax
ax_right = ax_left.twinx()  # Create right-side y-axis
ax_left.plot(
    df_filtered["Date"],
    df_filtered["Google_Trend"],
    label="Google Trend: American Exceptionalism(좌측)",
    color="blue",
    lw=2,
)
ax_left.text(
    0,
    1.00,
    "(구글트렌드, 전세계)",
    ha="left",
    va="bottom",
    color="blue",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)
ax_left.yaxis.label.set_visible(True)

ax_right.plot(
    df_sp_filtered["observation_date"],
    df_sp_filtered["SP500"],
    label="S&P500(우측)",
    color="black",
    lw=1.5,
)

ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.7)

ax_right.text(
    1,
    1.00,
    "(S&P 500 지수)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)

ax_right.text(
    0,
    -0.15,
    "출처: Google, FRED",  # transform=plt.gcf().transFigure,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
    rotation=0,
    transform=ax.transAxes,
)

ax_left.legend(loc="upper left", bbox_to_anchor=(0.4, 0.99))
ax_right.legend(loc="upper left", bbox_to_anchor=(0.4, 0.899))

ax.xaxis.set_major_locator(mdates.YearLocator())

plt.grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
