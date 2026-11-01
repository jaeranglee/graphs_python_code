# %% [markdown]
# # [그림 35] 연준의 총자산 규모
#
# ## 이 코드가 하는 일
# FRED에서 연준의 총자산과 국채·MBS 보유액을 받아, 세 부분으로 나눠 쌓은 면적 그래프를 그린다.
#
# ## 그림이 다루는 내용
# 연준은 국채와 MBS(주택담보대출을 묶어 만든 채권)를 사서 시중에 돈을 푼다(양적완화).
# 코로나 때 총자산이 4조 달러대에서 9조 달러 가까이 늘었고, 2022년부터는 보유 채권을 줄이고 있다(양적긴축).
#
# ## 결과물
# pic_jpg/f35_fedasset.jpg, pic_tif/f35_fedasset.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장, FRED 자료 받기(fetch_fred_series)
# - fred_api.py: fetch_fred_series가 실제로 들어 있는 파일(plot_def.py가 대신 불러온다)
# %%
import matplotlib.ticker as ticker

# import matplotlib.dates as mdates

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

# api를 이용해 FRED 자료를 호출하기 위한 루틴

start = "2018-01-01"
end = "2025-12-31"

# %% [markdown]
# ## 자료 받기 (FRED, 매주 수요일 기준, 백만 달러)
# - 연준 총자산 (RESPPANWW), 국채 보유액 (WSHOTSL), MBS 보유액 (WSHOMCB)
# ## 자료 가공
# - 모두 1e6으로 나눠 조 달러로 바꾼다.
# - 기타 = 총자산 - (국채 + MBS)
# - 국채, MBS, 기타를 차례로 쌓아 면적 그래프로 그린다. 맨 위 경계가 총자산이 된다.
# %%
df0 = fetch_fred_series("RESPPANWW", start_date=start, end_date=end)
df1 = fetch_fred_series("WSHOTSL", start_date=start, end_date=end)
df2 = fetch_fred_series("WSHOMCB", start_date=start, end_date=end)

df_filtered = pd.merge(df0, df1, on="observation_date")
df_filtered = pd.merge(df_filtered, df2, on="observation_date").copy()

df_filtered["RESPPANWW"] = (
    pd.to_numeric(df_filtered["RESPPANWW"], errors="coerce") / 1e6
)
df_filtered["WSHOTSL"] = pd.to_numeric(df_filtered["WSHOTSL"], errors="coerce") / 1e6
df_filtered["WSHOMCB"] = pd.to_numeric(df_filtered["WSHOMCB"], errors="coerce") / 1e6


# df_filtered['WSHOMCB'] = pd.to_numeric(df_filtered['WSHOMCB'], errors='coerce') / 1e6 + df_filtered['WSHOTSL']
df_filtered["Other"] = df_filtered["RESPPANWW"] - (
    df_filtered["WSHOMCB"] + df_filtered["WSHOTSL"]
)


# Custom labels for Korean legend
label_map = {
    #    'RESPPANWW': '총자산',
    "WSHOTSL": "미국채",
    "WSHOMCB": "모기지증권",
    "Other": "기타",
}


df_all = df_filtered[label_map.keys()].copy()

df_all = df_all.rename(columns=label_map)

# 날짜를 datetime으로 변환하고 인덱스로 설정
df_filtered["observation_date"] = pd.to_datetime(df_filtered["observation_date"])
df_filtered = df_filtered.set_index("observation_date")

df_all.index = pd.to_datetime(df_all.index)
df_filtered.index = pd.to_datetime(df_filtered.index)


# 날짜 인덱스를 df_all에도 적용
df_all.index = df_filtered.index


# Plot
fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)

# 색상 정의 (df_all 컬럼 수에 맞춰)
# colors = ['#003f5c', 'lightblue', '#a5a5a5'][:len(df_all.columns)]

"""
colors = [
    '#003f5c',  # deep blue
    'lightblue',  # medium blue
    '#a5a5a5',  # light gray
    'gray'
    '#000000',  # black
]
"""

# 색상 정의 (df_all 컬럼 수에 맞춰)
colors = ["#003f5c", "lightblue", "#a5a5a5"][: len(df_all.columns)]
# df_all.plot.area(ax=ax, stacked=True, alpha=0.6, color=colors[:df_all.shape[1]])

df_all.plot.area(ax=ax, stacked=True, alpha=0.6, color=colors)
# ax.plot(df_filtered.index, df_filtered['RESPPANWW'], label='총자산', lw=2.5, color='black', zorder=10)

ax.set_xlabel("")

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

# Turn off scientific notation on y-axis
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))


ax.grid(False)
ax.legend()

ax.text(
    0.0,
    -0.15,
    "출처: Federal Reserve Bank of St. Louis",
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
# Last executed at: 2025-09-20 23:03:26
