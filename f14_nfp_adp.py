# %% [markdown]
# # [그림 14] 월별 구인건수와 고용 증감
#
# ## 이 코드가 하는 일
# FRED에서 고용 관련 자료 세 개를 받아 막대그래프 세 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# - 구인건수(JOLTS): 기업이 사람을 뽑으려고 낸 일자리 수. 노동 수요를 보여준다.
# - ADP 고용: 민간 급여처리 회사 ADP가 집계한 민간 일자리 증감. 정부 발표보다 이틀 먼저 나온다.
# - NFP(비농업 고용): 미국 노동부가 매달 발표하는 일자리 증감. 시장이 가장 주목하는 고용 지표이다.
# 책 본문에서 다룬 달(구인건수 2023년 8월, ADP·NFP 2023년 9월)을 다른 색으로 강조한다.
#
# ## 결과물
# pic_jpg/f14_nfp_adp.jpg, pic_tif/f14_nfp_adp.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
# %%
import pandas as pd

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

from fred_api import fetch_fred_series

start = "2022-07-01"
end = "2025-10-01"

# %% [markdown]
# ## 자료 받기 (FRED)
# - NFP: 비농업 전체 고용자 수 (PAYEMS), 천 명, 계절조정, 월별
# - ADP: 민간 비농업 고용자 수 (ADPMNUSNERSA), 명, 계절조정, 월별. 1000으로 나눠 천 명 단위로 맞춘다.
# - 구인건수 (JTSJOL), 천 건
#
# ## 자료 가공
# 1. 세 자료를 반복문(for)으로 차례로 받아 월별 평균으로 맞추고 날짜를 매달 1일로 통일한다.
# 2. 하나의 dataframe(df_all)으로 합친다.
# 3. NFP와 ADP는 고용자 '수'이므로 diff()로 전월 대비 증감을 구한다.
#
# ## 그리기
# 왼쪽부터 구인건수, ADP 증감, NFP 증감을 막대로 그린다.
# 구인건수는 2023년 8월을 파란색으로, ADP와 NFP는 2023년 9월을 속이 빈 막대로 강조한다.
# %%


series_ids = {"NFP": "PAYEMS", "ADP": "ADPMNUSNERSA", "Job Openings": "JTSJOL"}

# 데이터 가져오기
# Fred series_id를 일반 명칭으로 변환

all_data = {}
for term, sid in series_ids.items():
    df_temp = fetch_fred_series(sid, start_date=start, end_date=end)
    df_temp = df_temp.rename(columns={df_temp.columns[-1]: "value"})

    # Series로 변환
    s = df_temp.set_index("observation_date")["value"]

    # Weekly or Daily to Monthly
    s = s.resample("ME").mean()
    s.index = s.index.to_period("M").to_timestamp(how="start")  # 월초로 통일

    all_data[term] = s

# 병합
df_all = pd.DataFrame(all_data)

series_names = list(series_ids.keys())

# ADP 취업자수 천명 단위로 전환
df_all[series_names[1]] = df_all[series_names[1]] / 1000

# NFP, ADP를 전월 대비 증감으로 변환
for s in series_names[:2]:
    df_all[s] = df_all[s].diff(periods=1).copy()

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# 한글 폰트 설정
from plot_def import set_fonts

set_fonts()

colors = ["gray", "blue"]

# 강조할 달
nfp_highlight_month = "2023-09"
nfp_highlight_month = pd.to_datetime(nfp_highlight_month)

jolt_highlight_month = "2023-08"
jolt_highlight_month = pd.to_datetime(jolt_highlight_month)


# NFP 색상 지정 (9월만 red)
colors_nfp = [
    "none" if d.month == 9 and d.year == nfp_highlight_month.year else colors[1]
    for d in df_all.index
]
edge_nfp = [
    "black" if d.month == 9 and d.year == nfp_highlight_month.year else "none"
    for d in df_all.index
]
# ADP 색상 지정 (9월만 red)
colors_adp = [
    "none" if d.month == 9 and d.year == nfp_highlight_month.year else colors[1]
    for d in df_all.index
]
edge_adp = [
    "black" if d.month == 9 and d.year == nfp_highlight_month.year else "none"
    for d in df_all.index
]

# JOLT 색상 지정 (8월만 파란색, 나머지는 red)
colors_jolt = [
    "blue" if d.month == 8 and d.year == jolt_highlight_month.year else colors[0]
    for d in df_all.index
]


# plot 정의

fig, ax = plt.subplots(1, 3, figsize=(8, 4.5), constrained_layout=True)

# x축
x = df_all.index

# plot
# ---- JOLT 건수

ax[0].bar(
    df_all.index,
    df_all[series_names[2]],
    width=20,
    label=series_names[2],
    color=colors_jolt,
)

# ---- ADP 전월대비 증감

ax[1].bar(
    x,
    df_all[series_names[1]],
    width=20,
    label=series_names[1],
    color=colors_adp,
    edgecolor=edge_adp,
)

# ---- NFP 전월대비 증감
ax[2].bar(
    x,
    df_all[series_names[0]],
    width=20,
    label=series_names[0],
    color=colors_nfp,
    edgecolor=edge_nfp,
)


for i in [0, 1, 2]:
    ax[i].xaxis_date()
    ax[i].xaxis.set_major_locator(mdates.YearLocator())
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    # 단위 표시 및 출처
    ax[i].legend(loc="upper left", bbox_to_anchor=(0.3, 1.0))
    ax[i].yaxis.label.set_visible(True)
    ax[i].text(
        0,
        1.00,
        "(천명)",
        ha="left",
        va="bottom",
        color="black",
        fontsize=12,
        rotation=0,
        transform=ax[i].transAxes,
    )

ax[0].text(
    0.0,
    -0.15,
    "출처: FRED, 파란색은 2023년 8월",
    transform=ax[0].transAxes,
    fontsize=10,
    ha="left",
)
ax[1].text(
    0.0, -0.15, "회색은 2023년 9월", transform=ax[1].transAxes, fontsize=10, ha="left"
)
ax[2].text(
    0.0, -0.15, "회색은 2023년 8월", transform=ax[2].transAxes, fontsize=10, ha="left"
)

# 그림 파일로 저장

from plot_def import plot_save

plot_save()
