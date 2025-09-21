# %% [markdown]
# ## [그림 27] Bid to cover ratio
# ## 같은 디렉토리에 필요한 file
# - plot_def.py : 한글폰트 추가, 그래프 저장
# - treasury_auctions_api.py : Treasury Fiscal Data, Treasury Auctions Data에서 data fetch
# ## data 파일
# - data/treasury_auctions_2024.csv
# - fetch_securities_auction(start_date=start, end_date=end) 실행되며 자동 생성
# %%

from treasury_auctions_api import fetch_securities_auction

start='2024-01-01'
end='2026-01-01'

fetch_securities_auction(start_date=start, end_date=end)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 한글 폰트 설정
from plot_def import *
set_fonts()

# CSV 불러오기
df = pd.read_csv("data/treasury_auctions_2024.csv")

# 날짜 변환
df['auction_date'] = pd.to_datetime(df['auction_date'])
df = df[df['auction_date'] >= "2024-01-01"].copy()

# bid_to_cover_ratio' 숫자로 변환
df["bid_to_cover_ratio"] = pd.to_numeric(df["bid_to_cover_ratio"], errors="coerce")

# security_type 별 색상 지정
colors = {
    "Bill": "red",
    "Bond": "blue",
    "Note": "green"
}

# Figure, Axes 객체 생성
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

for sec, color in colors.items():
    subset = df[df["security_type"] == sec].sort_values('auction_date')

    # 실제 값 (점선)
    #ax.plot(subset['auction_date'], subset["bid_to_cover_ratio'"],
    #             linestyle="--", color=color, alpha=0.7, label=f"{sec} (Actual)")

    # 6개월 이동평균 (실선)
    ax.plot(
        subset['auction_date'],
        subset["bid_to_cover_ratio"].rolling(window=6, min_periods=1).mean(),
        linestyle="-", color=color, linewidth=2, label=f"{sec} (6M MA)"
    )

# 레이블, 범례, 격자
ax.legend()
ax.grid(True, linestyle="--", alpha=0.6)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # 1년 간격으로 눈금 표시
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # 연도만 표시

# Add a grid and ensure a tight layout
plt.grid(True, which='major', linestyle='--', linewidth='0.5', color='grey')


# y축 단위 표시
ax.text(0.0, 1.02, '(%)', ha='left', va='bottom', color='black',
        fontsize=12, rotation=0, transform=ax.transAxes)

# 출처 표기
ax.text(0.0, -0.15, "출처: Fiscal Data, Treasury Auctions Data", va='bottom', rotation=0,
         fontsize=12, ha='left', color='black',transform=ax.transAxes)


#plt.tight_layout()

plot_save()