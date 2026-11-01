# %% [markdown]
# # [그림 17] 베버리지커브: 구인율과 실업률
#
# ## 이 코드가 하는 일
# FRED에서 구인율과 실업률을 받아, x축에 실업률, y축에 구인율을 놓고 달마다 점을 찍어 이은다.
#
# ## 그림이 다루는 내용
# 베버리지커브는 실업률과 구인율의 관계이다. 보통 구인율이 높으면(일자리가 많으면) 실업률이 낮다.
# 그래서 점들이 오른쪽 아래로 기울어진 곡선을 따라 움직인다.
# 경기침체 때는 오른쪽 아래(실업 증가, 구인 감소)로, 회복 때는 왼쪽 위로 움직인다.
# 코로나 이후에는 곡선이 위로 크게 올라갔다가 다시 내려왔는데, 실업을 크게 늘리지 않고 구인만 줄어든 것이어서
# 경기 연착륙 논의와 연결된다. 기간마다 선의 색을 달리하고, 2024년 8월과 가장 최근 달을 큰 점으로 표시한다.
#
# ## 결과물
# pic_jpg/f17_beveridge.jpg, pic_tif/f17_beveridge.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
# %%
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

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

from plot_def import set_fonts

set_fonts()

# %% [markdown]
# ## 자료 받기 (FRED)
# - 구인율 (JTSJOR): 구인건수 / (고용자 수 + 구인건수) x 100, 계절조정, 월별
# - 실업률 (UNRATE): %, 계절조정, 월별
# - 2000년 12월부터 가장 최근 자료까지 받는다(end를 먼 미래로 두면 있는 자료까지만 온다).
#
# ## 그리기
# 1. 기간 목록(periods)의 기간마다 선의 색을 달리해 그린다.
# 2. 모든 달을 회색 점으로 찍는다.
# 3. 2024년 8월(검은 점)과 가장 최근 달(파란 점)을 크게 표시한다.
# 4. 범례는 2열로 오른쪽 위에 둔다.
# %%
from fred_api import fetch_fred_series

# 사용자 정의 기간으로 호출
start = "2000-12-01"
end = "2029-12-31"

df0 = fetch_fred_series("JTSJOR", start_date=start, end_date=end)
df1 = fetch_fred_series("UNRATE", start_date=start, end_date=end)

df = pd.merge(df0, df1, on="observation_date")

# 변경할 컬럼 이름들을 dict로 정의
rename_dict = {
    "observation_date": "Date",
    "JTSJOR": "Job openings rate",
    "UNRATE": "Unemployment rate",
}

# 이름 변경 적용
df = df.rename(columns=rename_dict)

# 정렬
df = df.sort_values("Date")

# 2024년 8월 데이터 필터링
highlight_row = df[df["Date"] == pd.Timestamp("2024-08-01")]

# 가장 최근 달 데이터 필터링
highlight_row1 = df[df["Date"] == df["Date"].max()]


# 시각화 시작
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
# plt.figure(figsize=(12, 6),constrained_layout=True)

date = df["Date"].max()
last_month = "{date.year}.{date.month}".format(date=date)

# 기간별 색상 설정
periods = [
    ("2000-12-01", "2001-02-28", "gray", "2000.12 - 2001.2"),
    ("2001-03-01", "2001-11-30", "lightblue", "2001.3 - 2001.11"),
    ("2001-12-01", "2007-11-30", "skyblue", "2001.12 - 2007.11"),
    ("2007-12-01", "2009-06-30", "blue", "2007.12 - 2009.6"),
    ("2009-07-01", "2020-02-29", "black", "2009.7 - 2020.2"),
    ("2020-03-01", "2020-04-30", "gray", "2020.3 - 2020.4"),
    ("2020-05-01", df["Date"].max(), "black", f"2020.5 - {last_month}"),
]

# 궤적선을 기간별로 나누어 그림
for start, end, color, label in periods:
    mask = (df["Date"] >= pd.Timestamp(start)) & (df["Date"] <= pd.Timestamp(end))
    sub_df = df[mask]
    if len(sub_df) >= 2:  # 선 그리기 위해 최소 2개 이상의 포인트 필요
        ax.plot(
            sub_df["Unemployment rate"],
            sub_df["Job openings rate"],
            color=color,
            linewidth=2,
            alpha=0.9,
            label=label,
        )

# 기본 점들
ax.scatter(
    df["Unemployment rate"],
    df["Job openings rate"],
    s=20,
    color="gray",
    alpha=0.6,
    marker="o",
    #    label='Monthly Data'
)

# 2024년 8월 점 강조
if not highlight_row.empty:
    ax.scatter(
        highlight_row["Unemployment rate"],
        highlight_row["Job openings rate"],
        s=90,
        color="black",
        edgecolors="black",
        label="2024.8",
    )

# 가장 최근 달 점 강조
if not highlight_row1.empty:
    ax.scatter(
        highlight_row1["Unemployment rate"],
        highlight_row1["Job openings rate"],
        s=80,
        color="blue",
        edgecolors="black",
        label=last_month,
    )

# 축 설정 및 포맷

ax.text(
    0,
    1.00,
    "(구인율)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)
ax.text(
    1,
    -0.1,
    "(실업률)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)

ax.xaxis.set_major_formatter(PercentFormatter())
ax.yaxis.set_major_formatter(PercentFormatter())

ax.text(
    0.0,
    -0.15,
    "출처: BLS",
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
    transform=ax.transAxes,
)

plt.grid(False)
plt.legend(loc="upper right", ncol=2)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

from plot_def import plot_save

plot_save()
