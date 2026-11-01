# %% [markdown]
# # [그림 31] 주요 국채 보유주체
#
# ## 이 코드가 하는 일
# FRED에서 누가 미국 국채를 얼마나 가지고 있는지 받아 한 그림에 그린다.
#
# ## 그림이 다루는 내용
# 연준의 자금순환표(Financial Accounts of the United States)는 경제 주체별로 어떤 자산을 얼마나 가졌는지 정리한 통계이다.
# 외국, 가계, MMF, 연금, 보험회사가 가진 미국 국채가 1990년 이후 어떻게 변해 왔는지 비교한다.
#
# ## 결과물
# pic_jpg/f31_treasury_holders.jpg, pic_tif/f31_treasury_holders.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
# %%
import pandas as pd
import matplotlib.pyplot as plt

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

# %% [markdown]
# ## 자료 받기 (FRED, 분기 자료, 백만 달러)
# 그림에 쓰는 자료는 아래 다섯 가지이다. 1e6으로 나눠 조 달러로 그린다.
# - 외국 전체 (ROWTSEQ027S)
# - 가계와 비영리단체 (HNOTSAQ027S)
# - MMF (BOGZ1FL633061105Q)
# - 연금 (BOGZ1FL593061105Q)
# - 보험회사 (BOGZ1FL523061105Q)
#
# series_ids에 추가하면 함께 그려 볼 수 있는 자료
# - 가계 보유 국채의 시장가치 (BOGZ1LM153061105Q)
# - 외국 공적기관(중앙은행 등) 보유 (BOGZ1FL263061130Q)
# - 외국 보유 국채의 시장가치 (BOGZ1LM263061105Q)
# - 뮤추얼펀드 (BOGZ1FL653061105Q), 국내 금융기관 전체 (FBTSAAQ027S): 코드에 주석으로 남겨 두었다.
# - 비금융 기업 (TSABSNNCB): 단위가 10억 달러라서 1e3으로 나눠야 한다.
# %%
start = "1990-01-01"
end = "2025-09-01"

series_ids = {
    "외국전체": "ROWTSEQ027S",
    "가계와 비영리단체": "HNOTSAQ027S",
    "MMF": "BOGZ1FL633061105Q",
    "연금": "BOGZ1FL593061105Q",
    "보험": "BOGZ1FL523061105Q",
    #    "뮤추얼펀드": "BOGZ1FL653061105Q"
    #    "금융기관": "FBTSAAQ027S"
}

color_map = {
    "외국전체": "black",
    "가계와 비영리단체": "blue",
    "MMF": "black",
    "연금": "blue",
    "보험": "gray",
}

lw_map = {"외국전체": 2, "가계와 비영리단체": 2, "MMF": 2, "연금": 1, "보험": 1}

# plot style combos
ls_map = {
    "외국전체": "-",
    "가계와 비영리단체": "--",
    "MMF": ":",
    "연금": "-.",
    "보험": "-",
}

from fred_api import fetch_fred_series


# 모든 만기 데이터 가져오기
all_data = {}
for term, sid in series_ids.items():
    df = fetch_fred_series(sid, start_date=start, end_date=end)

    df = df.rename(columns={df.columns[-1]: "value"})
    all_data[term] = df.set_index("observation_date")["value"]

# 병합
# 백만을 조 단위로 변환
df_all = pd.DataFrame(all_data) / 1e6


# print(df_all)

# 2020년 이후 데이터 필터링
df_filtered = df_all[df_all.index >= "1990-01-01"]


# 그래프 그리기

fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

# 모든 컬럼을 line plot (zip 이용)
for col, series in zip(df_filtered.columns, df_filtered.T.values):
    ax.plot(
        df_filtered.index,
        series,
        label=col,
        color=color_map.get(col),
        lw=lw_map.get(col),
        ls=ls_map.get(col),
    )


ax.text(
    0,
    1.00,
    "(조 달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)

# plt.legend()
ax.text(
    0.0,
    -0.15,
    "출처: FRED, 자금순환표",
    transform=ax.transAxes,
    fontsize=12,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)
ax.legend()
ax.grid(True, linestyle="--", color="gray", linewidth=0.7, alpha=0.4)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
