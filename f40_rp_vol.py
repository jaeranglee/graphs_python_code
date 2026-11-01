# %% [markdown]
# # [그림 40] 연준의 RP 거래
#
# ## 이 코드가 하는 일
# 뉴욕 연준에서 연준의 RP(레포) 운영 결과를 받아, 날짜별 대출액을 그린다.
#
# ## 그림이 다루는 내용
# RP는 연준이 금융회사로부터 국채를 담보로 받고 하루 동안 돈을 빌려주는 거래이다(RRP와 방향이 반대).
# 시장에서 돈이 모자라 레포 금리가 오르면 금융회사들이 연준의 RP를 이용한다.
# 분기 말처럼 자금 수요가 몰리는 날에 이용액이 크게 늘어나는 모습을 본다.
#
# ## 결과물
# pic_jpg/f40_rp_vol.jpg, pic_tif/f40_rp_vol.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - nyfed_api_rp.py: 뉴욕 연준 RP 운영 결과 받기(fetch_rp_operation, API key 필요 없음)
# - fred_api.py: FRED의 RPONTTLD로 같은 그림을 그리는 코드를 문자열로 막아 두었다. 결과는 같다.
#
# ## 그리기
# - Type이 Repo인 거래만 골라 하루 낙찰액(Accepted)을 더하고, 10억 달러 단위로 그린다.
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set font depending on the platform
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


start = "2023-01-01"
end = "2025-12-31"

"""
# fetch from FRED
# same results as with NY FED Markets Data 
# Overnight Repurchase Agreements: Total Securities Purchased by the Federal Reserve
# in the Temporary Open Market Operations (RPONTTLD) in Billion US Dollars

from fred_api import fetch_fred_series

df = fetch_fred_series(series_id="RPONTTLD", start_date=start, end_date=end)

# 그래프 그리기

fig, ax = plt.subplots(figsize=(8, 4.5),constrained_layout=True)

ax.plot(df['observation_date'], df['RPONTTLD'], label='RP', color='blue', lw=2)


ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

ax.text(0, 1.00, '(십억 달러)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)
plt.grid(False)

ax.text(0.0, -0.15, "출처: FRED", transform=ax.transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')
"""


# fetch from NY FED Markets Data, case wise
# FRED 와 동일한 결과

from nyfed_api_rp import *

df = fetch_rp_operation(start_date=start, end_date=end)

# 데이터 전처리
# 날짜, 숫자 변환

df["Accepted"] = pd.to_numeric(df["Accepted"], errors="coerce") / 1e9
df["Limit"] = pd.to_numeric(df["Limit"], errors="coerce") / 1e9

# 날짜 변환 실패(NaT) 행 제거
df = df.dropna(subset=["Date"])


# 필요한 증권 종류만 필터링
type_to_plot = "Repo"

df_filtered = df[df["Type"] == type_to_plot]

# Sum accepted amount by day
# NY Fed has term filter, [overnight, term]
df_daily_sum = df_filtered.groupby(df["Date"].dt.date)["Accepted"].sum().reset_index()


# --- 시각화 ---

fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

ax.plot(df_daily_sum["Date"], df_daily_sum["Accepted"], label="RP", lw=2, color="blue")


ax.xaxis.set_major_locator(
    mdates.MonthLocator(interval=6)
)  # 6 month 간격으로 눈금 표시
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))  # year-month 표시

ax.text(
    0, 1.00, "(10억 달러)", ha="left", va="bottom", transform=ax.transAxes, fontsize=12
)
ax.text(0, -0.15, "출처: NY Fed Markets Data", transform=ax.transAxes, fontsize=10)
ax.grid(False)

plt.legend()


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
