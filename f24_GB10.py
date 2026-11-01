# %% [markdown]
# # [그림 24] 10년물 미국채 수익률과 S&P500
#
# ## 이 코드가 하는 일
# FRED에서 10년만기 국채금리와 S&P500 지수를 받아 한 그림에 그린다(y축 두 개).
#
# ## 그림이 다루는 내용
# 10년만기 국채금리는 주택담보대출 금리, 회사채 금리 등 여러 금리의 기준이 된다.
# 금리가 오르면 기업의 미래 이익을 현재 가치로 바꿀 때 더 크게 깎이므로 주가에 부담이 된다.
# 2023년 이후 금리와 주가가 어떻게 함께 움직였는지 비교한다.
#
# ## 결과물
# pic_jpg/f24_GB10.jpg, pic_tif/f24_GB10.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
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

from fred_api import fetch_fred_series

start = "2023-01-01"
end = "2025-09-30"
# %% [markdown]
# ## 자료 받기 (FRED)
# - S&P 500 지수 (SP500)
# - 10년만기 국채금리 (DGS10)
# ## 그리기
# - 두 자료를 날짜 기준으로 합친 뒤, 왼쪽 y축에 10년물 금리, 오른쪽 y축에 S&P500을 그린다.
# - 두 축의 범례를 하나로 합쳐 왼쪽 위에 둔다.
# %%
dgs10_df = fetch_fred_series("DGS10", start_date=start, end_date=end)
sp500_df = fetch_fred_series("SP500", start_date=start, end_date=end)

# 날짜 기준으로 두 데이터프레임 병합 (공통 날짜 기준)
merged_df = pd.merge(dgs10_df, sp500_df, on="observation_date", how="inner")

selected_terms_to_plot = ["observation_date", "DGS10", "SP500"]
merged_df = merged_df.dropna(subset=selected_terms_to_plot)[
    selected_terms_to_plot
].copy()


# 그래프 그리기
fig, ax1 = plt.subplots(figsize=(10, 5), constrained_layout=True)

# DGS10 (10년물 금리)
ax1.plot(
    merged_df["observation_date"],
    merged_df["DGS10"],
    color="blue",
    label="10년물 국채수익률(좌축)",
    lw=2,
)

# ax1.set_ylabel('TB10 (%)', color='blue', fontsize=12)
ax1.text(
    0,
    1.00,
    "(10년물 국채수익률 ,%)",
    ha="left",
    va="bottom",
    color="blue",
    fontsize=12,
    rotation=0,
    transform=ax1.transAxes,
)
ax1.tick_params(axis="y", labelcolor="blue")

# 보조 y축: S&P 500
ax2 = ax1.twinx()
ax2.plot(
    merged_df["observation_date"],
    merged_df["SP500"],
    color="black",
    label="S&P 500(우축)",
)

ax2.set_ylim(3500, 6700)

ax2.text(
    1,
    1.00,
    "(S&P 500 지수)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax1.transAxes,
)

ax2.tick_params(axis="y", labelcolor="black")

# 출처

ax2.text(
    0.0,
    -0.15,
    "출처: FRED",
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
    transform=ax1.transAxes,
)
# 두 축의 범례를 하나로 합친다.
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left")

ax1.grid(True, linestyle="--", linewidth=0.7, alpha=0.7)

# X축 눈금

ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
# ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# fig.tight_layout()

plt.grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
