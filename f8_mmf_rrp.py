# %% [markdown]
# # [그림 8] MMF의 단기국채 투자잔액, 연준과 MMF의 RRP
#
# ## 이 코드가 하는 일
# FRED에서 MMF의 단기국채 보유액을, 뉴욕 연준에서 MMF의 RRP 거래액을 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# RRP(Reverse Repurchase Agreement, 역레포)는 MMF 같은 기관이 연준에 하루 동안 돈을 맡기고 이자를 받는 거래이다.
# MMF는 남는 돈을 연준 RRP에 맡기거나 단기국채(T-Bill)를 산다.
# 2023년 6월 부채한도 문제가 풀린 뒤 재무부가 단기국채를 많이 발행하자, MMF는 RRP에서 돈을 빼 단기국채를 샀다.
# - 왼쪽: MMF의 단기국채 보유액이 늘어나는 모습
# - 오른쪽: MMF가 연준 RRP에 맡긴 돈이 줄어드는 모습
#
# ## 결과물
# pic_jpg/f8_mmf_rrp.jpg, pic_tif/f8_mmf_rrp.tif
#
# ## 필요한 파일 (defs 폴더)
# - fred_api.py: FRED 자료 받기
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - nyfed_rrp_vol.py: 뉴욕 연준 RRP 거래 자료 받기(fetch_rrp_vol)
# ## 필요한 패키지
# - 따로 설치할 패키지는 없다(datetime은 파이썬에 기본으로 들어 있다).
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

# 폰트 설정
set_fonts()

# Fetch series
# ---------------------

from fred_api import fetch_fred_series
from nyfed_rrp_vol import fetch_rrp_vol

start = "2021-01-01"
end = "2025-10-01"
op_type = "Reverse Repo"

# %% [markdown]
# ## 자료 받기 (FRED)
# - 연준 RRP 잔액 주평균 (WLRRAA): 불러오기만 하고 그림에는 쓰지 않는다.
# - MMF의 단기국채 보유액 (BOGZ1FL633061110Q): 분기 자료, 백만 달러
# - 연방정부 총부채 (GFDEBTN): 분기 자료, 백만 달러.
#   아래에서 'MMF 단기국채 보유액 / 총부채' 비율을 계산해 두지만 그림에는 쓰지 않는다.
# %%

df_rrp = fetch_fred_series("WLRRAA", start_date=start, end_date=end)
df_mmf = fetch_fred_series("BOGZ1FL633061110Q", start_date=start, end_date=end)
df_debt = fetch_fred_series("GFDEBTN", start_date=start, end_date=end)

# %% [markdown]
# ## 자료 받기 (뉴욕 연준 Markets Data)
# fetch_rrp_vol()은 자료 두 개를 돌려준다. 두 번째 자료는 거래상대방별 RRP 거래액이며,
# 그중 거래상대방(Counterparty Type)이 mmf인 줄만 골라 MMF의 RRP 거래액으로 쓴다.
# %%
mmf_rrp = fetch_rrp_vol(start_date=start, end_date=end)[1]
mmf_rrp = mmf_rrp[mmf_rrp["Counterparty Type"] == "mmf"]

# total MMF Treasury Bills outstanding to Total US government debt outstanding
df_mmf["ratio"] = df_mmf["BOGZ1FL633061110Q"] / df_debt["GFDEBTN"] * 100

# %% [markdown]
# ## 그리기
# - 왼쪽: MMF 단기국채 보유액. 백만 달러를 1e6으로 나눠 조 달러로 그린다.
# - 오른쪽: MMF의 RRP 거래액(Amount Accepted). 달러를 1e12로 나눠 조 달러로 그린다.
# - 두 그림 모두 2023년 1~5월을 회색으로 칠한다.
# %%
fig, ax = plt.subplots(1, 2, figsize=(8, 4.5), constrained_layout=True)

ax[0].plot(
    df_mmf["observation_date"],
    df_mmf["BOGZ1FL633061110Q"] / 1e6,
    color="blue",
    lw=2,
    label="MMF 단기국채 투자잔액",
)

# 단위 표시 및 출처:

ax[0].text(
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

ax[0].text(
    0.0,
    -0.15,
    "출처: FRED, 음영은 2023년 1월~5월",
    transform=ax[0].transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)

# 범례 (하나만 표시하거나 합칠 수도 있음)
ax[0].legend(loc="upper left")
ax[0].grid(False)

# 2 번째 그림 시작
ax[1].plot(
    mmf_rrp["Date"],
    mmf_rrp["Amount Accepted"] / 1e12,
    label="MMF RRP",
    linestyle="-",
    lw=2,
    color="blue",
)

# 단위 표시 및 출처:

ax[1].text(
    0,
    1.00,
    "(조 달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)

ax[1].text(
    0.0,
    -0.15,
    "출처: NY FED, 음영은 2023년 1월~5월",
    transform=ax[1].transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)

# 범례
ax[1].legend(loc="upper left")
ax[1].grid(False)
ax[1].set_ylim(0.0, 2.5)


# X축 눈금
for i in [0, 1]:
    ax[i].xaxis.set_major_locator(mdates.YearLocator())
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 음영 구간 추가
# 2023.1.1 - 2023.6.1
from datetime import datetime

shaded_periods = [(datetime(2023, 1, 1), datetime(2023, 6, 1))]

for i in [0, 1]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color="gray", alpha=0.2)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
plot_save()
