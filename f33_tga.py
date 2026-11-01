# %% [markdown]
# # [그림 33] 미국 재무부 TGA잔고
#
# ## 이 코드가 하는 일
# FRED에서 재무부의 연준 예금(TGA) 잔액을 받아 2020년 이후를 그린다.
#
# ## 그림이 다루는 내용
# TGA는 미국 재무부가 연준에 둔 예금 계좌로, 정부의 '지갑'이라고 할 수 있다.
# 부채한도에 걸려 국채를 새로 발행하지 못하면 재무부는 TGA에 있는 돈을 꺼내 쓰므로 잔액이 줄어든다.
# 부채한도 문제가 풀리면 국채를 발행해 TGA를 다시 채운다. 2025년 3월 19일 값을 점으로 강조한다.
#
# ## 결과물
# pic_jpg/f33_tga.jpg, pic_tif/f33_tga.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
# %%
import pandas as pd
import matplotlib.pyplot as plt


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

# api를 이용해 FRED 자료를 호출하기 위한 루틴

start = "2020-01-01"
end = "2025-12-31"

from fred_api import fetch_fred_series

# %% [markdown]
# ## 자료 받기 (FRED)
# - TGA 잔액 (D2WLTGAL): 매주 수요일 기준, 백만 달러. 1000으로 나눠 10억 달러로 그린다.
# %%
df = fetch_fred_series("D2WLTGAL", start_date=start, end_date=end)

# Identify the specific date
highlight_date = "2025-03-19"

# Convert date format to match DataFrame
highlight_date = pd.to_datetime(highlight_date)

# Find the corresponding data point in dff

highlight_point = df[df["observation_date"] == highlight_date]


# 그래프 그리기

fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
ax.plot(df["observation_date"], df["D2WLTGAL"] / 1000, color="blue", lw=2)
ax.scatter(
    highlight_point["observation_date"],
    highlight_point["D2WLTGAL"] / 1000,
    color="blue",
    marker="o",
    s=100,
    linewidth=2,
    label="2025년 3월 19일 TGA",
)


ax.text(
    0,
    1.00,
    "(십억 달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)
plt.grid(True, linestyle="--", color="gray", linewidth=0.7, alpha=0.7)
plt.legend()
ax.text(
    0.0,
    -0.15,
    "출처: FRED; 수요일 뉴욕연준 기준",
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)

# plt.tight_layout()


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
