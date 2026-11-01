# %% [markdown]
# # [그림 11] 1일물 금리
#
# ## 이 코드가 하는 일
# FRED와 뉴욕 연준에서 하루짜리(1일물) 금리 여러 개를 받아 한 그림에 그린다.
#
# ## 그림이 다루는 내용
# 연준은 정책금리를 하나의 숫자가 아니라 범위(예: 4.25~4.50%)로 정한다.
# 그리고 두 가지 금리로 시장 금리를 그 범위 안에 묶어 둔다.
# - IORB: 은행이 연준에 맡긴 지급준비금에 연준이 주는 이자. 시장 금리의 위쪽 기준 역할을 한다.
# - RRP 금리: MMF 등이 연준에 돈을 맡길 때 받는 금리. 시장 금리의 아래쪽 바닥 역할을 한다.
# SOFR, TGCR(국채담보 레포 금리), EFFR(은행 간 무담보 금리)이 이 사이에서 움직이는 모습을 본다.
#
# ## 결과물
# pic_jpg/f11_on_rates.jpg, pic_tif/f11_on_rates.tif
#
# ## 필요한 파일 (defs 폴더)
# - fred_api.py: FRED 자료 받기
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - nyfed_api_all_rates.py: 뉴욕 연준 기준금리 받기(fetch_all_secured_rates)
# %%
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

set_fonts()

# %% [markdown]
# ## 자료 받기 (FRED)
# - IORB, SOFR
# - EFFR: 불러오지만 그림에는 아래 뉴욕 연준 자료의 EFFR을 쓴다.
# - 정책금리 범위의 위쪽(DFEDTARU)과 아래쪽(DFEDTARL): 한 dataframe으로 합쳐 범위를 색칠한다.
# - 연준 RRP 금리 (RRPONTSYAWARD)
# ## 자료 받기 (뉴욕 연준 Markets Data)
# - fetch_all_secured_rates()로 기준금리를 받아 TGCR과 EFFR을 고른다.
# ## 기간
# - 2024년 8월 1일부터 2025년 10월 31일까지
# %%
from fred_api import fetch_fred_series

start = "2024-08-01"
end = "2025-10-31"

# fetch IORB and SOFR from FRED
iorb = fetch_fred_series("IORB", start_date=start, end_date=end)
sofr = fetch_fred_series("SOFR", start_date=start, end_date=end)

# Effective Federal Funds Rate (EFFR)
effr = fetch_fred_series("EFFR", start_date=start, end_date=end)

target_u = fetch_fred_series("DFEDTARU", start_date=start, end_date=end)
target_l = fetch_fred_series(
    "DFEDTARL", start_date=start, end_date=end
)  # Lower Target 추가
target_u["DFEDTARL"] = target_l["DFEDTARL"]  # 상하한 결합

rrp = fetch_fred_series("RRPONTSYAWARD", start_date=start, end_date=end)

# New York Fed Markets Data fetch
from nyfed_api_all_rates import fetch_all_secured_rates

# fetch secured over night rates
df_all = fetch_all_secured_rates(start_date=start, end_date=end, rate_type_filter=None)

# tgcr, sofr, bgcr, sofrai, effr, obfr 등 선택가능
tgcr = df_all[df_all["Type"] == "TGCR"].copy()
effr1 = df_all[df_all["Type"] == "EFFR"].copy()

# 그래프 그리기
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

# 왼쪽:
ax.plot(
    iorb["observation_date"], iorb["IORB"], label="IORB", lw=1, ls="-", color="blue"
)
ax.plot(
    sofr["observation_date"], sofr["SOFR"], label="SOFR", lw=2, ls=":", color="black"
)
ax.plot(tgcr["Date"], tgcr["Rate"], label="TGCR", lw=2, color="blue")

ax.plot(effr1["Date"], effr1["Rate"], label="EFFR", lw=2, color="black")
ax.plot(
    rrp["observation_date"],
    rrp["RRPONTSYAWARD"],
    label="O/N RRP",
    lw=1,
    ls="--",
    color="black",
)

# target rate bound in filled lines
ax.fill_between(
    target_u["observation_date"],
    target_u["DFEDTARU"],
    target_u["DFEDTARL"],
    color="gray",
    alpha=0.2,
    label="Target Range",
)

ax.legend(loc="upper right", bbox_to_anchor=(1, 1))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.text(0, 1.00, "(%)", ha="left", va="bottom", transform=ax.transAxes, fontsize=12)
ax.text(0, -0.15, "출처: FRED, NY FED", transform=ax.transAxes, fontsize=10)

# grid with dashed lines
ax.grid(True, linestyle="--", color="gray", linewidth=0.7, alpha=0.7)

# 저장 및 출력
plot_save()
