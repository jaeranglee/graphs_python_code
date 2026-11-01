# %% [markdown]
# ## [그림 27] Bid to cover ratio
#
# ## 이 코드가 하는 일
# 재무부 국채 경매 결과를 받아, 국채 종류별 응찰률(bid to cover ratio)의 흐름을 그린다.
#
# ## 그림이 다루는 내용
# 응찰률 = 응찰 금액 합계 / 발행 금액. 예를 들어 100억 달러를 파는데 250억 달러어치 주문이 들어오면 2.5이다.
# 응찰률이 높을수록 그 국채를 사려는 수요가 강하다는 뜻이다.
# 경매마다 값이 들쭉날쭉해서 최근 6번 경매의 평균(이동평균)으로 그린다.
#
# ## 결과물
# pic_jpg/f27_treasury_bid_to_cover.jpg, pic_tif/f27_treasury_bid_to_cover.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - treasury_auctions_api.py: 경매 결과 받기(fetch_securities_auction)
# ## data 파일
# - data/treasury_auctions_2024.csv: 코드를 실행하면 fetch_securities_auction()이 자동으로 만든다.
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

from treasury_auctions_api import fetch_securities_auction

start = "2024-01-01"
end = "2026-01-01"

fetch_securities_auction(
    start_date=start, end_date=end, csv_path="data/treasury_auctions_2024.csv"
)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 한글 폰트 설정
from plot_def import *

set_fonts()

# CSV 불러오기
df = pd.read_csv("data/treasury_auctions_2024.csv")

# 날짜 변환
df["auction_date"] = pd.to_datetime(df["auction_date"])
df = df[df["auction_date"] >= "2024-01-01"].copy()

# bid_to_cover_ratio' 숫자로 변환
df["bid_to_cover_ratio"] = pd.to_numeric(df["bid_to_cover_ratio"], errors="coerce")

# security_type 별 색상 지정
colors = {"Bill": "black", "Bond": "blue", "Note": "gray"}

# Figure, Axes 객체 생성
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

for sec, color in colors.items():
    subset = df[df["security_type"] == sec].sort_values("auction_date")

    # 실제 값 (점선)
    # ax.plot(subset['auction_date'], subset["bid_to_cover_ratio'"],
    #             linestyle="--", color=color, alpha=0.7, label=f"{sec} (Actual)")

    # 6개월 이동평균 (실선)
    ax.plot(
        subset["auction_date"],
        subset["bid_to_cover_ratio"].rolling(window=6, min_periods=1).mean(),
        linestyle="-",
        color=color,
        linewidth=2,
        label=f"{sec} (6M MA)",
    )

# 레이블, 범례, 격자
ax.legend()
ax.grid(True, linestyle="--", alpha=0.6)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # 1년 간격으로 눈금 표시
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))  # 연도만 표시

# Add a grid and ensure a tight layout
plt.grid(True, which="major", linestyle="--", linewidth="0.5", color="grey")


# y축 단위 표시
ax.text(
    0.0,
    1.02,
    "(%)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)

# 출처 표기
ax.text(
    0.0,
    -0.15,
    "출처: Fiscal Data, Treasury Auctions Data",
    va="bottom",
    rotation=0,
    fontsize=12,
    ha="left",
    color="black",
    transform=ax.transAxes,
)

plot_save()
