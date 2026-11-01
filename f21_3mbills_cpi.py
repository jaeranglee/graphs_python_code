# %% [markdown]
# # [그림 21] 제2차 세계대전 전후 국채 수익률, 소비자물가 상승률
#
# ## 이 코드가 하는 일
# FRED에서 1941~1952년의 3개월 국채금리와 소비자물가를 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# 제2차 세계대전 동안 미국 정부는 전쟁 비용을 마련하려고 국채를 많이 발행했다.
# 연준은 정부가 싼 이자로 돈을 빌릴 수 있도록 3개월 국채금리를 0.375%에 묶어 두었다.
# 전쟁이 끝난 뒤 물가가 크게 올랐지만 금리는 낮게 묶여 있었고, 1951년 재무부와 연준이 합의(Accord)한 뒤에야
# 연준이 금리를 스스로 정하게 되었다. 금리를 낮게 묶으면 물가를 잡기 어렵다는 점을 보여주는 역사적 사례이다.
#
# ## 결과물
# pic_jpg/f21_3mbills_cpi.jpg, pic_tif/f21_3mbills_cpi.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 경기침체 기간(nber_recession), 그림 저장
# - fred_api.py: FRED 자료 받기
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

start = "1941-01-01"
end = "1952-01-01"

from fred_api import *

# %% [markdown]
# ## 자료 받기 (FRED)
# - 3개월 국채금리 (TB3MS), 월별
# - 소비자물가지수 (CPIAUCNS, 계절조정 전): pct_change(12)로 전년동월대비 상승률을 구한다.
# ## 그리기
# - 왼쪽: 3개월 국채금리, 오른쪽: 소비자물가 상승률
# - nber_recession()으로 이 기간의 경기침체 기간을 받아 두 그림에 회색으로 칠한다.
# %%
df_cpins = fetch_fred_series("CPIAUCNS", start_date=start, end_date=end)
df0 = fetch_fred_series("TB3MS", start_date=start, end_date=end)

# CPI YoY 계산
df_cpins["yoy_cpi"] = (df_cpins["CPIAUCNS"].pct_change(periods=12) * 100).copy()
cpi = df_cpins

# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽:
ax[0].plot(
    df0["observation_date"], df0["TB3MS"], label="T-bill 3개월", lw=2, color="blue"
)


ax[0].legend(loc="upper left", bbox_to_anchor=(0, 1.0))
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

ax[0].xaxis.set_major_locator(mdates.YearLocator(2))
# ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[0].text(
    0.0,
    -0.15,
    "출처: FRED, 음영은 경기침체 기간",
    transform=ax[0].transAxes,
    fontsize=10,
    ha="left",
)
ax[0].grid(False)

# 오른쪽: CPI

ax[1].plot(
    cpi["observation_date"], cpi["yoy_cpi"], label="소비자물가", lw=2, color="blue"
)

ax[1].legend(loc="upper left", bbox_to_anchor=(0, 1))
ax[1].xaxis.set_major_locator(mdates.YearLocator(2))

# 단위 표시 및 출처
ax[1].text(
    0,
    1.00,
    "(%)",
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
    "출처: FRED, 음영은 경기침체 기간",
    transform=ax[1].transAxes,
    fontsize=10,
    ha="left",
)
ax[1].grid(False)

# recession 기간표시
recession_periods = nber_recession(start=start, end=end)

# 두 그래프에 음영 처리
for peak, trough in recession_periods:
    ax[0].axvspan(peak, trough, color="gray", alpha=0.3)
    ax[1].axvspan(peak, trough, color="gray", alpha=0.3)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
