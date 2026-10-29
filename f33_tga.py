# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # [그림 33] 미국 재무부 TGA잔고
# ## 같은 디렉토리에 필요한 file
#   - plot_def.py : 한글폰트 추가, 그래프 저장
#   - fred_api.py
# %%
import pandas as pd
import matplotlib.pyplot as plt


# Set font depending on the platform
# 공통 함수 폴더(codes/defs)를 import 경로에 추가
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
# ## FRED 자료 추출
# - D2WLTGAL (TGA Wednesday, NY FED)
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
