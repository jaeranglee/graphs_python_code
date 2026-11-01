# %% [markdown]
# # [그림 16] 직전 2개월 NFP 수정치
#
# ## 이 코드가 하는 일
# data/nfp_revisions.csv를 읽어, NFP 발표일마다 직전 두 달 치가 얼마나 수정됐는지 막대그래프로 그린다.
#
# ## 그림이 다루는 내용
# NFP를 발표할 때는 이번 달 숫자와 함께 지난 두 달의 숫자도 고쳐 발표한다.
# 두 달 치 수정 폭을 더하면 그동안 고용을 얼마나 많게(또는 적게) 발표했는지 알 수 있다.
# 2007년 이후 수정치를 보여주고, 크게 하향 수정된 2023년 11월 3일과 2025년 8월 1일 발표를 따로 강조한다.
#
# ## 결과물
# pic_jpg/f16_nfp_2month_revisions.jpg, pic_tif/f16_nfp_2month_revisions.tif
#
# ## 필요한 파일
# - plot_def.py (defs): 한글 폰트 설정, 그림 저장
# - nfp_revision.py (이 폴더): NFP 발표 시점별 값을 받아 수정 내역을 csv로 저장하는 코드
# - data/nfp_revisions.csv: 위 코드가 만든 파일
#
# ## 그리기
# - 막대 높이 = 1개월 전 수정치(revision1) + 2개월 전 수정치(revision2)
# - 위로 고쳐지면 파란색, 아래로 고쳐지면 검은색
# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy.dialects.mssql.information_schema import columns

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

from plot_def import set_fonts

set_fonts()

# Load the data from the CSV file
df = pd.read_csv("data/nfp_revisions.csv", index_col="month", parse_dates=True)


# Apply the conditional logic to create a new column with the value to plot
df["plot_value"] = np.where(
    df["vintage_completeness"] == "3 vintage(s)",  # Condition 1
    df["3rd - 1st"],  # Value if Condition 1 is true
    np.where(
        df["vintage_completeness"] == "2 vintage(s)",  # Condition 2
        df["2nd - 1st"],  # Value if Condition 2 is true
        np.nan,  # Value if neither condition is true
    ),
)

# Filter out rows that don't have a value to plot
plot_data = df.dropna(subset=["plot_value"])

df["revisions"] = df["revision1"] + df["revision2"]

plot_data2 = df[["1st_vintage_key", "revision1", "revision2", "revisions"]]


plot_data2.index = pd.to_datetime(plot_data2["1st_vintage_key"])
plot_data2 = plot_data2.drop(columns=["1st_vintage_key"])


bar_width = 29.5
plot_data2 = plot_data2.reset_index()
plot_data2 = plot_data2.rename(columns={"1st_vintage_key": "date"}).copy()

plot_data2 = plot_data2[plot_data2["date"] >= "2007-01-01"]

# Base colors

base_colors = np.where(
    (plot_data2["date"] == "2023-11-03") | (plot_data2["date"] == "2025-08-01"),
    "black",
    np.where(plot_data2["revisions"] >= 0, "blue", "black"),
)


# 월별 고용 발표일(Vintage Date)에 전월과 전전월 실적 수정 폭(인원수) 그려줌
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)


# Plot revisions
ax.bar(plot_data2["date"], plot_data2["revisions"], width=bar_width, color=base_colors)

ax.text(
    0,
    1.00,
    "(천명)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)

# Add a grid
ax.grid(True, which="major", linestyle="--", linewidth="0.5", color="grey", alpha=0.3)

# 0에서 가로줄
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")


# 출처 표시
ax.text(
    0.0,
    -0.15,
    "출처: BLS, ALFRED, FRED",
    fontsize=12,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
    transform=ax.transAxes,
)


# 그림파일 저장, 화면출력

from plot_def import plot_save

plot_save()
