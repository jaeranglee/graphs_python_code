# %% [markdown]
# # [그림 48] 달러 인덱스와 10년물 미국채 수익률
#
# ## 이 코드가 하는 일
# FRED에서 달러인덱스와 10년만기 국채금리를 받아 한 그림에 그린다(y축 두 개).
#
# ## 그림이 다루는 내용
# 달러인덱스는 여러 나라 통화와 비교한 달러의 평균 가치이다. 오르면 달러가 강해진 것이다.
# 보통 미국 금리가 오르면 달러 자산의 매력이 커져 달러도 강해진다.
# 2024~2025년에 둘이 함께 움직였는지, 따로 움직인 때가 있었는지 비교한다.
#
# ## 결과물
# pic_jpg/f48_dollar_index_and_10y.jpg, pic_tif/f48_dollar_index_and_10y.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
#
# ## 자료 받기 (FRED)
# - 명목 광의 달러인덱스 (DTWEXBGS): 왼쪽 y축
# - 10년만기 국채금리 (DGS10): 오른쪽 y축
# - 두 축의 범례를 하나로 합쳐 선이 없는 오른쪽 위에 둔다.
# %%
import pandas as pd
import matplotlib.pyplot as plt

# 폰트 설정
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

# 데이터 수집
start = "2024-01-01"
end = "2025-10-01"
from fred_api import fetch_fred_series

dgs10_df = fetch_fred_series("DGS10", start_date=start, end_date=end)
bdxy_df = fetch_fred_series("DTWEXBGS", start_date=start, end_date=end)


# 날짜 기준으로 두 데이터프레임 병합 (공통 날짜 기준)

merged_df = pd.merge(dgs10_df, bdxy_df, on="observation_date")

selected_terms_to_plot = ["observation_date", "DGS10", "DTWEXBGS"]
merged_df = merged_df.dropna(subset=selected_terms_to_plot)[
    selected_terms_to_plot
].copy()


# 그래프 그리기
fig, ax1 = plt.subplots(figsize=(9, 4.5), constrained_layout=True)

# 보조 y축: S&P 500
ax1.plot(
    merged_df["observation_date"],
    merged_df["DTWEXBGS"],
    label="달러인덱스(좌측)",
    color="blue",
    lw=2,
)


ax1.text(
    0,
    1.00,
    "(연준달러인덱스, 2006=100)",
    ha="left",
    va="bottom",
    color="blue",
    fontsize=12,
    rotation=0,
    transform=ax1.transAxes,
)

ax1.tick_params(axis="y", labelcolor="b")
ax1.grid(True, linestyle="--", color="gray", linewidth=0.7, alpha=0.5)

# DGS10 (10년물 금리)
ax2 = ax1.twinx()
ax2.plot(
    merged_df["observation_date"],
    merged_df["DGS10"],
    label="10년물 국채수익률(우측)",
    color="black",
    lw=1,
)

ax2.text(
    1,
    1.00,
    "(10년물 국채 수익률, %)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax1.transAxes,
)

ax2.tick_params(axis="y", labelcolor="r")


# 제목 및 레이아웃

ax2.text(
    0.0,
    -0.15,
    "출처: Federal Reserve Bank of St. Louis",
    transform=ax1.transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)
# 두 축의 범례를 하나로 합친다.
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper right")


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
