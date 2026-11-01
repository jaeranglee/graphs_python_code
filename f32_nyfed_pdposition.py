# %% [markdown]
# # [그림 32] 프라이머리 딜러 국채 포지션
#
# ## 이 코드가 하는 일
# 뉴욕 연준에서 프라이머리 딜러의 국채 보유 자료를 받아 만기별로 그린다.
#
# ## 그림이 다루는 내용
# 프라이머리 딜러는 연준과 직접 거래하고 국채 경매에 반드시 참여해야 하는 대형 금융회사이다.
# 국채 발행이 늘어 딜러들이 팔지 못한 국채를 많이 떠안으면 보유액(포지션)이 커진다.
# 보유액이 너무 커지면 딜러가 국채를 더 사기 어려워져 국채시장의 거래가 원활하지 않을 수 있다.
#
# ## 결과물
# pic_jpg/f32_nyfed_pdposition.jpg, pic_tif/f32_nyfed_pdposition.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - nyfed_api.py: 시계열 목록 받기(fetch_series_list), 딜러 포지션 받기(fetch_pdpositions)
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
# %% [markdown]
# ## 자료 받기 (뉴욕 연준 Markets Data)
# 1. fetch_series_list(): 어떤 시계열이 있는지 목록과 설명을 받아 data/nyfed_pdposition.csv로 저장한다.
#    목록을 확인하는 용도라서 한 번만 실행해 보면 된다.
# 2. fetch_pdpositions(): 딜러 포지션 전체 시계열을 받아 data/TimeSeries.csv로 저장한다.
# 3. 저장한 csv를 읽어 Time Series 열의 코드로 필요한 자료를 고른다.
#    - 국채 전체, 단기국채(Bills), 중기국채(만기 11년 이하 구간을 더한 것), 장기국채(만기 11년 초과)
#    - 값은 백만 달러이며 1e3으로 나눠 10억 달러로 그린다.
# %%
from nyfed_api import fetch_series_list

# ny fed의 pd positions data를
#'data/TimesSeries.csv'로 저장

des = fetch_series_list()
des.to_csv("data/nyfed_pdposition.csv")


from nyfed_api import fetch_pdpositions

fetch_pdpositions()

#'data/TimesSeries.csv'를 dataframe으로 read

df = pd.read_csv("data/TimeSeries.csv")
df["As Of Date"] = pd.to_datetime(df["As Of Date"])
df["Value (millions)"] = pd.to_numeric(df["Value (millions)"], errors="coerce")

df["Value (millions)"] = df["Value (millions)"] / 1e3
df = df.set_index("As Of Date")


# PD Bills position
bills = df[df["Time Series"] == "PDPOSGS-B"]


notes11 = df[df["Time Series"] == "PDPOSGSC-G11L21"]


notes2 = df[df["Time Series"] == "PDPOSGSC-L2"]
notes23 = df[df["Time Series"] == "PDPOSGSC-G2L3"]
notes36 = df[df["Time Series"] == "PDPOSGSC-G3L6"]
notes67 = df[df["Time Series"] == "PDPOSGSC-G6L7"]
notes711 = df[df["Time Series"] == "PDPOSGSC-G7L11"]

# PD Bonds Position
notes10 = df[df["Time Series"] == "PDPOSGSC-G11"]

# PD Notes Position
notes = notes2 + notes23 + notes36 + notes67 + notes711

# PD Bonds Position
bonds = df[df["Time Series"] == "PDPOSGSC-G21"] + notes11

# PD total Treasuries Position
treasuries = df[df["Time Series"] == "PDPOSGST-TOT"]

cb = df[df["Time Series"] == "PDPOSCS-TOT"]
agencies = df[df["Time Series"] == "PDPOSFGS-TOT"]


# 그래프 그리기

fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)


ax.plot(
    treasuries.index,
    treasuries["Value (millions)"],
    label="Total Treasuries",
    color="blue",
    lw=2,
)
ax.plot(bills.index, bills["Value (millions)"], label="Bills", color="black", lw=2)
ax.plot(
    notes.index, notes["Value (millions)"], label="Notes", color="gray", lw=2, ls="-"
)

# Bond position 데이터
ax.plot(
    bonds.index, bonds["Value (millions)"], label="Bonds", color="black", lw=1, ls="-"
)
ax.plot(notes10.index, notes10["Value (millions)"], label=None, color="black", lw=1)


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

ax.text(
    0.0,
    -0.15,
    "출처: NY Fed, Primary Dealer Statistics",
    transform=ax.transAxes,
    fontsize=12,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)
ax.legend()
ax.grid(True, linestyle="--", color="gray", linewidth=0.7, alpha=0.4)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
