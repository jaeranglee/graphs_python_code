# %% [markdown]
# # [그림 13] 정책금리 기대확률(2025년 9월 17일 FOMC)
#
# ## 이 코드가 하는 일
# CME FedWatch에서 내려받은 csv 파일(data/FedMeeting_20250917.csv)을 읽어,
# 2025년 9월 17일 FOMC 회의에서 정책금리가 어떻게 정해질지에 대한 시장의 예상 확률을 날짜별로 그린다.
#
# ## 그림이 다루는 내용
# FOMC는 미국 정책금리를 정하는 연준의 회의이다. CME FedWatch는 연방기금금리 선물 가격으로부터
# "다음 회의에서 금리를 얼마나 바꿀지"에 대한 확률을 계산해 보여준다.
# 50bp 인하(3.75~4.00%), 25bp 인하(4.00~4.25%), 동결(4.25~4.50%) 확률이 회의 날짜가 다가오며 어떻게 변했는지 본다.
# (1bp = 0.01%포인트)
#
# ## 자료를 얻는 방법
# CME는 무료 Open API를 제공하지 않는다. 아래 FedWatch 사이트의 historical 자료를 csv로 내려받아 data 폴더에 넣었다.
# https://www.cmegroup.com/ko/markets/interest-rates/cme-fedwatch-tool.html
#
# ## 결과물
# pic_jpg/f13_cme_rate_probability.jpg, pic_tif/f13_cme_rate_probability.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# %%
import matplotlib.dates as mdates

# 한글 폰트 설정
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

# 'data/FedMeeting_20250917.csv' CME에서 받은 파일의 경로와 이름을 넣어준다.
df_pro = pd.read_csv("data/FedMeeting_20250917.csv")
df_pro["Date"] = pd.to_datetime(df_pro["Date"])

# 현재 날짜 가져오기
access_date = df_pro["Date"].max().strftime("%Y-%m-%d")

# 시각화
fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)


ax.plot(
    df_pro["Date"],
    df_pro["(375-400)"] * 100,
    label="50bp 인하(3.75-4.00%)",
    ls="--",
    lw=2,
    color="black",
)
ax.plot(
    df_pro["Date"],
    df_pro["(400-425)"] * 100,
    label="25bp 인하(4.00-4.25%)",
    lw=2,
    color="blue",
)
ax.plot(
    df_pro["Date"],
    df_pro["(425-450)"] * 100,
    label="동결(4.25-4.5%)",
    lw=1,
    ls=":",
    color="blue",
)


ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

ax.text(
    0,
    1.00,
    "(%)",
    ha="left",
    va="bottom",
    transform=ax.transAxes,
    fontsize=12,
    color="black",
)
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1))

ax.text(0, -0.15, f"출처: CME FedWatch", transform=ax.transAxes, fontsize=10)
ax.grid(True, linestyle="--", color="gray", alpha=0.3)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

from plot_def import plot_save

plot_save()
