# %% [markdown]
# # [그림 45] 미국채 수익률
# # [그림 46] 연준의 미국채 보유액
#
# ## 이 코드가 하는 일
# FRED에서 국채금리와 연준의 국채 보유액을 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# - 왼쪽(그림 45): 10년물과 2년물 국채금리. 2002년 이후의 긴 흐름을 본다.
# - 오른쪽(그림 46): 연준이 가진 국채 전체와 그중 중장기국채
# - 음영은 재무부가 국채 바이백(이미 발행한 국채를 만기 전에 되사는 것)을 다시 시작한 2024년 5월 이후이다.
#
# ## 결과물
# pic_jpg/f45_tb_yield_fed_tb_holdings.jpg, pic_tif/f45_tb_yield_fed_tb_holdings.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장, FRED 자료 받기
# - fred_api.py: fetch_fred_series가 실제로 들어 있는 파일(plot_def.py가 대신 불러온다)
#
# ## 자료 받기 (FRED)
# - 10년만기 국채금리 (DGS10), 2년만기 국채금리 (DGS2)
# - 연준 보유 국채 합계 (WSHOTSL), 연준 보유 중장기국채 (WSHONBNL): 백만 달러를 1e6으로 나눠 조 달러로 그린다.
# %%
import pandas as pd
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

start = "2002-01-01"
end = "2099-12-31"

# Fetch from FRED

# 데이터 수집
df0 = fetch_fred_series("DGS10", start_date=start, end_date=end)
df1 = fetch_fred_series("DGS2", start_date=start, end_date=end)
df2 = fetch_fred_series("WSHOTSL", start_date=start, end_date=end)
df3 = fetch_fred_series("WSHONBNL", start_date=start, end_date=end)

tb1 = pd.merge(df0, df1, on="observation_date").copy()


# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: 국채금리
ax[0].plot(tb1["observation_date"], tb1["DGS10"], label="10년물", lw=1.5, color="black")
ax[0].plot(tb1["observation_date"], tb1["DGS2"], label="2년물", lw=1.5, color="blue")


ax[0].legend(loc="upper left", bbox_to_anchor=(0.35, 1))
ax[0].xaxis.set_major_locator(mdates.YearLocator(3))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
ax[0].text(
    0,
    1.00,
    "(%)",
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
    "출처: FRED, 음영은 국채 바이백 기간",
    transform=ax[0].transAxes,
    fontsize=10,
    ha="left",
)
ax[0].grid(False)

# 오른쪽: 연준 국채보유액

ax[1].plot(
    df2["observation_date"], df2["WSHOTSL"] / 1e6, label="국채", lw=2, color="black"
)
ax[1].plot(
    df3["observation_date"],
    df3["WSHONBNL"] / 1e6,
    label="중장기 국채",
    lw=2,
    color="blue",
)

ax[1].legend(loc="upper left", bbox_to_anchor=(0.35, 1))
ax[1].xaxis.set_major_locator(mdates.YearLocator(3))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
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
    "출처: FRED, 음영은 국채 바이백 기간",
    transform=ax[1].transAxes,
    fontsize=10,
    ha="left",
)
ax[1].grid(False)

# 음영 구간 추가: 바이백 실시 시기
from datetime import datetime

shaded_periods = [
    # (datetime(2014, 1, 1), datetime(2023, 12, 31)),
    (datetime(2024, 5, 1), datetime(2025, 12, 31))
]

for i in [0, 1]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color="gray", alpha=0.2)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
