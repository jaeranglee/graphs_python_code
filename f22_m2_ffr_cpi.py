# %% [markdown]
# # [그림 22] M2 증가율, 연방기금금리, 소비자물가 상승률
#
# ## 이 코드가 하는 일
# FRED에서 1968~1980년의 통화량(M2), 연방기금금리, 소비자물가를 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# 1970년대 미국은 물가가 크게 오른 '대인플레이션' 시기를 겪었다.
# 연준이 경기가 나빠질 때마다 금리를 빨리 내리고 통화량을 늘리자 물가가 다시 오르는 일이 되풀이됐다.
# - 왼쪽: M2(현금과 예금 등 넓은 의미의 통화량) 증가율과 연방기금금리
# - 오른쪽: 소비자물가 상승률
# 두 그림을 함께 보면 통화량이 늘고 금리가 낮아진 뒤에 물가가 오르는 흐름을 볼 수 있다.
#
# ## 결과물
# pic_jpg/f22_m2_ffr_cpi.jpg, pic_tif/f22_m2_ffr_cpi.tif
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

# fetch fred series

start = "1968-01-01"
end = "1980-01-01"

from fred_api import *

# %% [markdown]
# ## 자료 받기 (FRED)
# - M2 (MYAGM2USM052N): pct_change(12)로 전년동월대비 증가율을 구한다.
# - 실효연방기금금리 (RIFSPFFNB)
# - 소비자물가지수 (CPIAUCNS): pct_change(12)로 전년동월대비 상승률을 구한다.
# ## 그리기
# - 왼쪽: M2 증가율(왼쪽 y축)과 연방기금금리(오른쪽 y축). 두 축의 범례를 하나로 합쳐 선이 없는 오른쪽 아래에 둔다.
# - 오른쪽: 소비자물가 상승률. 범례는 오른쪽 아래에 둔다.
# - 두 그림 모두 NBER 경기침체 기간을 회색으로 칠한다.
# %%
df0 = fetch_fred_series("MYAGM2USM052N", start_date=start, end_date=end)
df1 = fetch_fred_series("RIFSPFFNB", start_date=start, end_date=end)
df_cpins = fetch_fred_series("CPIAUCNS", start_date=start, end_date=end)

df0["yoy_m2"] = df0["MYAGM2USM052N"].pct_change(periods=12) * 100

# 필요한 열 추출
m2 = df0[["observation_date", "yoy_m2"]].copy()

df1 = df1.set_index("observation_date")

df1 = df1.resample("ME").mean().copy()
ffr = df1.copy()

# YoY 계산
df_cpins["yoy_cpi"] = df_cpins["CPIAUCNS"].pct_change(periods=12) * 100
cpi = df_cpins.copy()

# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: M2, EFFR

ax_left = ax[0]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(m2["observation_date"], m2["yoy_m2"], label="M2", lw=2, color="black")
ax_right.plot(ffr.index, ffr["RIFSPFFNB"], label="연방기금금리", lw=2, color="blue")

# 두 축의 범례를 하나로 합친다.
h1, l1 = ax_left.get_legend_handles_labels()
h2, l2 = ax_right.get_legend_handles_labels()
ax_left.legend(h1 + h2, l1 + l2, loc="lower right")
ax_left.yaxis.label.set_visible(True)

ax_left.text(
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

ax[1].legend(loc="lower right")

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

# USREC 기준으로 recession 음영 처리 (확장기: 0, 침체기: 1)

recession_periods = nber_recession(start=start, end=end)

# 두 그래프에 음영 처리
for peak, trough in recession_periods:
    ax[0].axvspan(peak, trough, color="gray", alpha=0.3)
    ax[1].axvspan(peak, trough, color="gray", alpha=0.3)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
