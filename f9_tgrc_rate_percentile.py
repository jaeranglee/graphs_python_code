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
# # [그림 9] 1일만기 국채담보 단기금융거래 이자율
# ## required file
#   - fred_api.py
#   - plot_def.py
#   - nyfed_api_all_rates.py
# %%

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

# %% [markdown]
# ## Fetch Data from NY FED Markets Data, Reference Rates
# - tgcr, sofr, bgcr, sofrai, effr, obfr 등 선택가능
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
# ## FRED series fetched
#   - Overnight Reverse Repurchase Agreements Award Rate: Treasury Securities Sold by the Federal Reserve in the Temporary Open Market Operations (RRPONTSYAWARD)
#       - Units: Percent,Not Seasonally Adjusted
#       - Frequency: Daily
# %%
from fred_api import fetch_fred_series

df_onrrp = fetch_fred_series("RRPONTSYAWARD", start_date=start, end_date=end)

# %% [markdown]
# ## Plot
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
