# %% [markdown]
# # [그림 9] 1일만기 국채담보 단기금융거래 이자율
#
# ## 이 코드가 하는 일
# 뉴욕 연준에서 TGCR 금리와 그 분포를, FRED에서 연준 RRP 금리를 받아 한 그림에 그린다.
#
# ## 그림이 다루는 내용
# TGCR(Tri-party General Collateral Rate)은 국채를 담보로 하루 동안 돈을 빌리고 빌려줄 때의 금리이다.
# 연준 RRP 금리는 MMF가 연준에 돈을 맡길 때 받는 금리라서, 시장 금리가 그보다 크게 낮아지기 어렵다(금리의 바닥 역할).
# 그날 거래된 금리들이 얼마나 퍼져 있는지(백분위)를 띠로 함께 그려, 금리가 고르게 형성됐는지 볼 수 있다.
#
# ## 결과물
# pic_jpg/f9_tgcr_rate_percentile.jpg, pic_tif/f9_tgcr_rate_percentile.tif
#
# ## 필요한 파일 (defs 폴더)
# - fred_api.py: FRED 자료 받기
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - nyfed_api_all_rates.py: 뉴욕 연준 기준금리 받기(fetch_all_secured_rates)
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

from plot_def import *

set_fonts()

# %% [markdown]
# ## 자료 받기 (뉴욕 연준 Markets Data)
# - fetch_all_secured_rates()는 여러 기준금리를 한꺼번에 받는다. Type 열에서 원하는 금리만 고른다.
# - rate_type_filter에 'tgcr' 대신 'sofr', 'bgcr', 'effr', 'obfr' 등을 넣으면 다른 금리를 그릴 수 있다.
# - 금리와 함께 1·25·75·99 백분위 금리가 들어 있다.
#   예를 들어 25 백분위는 그날 거래의 25%가 그 금리 이하에서 이루어졌다는 뜻이다.
# %%
from nyfed_api_all_rates import fetch_all_secured_rates

start = "2023-01-01"
end = "2025-10-01"

df_all = fetch_all_secured_rates(start_date=start, end_date=end)

rate_type_filter = "tgcr"

df_tgcr = df_all[df_all["Type"] == rate_type_filter.upper()].copy()

# 날짜 정렬

df_tgcr = df_tgcr.sort_values("Date")

# %% [markdown]
# ## 자료 받기 (FRED)
# - 연준 RRP 금리 (RRPONTSYAWARD): 하루 단위, %
# %%
from fred_api import fetch_fred_series

df_onrrp = fetch_fred_series("RRPONTSYAWARD", start_date=start, end_date=end)

# %% [markdown]
# ## 그리기
# - 선: TGCR(검정)과 RRP 금리
# - 띠: TGCR의 25~75 백분위 범위와 1~99 백분위 범위(fill_between으로 두 선 사이를 칠한다)
# %%
fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)

ax.plot(df_tgcr["Date"], df_tgcr["Rate"], label="TGCR", color="black", linewidth=2)
ax.plot(
    df_onrrp["observation_date"],
    df_onrrp["RRPONTSYAWARD"],
    label="O/N RRP",
    color="blue",
    linewidth=2,
)

# Percentile 구간을 면적(band)으로 표현
ax.fill_between(
    df_tgcr["Date"],
    df_tgcr["Percentile25"],
    df_tgcr["Percentile75"],
    color="skyblue",
    alpha=1,
    label="25th–75th Percentile",
)
ax.fill_between(
    df_tgcr["Date"],
    df_tgcr["Percentile1"],
    df_tgcr["Percentile99"],
    color="lightgray",
    alpha=0.5,
    label="1st–99th Percentile",
)
ax.set_ylim(4.0, 5.5)

# 점선 스타일 그리드 표시
ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.7)

plt.legend()

# 단위 표시 및 출처
ax.text(
    0,
    1.00,
    "(%)",
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
    "출처: New York FED, FRED",
    fontsize=10,
    ha="left",
    transform=ax.transAxes,
)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
