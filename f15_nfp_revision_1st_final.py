# %% [markdown]
# # [그림 15] NFP 고용 수정 전후비교
#
# ## 이 코드가 하는 일
# NFP 처음 발표치(csv 파일)와 최종 수정치, ADP 고용(FRED)을 한 그림에 겹쳐 그린다.
#
# ## 그림이 다루는 내용
# NFP는 처음 발표된 뒤 다음 두 달 동안 두 번 수정되고, 해마다 한 번 더 크게 수정된다.
# 처음 발표치만 보고 판단하면 실제 고용 흐름을 잘못 읽을 수 있다.
# 처음 발표치(1st NFP)와 최종치(final NFP)가 얼마나 다른지, 그리고 ADP와는 어떻게 다른지 비교한다.
#
# ## 결과물
# pic_jpg/f15_nfp_revision_1st_final.jpg, pic_tif/f15_nfp_revision_1st_final.tif
#
# ## 필요한 파일
# - plot_def.py (defs): 한글 폰트 설정, 그림 저장
# - fred_api.py (defs): FRED 자료 받기
# - nfp_revision.py (이 폴더): NFP 발표 시점별 값을 받아 수정 내역을 csv로 저장하는 코드
# - data/nfp_revisions.csv: 위 코드가 만든 파일. 달마다 첫 발표치(1st)와 수정치(2nd, 3rd)가 들어 있다.
# %%
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
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

from plot_def import set_fonts

set_fonts()

# Load the data from the CSV file
df = pd.read_csv("data/nfp_revisions.csv", index_col="month", parse_dates=True)

# Apply the conditional logic to create a new column with the value to plot
df["plot_value"] = np.where(
    df["vintage_completeness"] == "3 vintage(s)",  # Condition 1
    df["3rd - 1st"],  # Value if Condition 1 is true
    np.where(
        df["vintage_completeness"] == "2 vintage(s)",  # Condition 2
        df["2nd - 1st"],  # Value if Condition 2 is true
        np.nan,  # Value if neither condition is true
    ),
)

# Filter out rows that don't have a value to plot
plot_data = df.dropna(subset=["plot_value"])

df = df.reset_index()

start = "2022-07-01"
end = "2025-12-31"

df = df[df["month"] >= start].copy()

# %% [markdown]
# ## 자료 받기 (FRED)
# - 최종 NFP: 비농업 전체 고용자 수 (PAYEMS), 천 명, 계절조정, 월별
# - ADP: 민간 비농업 고용자 수 (ADPMNUSNERSA), 명, 계절조정, 월별
# - 두 자료 모두 전월 대비 증감으로 바꿔, csv의 첫 발표치와 같은 단위(천 명)로 맞춘다.
# %%
from fred_api import fetch_fred_series

series_ids = {"NFP": "PAYEMS", "ADP": "ADPMNUSNERSA"}

# 데이터 가져오기
# 이름을 Fred series_id를 일반 명칭으로 변환

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

# Identify the specific date
highlight_date = "2023-09-01"
highlight_date2 = "2025-06-01"

print(df_all[df_all.index == highlight_date])
print(df_all[df_all.index == highlight_date2])

# Convert date format to match DataFrame
highlight_date = pd.to_datetime(highlight_date)
highlight_date2 = pd.to_datetime(highlight_date2)

# Find the corresponding data point
highlight_1st_point = df[df["month"] == highlight_date]
highlight_final_point = df_all[df_all.index == highlight_date]

highlight_1st_point2 = df[df["month"] == highlight_date2]
highlight_final_point2 = df_all[df_all.index == highlight_date2]

# 월별 고용 최초 발표, 최종발표, ADP 그래프

fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)


# 최초 발표 NFP
ax.plot(df["month"], df["1st"], color="blue", lw=2, label="1st NFP")
ax.scatter(
    highlight_1st_point["month"],
    highlight_1st_point["1st"],
    color="blue",
    marker="o",
    s=100,
    linewidth=2,
    label=None,
)
ax.scatter(
    highlight_1st_point2["month"],
    highlight_1st_point2["1st"],
    color="blue",
    marker="o",
    s=100,
    linewidth=2,
    label=None,
)

# 최종 NFP
ax.plot(df_all.index, df_all["NFP"], color="black", lw=2, label="final NFP")
ax.scatter(
    highlight_final_point.index,
    highlight_final_point["NFP"],
    color="black",
    marker="o",
    s=100,
    linewidth=2,
    label=None,
)
ax.scatter(
    highlight_final_point2.index,
    highlight_final_point2["NFP"],
    color="black",
    marker="o",
    s=100,
    linewidth=2,
    label=None,
)


# ADP
ax.plot(df_all.index, df_all["ADP"], color="blue", lw=1, ls="--", label="ADP")

ax.set_ylim(-60, 600)

ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # 5년마다 큰 눈금
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))  # '2024' 형식으로 표시

ax.legend(loc="upper left", bbox_to_anchor=(0.3, 1.0), fontsize=12)

# Add a grid
ax.grid(True, which="major", linestyle="--", linewidth="0.5", color="grey", alpha=0.3)

# 단위와 출처 표시
ax.text(
    0,
    1.00,
    "(천명)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)
# ax.set_title("NFP Revisions", size=16)
ax.text(
    0.0,
    -0.15,
    "출처: BLS, ALFRED, FRED",
    fontsize=12,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
    transform=ax.transAxes,
)


# 그림파일 저장 및 화면 출력

from plot_def import plot_save

plot_save()
