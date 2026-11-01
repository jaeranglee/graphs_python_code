# %% [markdown]
# # [그림 36] 단기 자금시장 유동성과 주식시장 변동성
#
# ## 이 코드가 하는 일
# FRED에서 단기 금리 두 개와 주가 변동성 지수를 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# - 왼쪽: 3개월 CP 금리 - 3개월 국채금리. CP는 기업이 짧게 돈을 빌릴 때 발행하는 어음이다.
#   돈을 구하기 어려워지면 기업이 더 높은 금리를 줘야 하므로 이 차이(스프레드)가 커진다. 자금시장의 긴장 정도를 보여준다.
# - 오른쪽: 주가 변동성 지수. 투자자들이 앞으로 주가가 크게 흔들릴 것으로 예상할수록 높아져 '공포지수'라고도 부른다.
#
# ## 결과물
# pic_jpg/f36_cb_tb_vix.jpg, pic_tif/f36_cb_tb_vix.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정

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

start = "2021-01-01"
end = "2025-10-01"

from fred_api import fetch_fred_series

# %% [markdown]
# ## 자료 받기 (FRED)
# - 3개월 국채금리 (DTB3)
# - 3개월 AA등급 금융기관 CP 금리 (RIFSPPFAAD90NB)
# - CBOE 다우존스 변동성 지수 (VXDCLS): 그림에는 VIX로 표시한다.
# ## 그리기
# - 왼쪽: CP 금리에서 국채금리를 뺀 스프레드, 오른쪽: 변동성 지수
# %%
df0 = fetch_fred_series("DTB3", start_date=start, end_date=end)

df2 = fetch_fred_series("RIFSPPFAAD90NB", start_date=start, end_date=end)

df4 = fetch_fred_series("VXDCLS", start_date=start, end_date=end)


df0 = pd.merge(df0, df2, on="observation_date", how="inner").copy()
df0 = pd.merge(df0, df4, on="observation_date", how="inner").copy()

selected_terms_to_plot = ["observation_date", "DTB3", "RIFSPPFAAD90NB", "VXDCLS"]
df0 = df0.dropna(subset=selected_terms_to_plot)[selected_terms_to_plot].copy()

df0["cp"] = df0["RIFSPPFAAD90NB"] - df0["DTB3"]


# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: cp, sofr
ax[0].plot(df0["observation_date"], df0["cp"], label="3개월 CP-TB", lw=2, color="blue")

ax[0].axhline(y=0, color="gray", linestyle="--")
ax[0].legend()
ax[0].xaxis.set_major_locator(mdates.YearLocator(1))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
ax[0].text(
    0,
    1.00,
    "(%p)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax[0].text(0.0, -0.15, "출처: FRED", transform=ax[0].transAxes, fontsize=10, ha="left")
ax[0].grid(False)

# 오른쪽: VIX

ax[1].plot(df0["observation_date"], df0["VXDCLS"], label="VIX", lw=2, color="black")

ax[1].legend()
ax[1].xaxis.set_major_locator(mdates.YearLocator(1))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


# 단위 표시 및 출처

ax[1].text(0.0, -0.15, "출처: FRED", transform=ax[1].transAxes, fontsize=10, ha="left")
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
