# %% [markdown]
# # [그림 6] MMF와 은행예금 잔액
# # [그림 7] MMF와 은행예금 이자율
#
# ## 이 코드가 하는 일
# FRED에서 예금·MMF 잔액과 이자율을 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# MMF(Money Market Fund, 머니마켓펀드)는 단기국채 같은 안전한 단기자산에 투자하는 펀드이다.
# MMF 수익률은 정책금리를 빠르게 따라가지만 은행 저축예금 금리는 천천히 오른다.
# 2022년부터 금리가 오르자 돈이 은행 예금에서 MMF로 옮겨갔다.
# - 왼쪽(그림 6): 은행 예금은 줄거나 정체되고 MMF 자산은 늘어나는 모습
# - 오른쪽(그림 7): MMF 이자율과 저축예금 이자율의 차이
#
# ## 결과물
# pic_jpg/f6_mmf.jpg, pic_tif/f6_mmf.tif
#
# ## 필요한 파일 (defs 폴더)
# - fred_api.py: FRED 자료 받기(fetch_fred_series)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# ## 필요한 패키지
# - 따로 설치할 패키지는 없다(datetime은 파이썬에 기본으로 들어 있다).
# %%

import matplotlib.dates as mdates

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

## FRED 자료 불러오기

start = "2021-01-01"
# end='2025-10-01'
end = date.today()

from fred_api import fetch_fred_series

# %% [markdown]
# ## 자료 받기 (FRED)
# - 전체 상업은행 예금 (DPSACBM027NBOG): 10억 달러 단위, 1e3으로 나눠 조 달러로 그린다.
# - MMF 총금융자산 (MMMFFAQ027S): 분기 자료, 백만 달러 단위, 1e6으로 나눠 조 달러로 그린다.
# - 연준 역레포(RRP) 잔액 (RRPONTSYD): 불러오기만 하고 그림에는 쓰지 않는다.
# - 저축예금 전국 평균 금리 (SNDR)
# - 국채형 MMF 수익률 (MMTY)
# - MMF 전국 평균 금리 (MMNDR)
#
# ## 그리기
# - 왼쪽: 은행 예금(왼쪽 y축)과 MMF 자산(오른쪽 y축). 두 축의 범례를 하나로 합쳐 왼쪽 위에 둔다.
#   2023년 1~6월을 회색으로 칠한다.
# - 오른쪽: 이자율 세 개. 범례는 선이 없는 오른쪽 가운데에 둔다.
# %%
df0 = fetch_fred_series("DPSACBM027NBOG", start_date=start, end_date=end)

df1 = fetch_fred_series("MMMFFAQ027S", start_date=start, end_date=end)

df2 = fetch_fred_series("RRPONTSYD", start_date=start, end_date=end)

df3 = fetch_fred_series("SNDR", start_date=start, end_date=end)

df4 = fetch_fred_series("MMTY", start_date=start, end_date=end)

df5 = fetch_fred_series("MMNDR", start_date=start, end_date=end)

##왼쪽 그림
fig, ax = plt.subplots(1, 2, figsize=(8, 4.5), constrained_layout=True)

ax_left = ax[0]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(
    df0["observation_date"],
    df0["DPSACBM027NBOG"] / 1e3,
    label="은행 예금(좌축)",
    color="black",
    lw=2,
)
ax_right.plot(
    df1["observation_date"],
    df1["MMMFFAQ027S"] / 1e6,
    label="MMF(우축)",
    color="blue",
    lw=2,
)


ax[0].xaxis.set_major_locator(mdates.YearLocator())
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 라벨 위치 설정
# 두 축의 범례를 하나로 합친다.
h1, l1 = ax_left.get_legend_handles_labels()
h2, l2 = ax_right.get_legend_handles_labels()
ax_left.legend(h1 + h2, l1 + l2, loc="upper left")
ax_left.yaxis.label.set_visible(True)

# 단위 표시
ax_left.text(
    0,
    1.00,
    "(조 달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax_right.text(
    1.0,
    1.00,
    "(조 달러)",
    ha="right",
    va="bottom",
    color="blue",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
# 출처 표시
ax[0].text(0.0, -0.15, "출처: FRED", transform=ax[0].transAxes, fontsize=10, ha="left")
ax[0].grid(False)

# 음영 구간 추가
from datetime import datetime

shaded_periods = [(datetime(2023, 1, 1), datetime(2023, 6, 1))]

for i in [0]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color="gray", alpha=0.2)


# 오른쪽 그림

ax[1].plot(
    df4["observation_date"], df4["MMTY"], label="국채형MMF 이자율", color="blue", lw=2
)
ax[1].plot(
    df5["observation_date"],
    df5["MMNDR"],
    label="MMF 이자율",
    color="blue",
    lw=2,
    ls="--",
)
ax[1].plot(
    df3["observation_date"], df3["SNDR"], label="저축예금 이자율", color="black", lw=2
)

# 라벨표시 위치
ax[1].legend(loc="center right")

# X축 연도 표시 간격과 표시 형식
ax[1].xaxis.set_major_locator(mdates.YearLocator())
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
ax[1].text(
    0,
    1.00,
    "(%)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)

ax[1].text(
    0.0, -0.15, "출처: FRED, FDIC", transform=ax[1].transAxes, fontsize=10, ha="left"
)
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
