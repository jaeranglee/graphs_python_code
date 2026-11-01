# %% [markdown]
# # [그림 3] CRE 대출, 주택대출, CRE가격과 공동주택가격 상승률
#
# ## 이 코드가 하는 일
# FRED에서 은행 대출과 부동산 가격 자료를 받아 그림 세 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# CRE(Commercial Real Estate, 상업용 부동산)는 사무실, 상가, 호텔 같은 건물이다.
# 코로나 이후 재택근무가 늘면서 사무실이 비고 CRE 가격이 떨어졌다. CRE 대출을 많이 가진 은행, 특히 중소은행의 부실 우려가 커졌다.
# - 왼쪽: 상업은행의 CRE 대출 잔액과, 그중 중소은행이 차지하는 비중
# - 가운데: 주택대출 잔액과, 그중 중소은행 비중
# - 오른쪽: CRE 가격과 공동주택(아파트 등 다가구 주택) 가격의 1년 전 대비 상승률
#
# ## 결과물
# pic_jpg/f3_cre.jpg, pic_tif/f3_cre.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정(set_fonts), 그림 저장(plot_save), FRED 자료 받기(fetch_fred_series)
# - fred_api.py: fetch_fred_series가 실제로 들어 있는 파일(plot_def.py가 대신 불러온다)
# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# #폰트 설정
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

start = "2022-01-01"
end = "2025-10-01"

# #Fetch series from FRED
# ##상업은행 CRE대출

# %% [markdown]
# ## 자료 받기 (FRED)
# 괄호 안은 FRED의 자료 이름(series id)이다.
# - 상업은행 CRE 대출 (CREACBW027SBOG)
# - 상업은행 주택대출 (RREACBW027SBOG)
# - 상업은행 총신용 (TOTBKCR): 불러와서 합쳐 두지만 그림에는 쓰지 않는다.
# - 중소은행 CRE 대출 (CRESCBW027SBOG)
# - 중소은행 주택대출 (RRESCBW027SBOG)
# - CRE 가격의 1년 전 대비 변화율 (COMREPUSQ159N, IMF 자료)
# - 공동주택 가격 (BOGZ1FL075035403Q, 분기 자료): pct_change(4)로 4분기 전, 즉 1년 전 대비 상승률을 계산한다.
#
# ## 자료 가공
# - pd.merge로 대출 자료들을 날짜 기준으로 합친다.
# - 중소은행 비중(%) = 중소은행 대출 / 전체 상업은행 대출 x 100
# - 대출 잔액은 10억 달러 단위라서 1e3(=1,000)으로 나눠 조 달러로 그린다.
#
# ## 그리기
# 왼쪽과 가운데 그림은 대출 잔액(왼쪽 y축)과 중소은행 비중(오른쪽 y축)을 함께 그린다.
# 두 축의 범례를 하나로 합쳐 선과 겹치지 않는 오른쪽 아래에 둔다.
# %%

df_cre = fetch_fred_series("CREACBW027SBOG", start_date=start, end_date=end)
df_home = fetch_fred_series("RREACBW027SBOG", start_date=start, end_date=end)
df_credit = fetch_fred_series("TOTBKCR", start_date=start, end_date=end)
df_cre_small = fetch_fred_series("CRESCBW027SBOG", start_date=start, end_date=end)
df_home_small = fetch_fred_series("RRESCBW027SBOG", start_date=start, end_date=end)
df_price = fetch_fred_series("COMREPUSQ159N", start_date=start, end_date=end)

start_new = "2021-01-01"
end_new = "2025-01-31"

df_home_price = fetch_fred_series(
    "BOGZ1FL075035403Q", start_date=start_new, end_date=end_new
)
df_home_price["yoy"] = df_home_price["BOGZ1FL075035403Q"].pct_change(periods=4) * 100

# ##Merge on observation_date
df_merged = pd.merge(df_cre, df_credit, on="observation_date", how="inner")
df_merged = pd.merge(df_merged, df_home, on="observation_date", how="inner").copy()
df_merged = pd.merge(df_merged, df_cre_small, on="observation_date", how="inner")
df_merged = pd.merge(df_merged, df_home_small, on="observation_date", how="inner")
df_merged["ratio_cre"] = (df_merged["CREACBW027SBOG"] / df_merged["TOTBKCR"]) * 100
df_merged["ratio_home"] = (df_merged["RREACBW027SBOG"] / df_merged["TOTBKCR"]) * 100
df_merged["ratio_cre_small"] = (
    df_merged["CRESCBW027SBOG"] / df_merged["CREACBW027SBOG"]
) * 100
df_merged["ratio_home_small"] = (
    df_merged["RRESCBW027SBOG"] / df_merged["RREACBW027SBOG"]
) * 100

# Plotting
fig, ax = plt.subplots(1, 3, figsize=(9, 4.5), constrained_layout=True)

ax_left = ax[0]
ax_right = ax_left.twinx()

ax_left.plot(
    df_merged["observation_date"],
    df_merged["CREACBW027SBOG"] / 1e3,
    label="CRE대출(좌축)",
    color="blue",
    lw=2,
)
ax_right.plot(
    df_merged["observation_date"],
    df_merged["ratio_cre_small"],
    label="소규모은행 비중(우축)",
    color="black",
    lw=2,
)
# 두 축의 범례를 하나로 합친다.
h1, l1 = ax_left.get_legend_handles_labels()
h2, l2 = ax_right.get_legend_handles_labels()
ax_left.legend(h1 + h2, l1 + l2, loc="lower right")


ax[0].xaxis.set_major_locator(mdates.YearLocator())
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
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
    1,
    1.00,
    "(%)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax[0].text(0.0, -0.15, "출처: FRED", transform=ax[0].transAxes, fontsize=10, ha="left")
ax[0].grid(False)

ax_left1 = ax[1]
ax_right1 = ax_left1.twinx()

ax_left1.plot(
    df_merged["observation_date"],
    df_merged["RREACBW027SBOG"] / 1e3,
    label="주택대출(좌축)",
    color="blue",
    lw=2,
)
ax_right1.plot(
    df_merged["observation_date"],
    df_merged["ratio_home_small"],
    label="소규모은행 비중(우축)",
    color="black",
    lw=2,
)

# 두 축의 범례를 하나로 합친다.
h1, l1 = ax_left1.get_legend_handles_labels()
h2, l2 = ax_right1.get_legend_handles_labels()
ax_left1.legend(h1 + h2, l1 + l2, loc="lower right")


ax[1].xaxis.set_major_locator(mdates.YearLocator())
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

ax_left1.text(
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
ax_right1.text(
    1,
    1.00,
    "(%)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)

ax[1].text(0.0, -0.15, "출처: FRED", transform=ax[1].transAxes, fontsize=10, ha="left")
ax[1].grid(False)

# Plotting
ax[2].plot(
    df_price["observation_date"],
    df_price["COMREPUSQ159N"],
    label="CRE 가격",
    color="black",
    lw=2,
)
ax[2].plot(
    df_home_price["observation_date"],
    df_home_price["yoy"],
    label="공동주택 가격",
    color="blue",
    lw=2,
)
ax[2].axhline(y=0, color="gray", linestyle="--")

ax[2].legend(loc="upper left", bbox_to_anchor=(0.3, 1))
ax[2].xaxis.set_major_locator(mdates.YearLocator())
ax[2].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
ax[2].text(
    0,
    1.00,
    "(%, 전년동기대비)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[2].transAxes,
)
ax[2].text(
    0.0, -0.15, "출처: IMF, FRED", transform=ax[2].transAxes, fontsize=10, ha="left"
)
ax[2].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
