# %% [markdown]
# # [그림 31] 주요 국채 보유주체
# ## 같은 디렉토리에 필요한 file
#   - plot_def.py : 한글폰트 추가, 그래프 저장
#   - fred_api.py
# ## data 디렉토리에 필요한 파일
#   - Treasury Fiscal Data에서 받아놓은 json file
#       - data/MSPD_SumSecty_20010131_20250731.json
#   - 각자 직접 홈페이지에서 다운로드하기를 추천
#   - api fetch 시간이 너무 오래 걸림
# %%
import pandas as pd
import matplotlib.pyplot as plt

# Set font depending on the platform
from plot_def import *
set_fonts()

# %% [markdown]
# ## Fetch data from FRED
# - Households and Nonprofit Organizations; Treasury Securities; Asset, Level (HNOTSAQ027S)
#   - in Million dollars
# Households and Nonprofit Organizations; Treasury Securities; Asset, Market Value Levels (BOGZ1LM153061105Q)
# in Million dollars

# Pension Funds; Treasury Securities; Asset, Level (BOGZ1FL593061105Q)
# in Million dollars

# Rest of the World; Treasury Securities Held by Foreign Official Institutions; Asset, Level (BOGZ1FL263061130Q)
# in Million dollars

# Rest of the World; Treasury Securities; Asset, Level (ROWTSEQ027S)
# in Million dollars

# Rest of the World; Treasury Securities; Asset, Market Value Levels (BOGZ1LM263061105Q)
# in Million dollars

# Insurance Companies; Treasury Securities; Asset, Level (BOGZ1FL523061105Q)
# in Million dollars

# Money Market Funds; Treasury Securities; Asset, Level (BOGZ1FL633061105Q)
# in Million dollars

# Mutual Funds; Treasury Securities; Asset (Market Value), Level (BOGZ1FL653061105Q)
# in Million dollars

# Domestic Financial Sectors; Treasury Securities; Asset, Level (FBTSAAQ027S)
# in Million dollars

# Nonfinancial Corporate Business; Treasury Securities; Asset, Level (TSABSNNCB)
# in Billion dollars
start = "1990-01-01"
end = "2025-09-01"


# FRED 상의 시리즈 ID (Constant Maturity Treasury Rates)
series_ids = {
    "외국전체": "ROWTSEQ027S",
    "가계와 비영리단체": "HNOTSAQ027S",
    "MMF": "BOGZ1FL633061105Q",
    "연금": "BOGZ1FL593061105Q",
    "보험": "BOGZ1FL523061105Q"

#    "뮤추얼펀드": "BOGZ1FL653061105Q"
#    "금융기관": "FBTSAAQ027S"
}

color_map = {
    "외국전체": "black",
    "가계와 비영리단체": "blue",
    "MMF": "black",
    "연금": "blue",
    "보험": "gray"
}

lw_map = {
    "외국전체": 2,
    "가계와 비영리단체": 2,
    "MMF": 2,
    "연금": 1,
    "보험": 1
}

# plot style combos
ls_map = {
    "외국전체": "-",
    "가계와 비영리단체": "--",
    "MMF": ':',
    "연금": '-.',
    "보험": '-'
}

from fred_api import fetch_fred_series


# 모든 만기 데이터 가져오기
all_data = {}
for term, sid in series_ids.items():
    df = fetch_fred_series(sid,start_date=start, end_date=end)

    df.rename(columns={df.columns[-1]: "value"}, inplace=True)
    all_data[term] = df.set_index("observation_date")["value"]

# 병합
# 백만을 조 단위로 변환
df_all = pd.DataFrame(all_data)/1e6


print(df_all)

# 2020년 이후 데이터 필터링
df_filtered = df_all[df_all.index >= '1990-01-01']


# 그래프 그리기

fig, ax = plt.subplots(figsize=(8, 4.5),constrained_layout=True)

# 모든 컬럼을 line plot (zip 이용)
for col, series in zip(df_filtered.columns, df_filtered.T.values):
    ax.plot(df_filtered.index, series, label=col,
            color=color_map.get(col),
            lw=lw_map.get(col),
            ls=ls_map.get(col))


ax.text(0, 1.00, '(조 달러)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)

#plt.legend()
ax.text(0.0, -0.15, "출처: FRED, 자금순환표", transform=ax.transAxes,
         fontsize=12, verticalalignment='bottom', horizontalalignment='left', color='black')
ax.legend()
ax.grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.4)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()