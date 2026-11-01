# %% [markdown]
# # [그림 54] 수입증가율과 재고투자 증가율
#
# ## 이 코드가 하는 일
# FRED에서 수입과 재고투자 자료를 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# 2025년 초 미국 기업들은 관세가 오르기 전에 물건을 미리 들여왔다. 그래서 수입이 크게 늘고 창고에 쌓인 재고도 늘었다.
# 수입은 GDP를 계산할 때 빼는 항목이라 GDP 성장률을 끌어내리고, 재고 증가는 반대로 끌어올린다.
# - 왼쪽: 국제수지 기준과 통관 기준 수입의 전년동월대비 증가율
# - 오른쪽: GDP 통계의 재고투자와 수입 증가율
#
# ## 결과물
# pic_jpg/f54_import_inv.jpg, pic_tif/f54_import_inv.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기(FRED API key 필요)
#
# ## 자료 받기 (FRED)
# - 국제수지 기준 상품·서비스 수입 (BOPTIMP), 통관 기준 상품 수입 (IMP0004): pct_change(12)로 전년동월대비 증가율
# - GDP 성장률에 대한 재고투자의 기여도 (A014RY2Q224SBEA)
# - GDP 통계의 수입 (NA000342Q): pct_change()로 전기 대비 증가율
# - 기업재고 (BUSINV): 불러오지만 그림에는 쓰지 않는다.
# - 2021년 이후를 그린다.
# %%
import matplotlib.pyplot as plt
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

start = "2020-01-01"
end = "2026-01-01"

# Fetch series
# ---------------------
from fred_api import fetch_fred_series

# 각 시리즈에서 필요한 열 추출
bopimp = fetch_fred_series("BOPTIMP", start_date=start, end_date=end)
imp0004 = fetch_fred_series("IMP0004", start_date=start, end_date=end)
businv = fetch_fred_series("BUSINV", start_date=start, end_date=end)
# Contributions to percent change in real gross domestic product: Gross private domestic investment: Change in private inventories (A014RY2Q224SBEA)
invq1 = fetch_fred_series("A014RY2Q224SBEA", start_date=start, end_date=end)
invq = fetch_fred_series("NA000342Q", start_date=start, end_date=end)


# 전년동기대비 (YoY) 계산
bopimp["YoY"] = bopimp["BOPTIMP"].pct_change(12) * 100
imp0004["YoY"] = imp0004["IMP0004"].pct_change(12) * 100

# 전월대비 (MoM) 계산
# businv['MoM'] = businv['BUSINV'].pct_change() * 100
invq["MoM"] = invq["NA000342Q"].pct_change() * 100

# 2021년 이후로 필터링
bopimp = bopimp[bopimp["observation_date"] >= "2021-01-01"]
imp0004 = imp0004[imp0004["observation_date"] >= "2021-01-01"]
businv = businv[businv["observation_date"] >= "2021-01-01"]
invq = invq[invq["observation_date"] >= "2021-01-01"]

# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: 수입 (전년동기대비)
ax[0].plot(
    bopimp["observation_date"],
    bopimp["YoY"],
    label="국제수지기준 수입",
    lw=2,
    color="blue",
)
ax[0].plot(
    imp0004["observation_date"],
    imp0004["YoY"],
    label="통관기준 수입",
    lw=2,
    color="black",
)
ax[0].axhline(y=0, color="gray", linestyle="--")

ax[0].legend()
ax[0].xaxis.set_major_locator(mdates.YearLocator(1))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
ax[0].text(
    0,
    1.00,
    "(%, 전년동월대비)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax[0].text(
    0.0, -0.15, "출처: BEA, FRED", transform=ax[0].transAxes, fontsize=10, ha="left"
)
ax[0].grid(False)

# 오른쪽: 재고 (전월대비)
# ax[1].plot(businv['observation_date'], businv['BUSINV'], label='BUSINV', lw=2, color='green')
ax[1].plot(
    invq1["observation_date"],
    invq1["A014RY2Q224SBEA"],
    label="GDP기준 재고투자",
    lw=2,
    color="black",
)
ax[1].plot(
    invq["observation_date"], invq["MoM"], label="GDP기준 수입", lw=2, color="blue"
)
ax[1].axhline(y=0, color="gray", linestyle="--")
ax[1].set_ylim(-5, 14)

ax[1].legend()
ax[1].xaxis.set_major_locator(mdates.YearLocator(1))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


# 단위 표시 및 출처
ax[1].text(
    0,
    1.00,
    "(%, 전기대비)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)
ax[1].text(
    0.0, -0.15, "출처: BEA, FRED", transform=ax[1].transAxes, fontsize=10, ha="left"
)
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
