# %% [markdown]
# # [그림 51] 실질 달러인덱스, 금 현물가격, 실질실효 유로인덱스
#
# ## 이 코드가 하는 일
# FRED에서 달러인덱스와 유로 환율지수를, 한국은행 ECOS에서 금 가격을 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# - 왼쪽: 명목 달러인덱스와 실질 달러인덱스. 실질은 나라별 물가 차이를 반영해 달러의 실제 구매력을 비교한 것이다.
# - 오른쪽: 금 가격과 유로의 실질실효환율. 달러가 약해지는 시기에 금과 유로의 가치가 어떻게 움직였는지 본다.
# 2000년부터 그린다.
#
# ## 결과물
# pic_jpg/f51_real_dollar_and_gold.jpg, pic_tif/f51_real_dollar_and_gold.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기(FRED API key 필요)
# - bok_ecos_api.py: 한국은행 ECOS 자료 받기(ECOS API key 필요, defs/.env의 ECOS_API_KEY)
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정
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

start = "2000-01-01"
end = "2025-12-31"

# Fetch series from FRED
from fred_api import fetch_fred_series

# %% [markdown]
# ## 자료 받기 (FRED)
# - 명목 광의 달러인덱스 (DTWEXBGS)
# - 실질 광의 달러인덱스 (RTWEXBGS)
# - 유로 지역 실질실효환율 (RBXMBIS)
# %%
dbxy_df = fetch_fred_series("DTWEXBGS", start_date=start, end_date=end)

df0 = fetch_fred_series("RTWEXBGS", start_date=start, end_date=end)

df2 = fetch_fred_series("RBXMBIS", start_date=start, end_date=end)

# %% [markdown]
# ## 자료 받기 (한국은행 ECOS)
# - 금 현물가격, 월별: 통계표 코드 902Y003, 항목 코드 040101
# - fetch_ecos_series(이름, 통계표 코드, 항목코드1, 항목코드2, 항목코드3, 주기, start_date, end_date) 순서로 넣는다.
#   이 통계는 항목코드가 하나뿐이라 항목코드2, 3 자리에 빈 문자열 ""을 넣는다. 주기 "M"은 월별이다.
# - ECOS 홈페이지에서 통계를 검색하면 통계표 코드와 항목 코드를 확인할 수 있다.
# %%
from bok_ecos_api import fetch_ecos_series

series_list = [["Gold", "902Y003", "040101", "M"]]  # Gold data


dfs = {}

for name, stat_code, item_code, cycle in series_list:
    dfs[name] = fetch_ecos_series(
        name, stat_code, item_code, "", "", cycle, start_date=start, end_date=end
    )


# 중복 검증


for name in dfs:
    dfs[name] = dfs[name].drop_duplicates(subset="Date").reset_index(drop=True)

for name, df in dfs.items():
    dup_count = df.duplicated().sum()
    print(f"{name}: {dup_count} duplicates")

# %% [markdown]
# ## (참고) IMF에서 금 가격 받기
# 금 가격은 IMF 자료로도 받을 수 있다. 아래 코드를 ECOS 대신 쓰면 된다(이 파일에서는 실행하지 않는다).
# ```python
# from imf_api import fetch_imf_data
#
# gold = fetch_imf_data(data_set='IMF.RES,PCPS', country_id='G001',
#                       indicator_id='PGOLD',unit_id='USD',
#                       start_period=start, end_period=end,
#                       cycle='M')
# gold = gold.rename(columns={'OBS_VALUE': 'Value'})
# ```
# %%
# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: 달러인덱스
ax[0].plot(
    df0["observation_date"],
    df0["RTWEXBGS"],
    label="실질 달러인덱스",
    lw=2,
    color="blue",
)
ax[0].plot(
    dbxy_df["observation_date"],
    dbxy_df["DTWEXBGS"],
    label="명목 달러인덱스",
    lw=1,
    color="black",
)

ax[0].legend()
ax[0].xaxis.set_major_locator(mdates.YearLocator(3))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
ax[0].text(
    0,
    1.00,
    "(2006=100)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax[0].text(0.0, -0.15, "출처: FRED", transform=ax[0].transAxes, fontsize=10, ha="left")
ax[0].grid(False)


# 오른쪽, y축이 2개

ax_left = ax[1]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(
    dfs["Gold"]["Date"], dfs["Gold"]["Value"], label="금", lw=2, color="blue", alpha=1.0
)
ax_right.plot(
    df2["observation_date"],
    df2["RBXMBIS"],
    label="실질실효 유로인덱스",
    lw=2,
    color="black",
)

# 두 축의 범례를 하나로 합친다.
h1, l1 = ax_left.get_legend_handles_labels()
h2, l2 = ax_right.get_legend_handles_labels()
ax_left.legend(h1 + h2, l1 + l2, loc="lower right")

# 단위 표시
ax_left.text(
    0.12,
    1.00,
    "($/oz)",
    ha="right",
    va="bottom",
    color="red",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)
ax_right.text(
    1,
    1.00,
    "(2020=100)",
    ha="right",
    va="bottom",
    color="orange",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)


ax[1].xaxis.set_major_locator(mdates.YearLocator(3))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


# 출처

ax[1].text(
    0.0,
    -0.15,
    "출처: BOK ECOS, FRED",
    transform=ax[1].transAxes,
    fontsize=10,
    ha="left",
)
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
