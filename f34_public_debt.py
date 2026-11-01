# %% [markdown]
# # [그림 34] 연방정부 부채한도와 총부채
#
# ## 이 코드가 하는 일
# 재무부 일일 재정보고서(DTS)의 부채한도 표를 읽어, 법정 부채한도와 실제 총부채를 함께 그린다.
#
# ## 그림이 다루는 내용
# 미국은 의회가 정부가 빌릴 수 있는 돈의 상한(부채한도)을 법으로 정한다.
# 총부채가 한도에 닿으면 정부는 새로 돈을 빌릴 수 없어 총부채 선이 한도에 붙어 평평해진다.
# 의회가 한도를 올리거나 적용을 잠시 멈추면 총부채가 다시 늘어난다.
#
# ## 결과물
# pic_jpg/f34_public_debt.jpg, pic_tif/f34_public_debt.tif
#
# ## 필요한 파일
# - plot_def.py (defs): 한글 폰트 설정, 그림 저장
# - treasury_debt_limit_api.py (defs): 부채한도 자료를 읽는 함수(fetch_debt_limit_json 등)
# - data/DTS_DebtSubjLim_20051003_20250902.json: Treasury Fiscal Data의 DTS, Debt Subject to Limit 표를 미리 내려받은 파일
#
# ## 자료 가공
# - 총부채 = 민간 보유 국채(Debt Held by the Public) + 정부 기관 보유 국채(Intragovernmental Holdings)
# - 법정 부채한도(Statutory Debt Limit)와 날짜 기준으로 합친 뒤 1e6으로 나눠 조 달러로 그린다.
# - API로 바로 받는 fetch_debt_limit()와 csv를 읽는 fetch_debt_limit_csv()도 코드에 문자열로 막아 두었다.
#   API는 최신 자료를 받지만 시간이 오래 걸린다.
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
# 정부부채
# cvs 파일로 저장했을 때 불러오는 루틴

"""
start = '2021-01-01'
end = '2025-12-31'
file_path = "data/f_DTS_DebtSubjLim_20051003_20250703.csv"

from treasury_debt_limit_api import fetch_debt_limit_csv

df=fetch_debt_limit_csv(start_date=start, end_date=end, file_path=file_path)
"""


# 사용자 정의 기간으로 호출
start = "2021-01-01"
end = "2025-12-31"

# Treasury Fiscal Data, DTS, Debt Subject to Limit Table 에서 미리 다운로드한 파일 사용
base_url = "data/DTS_DebtSubjLim_20051003_20250902.json"
# Fetch debt limit data form pre download jason file stored at data\ directory
# use json format.
# use pre defined def at treasury_debt_limit_api.py
# def fetch_debt_limit_jason(start_data=start, end_date=end)

from treasury_debt_limit_api import fetch_debt_limit_json

df = fetch_debt_limit_json(start_date=start, end_date=end, base_url=base_url)


# Fetch debt limit data from https://fiscaldata.treasury.gov/datasets/daily-treasury-statement/debt-subject-to-limit
# def is stored in the file treasury_debt_limit_api.py
# It is good to fetch the most recent data, but takes to time to fetch.
# to save time it is good to save json file from the web page and use
# the above def

"""
from treasury_debt_limit_api import fetch_debt_limit


df = fetch_debt_limit(start_date = start, end_date = end)
"""

# 총 부채 계산을 위한 항목 선택
public_debt = df[df["Debt Category"] == "Debt Held by the Public"]
intragov_debt = df[df["Debt Category"] == "Intragovernmental Holdings"]

# 두 항목 병합 후 총 부채 계산
total_debt = pd.merge(
    public_debt[["Record Date", "Closing Balance Today"]],
    intragov_debt[["Record Date", "Closing Balance Today"]],
    on="Record Date",
    suffixes=("_public", "_intragov"),
)
total_debt["Total Debt"] = (
    total_debt["Closing Balance Today_public"]
    + total_debt["Closing Balance Today_intragov"]
)

# 법정 부채한도 항목만 필터링 후 열 이름 바꾸기
limit_debt = df[df["Debt Category"] == "Statutory Debt Limit"].copy()


# 총 부채와 법정한도 병합
merged = pd.merge(
    total_debt[["Record Date", "Total Debt"]],
    limit_debt[["Record Date", "Closing Balance Today"]],
    on="Record Date",
    #    how=""
)


# 단위: 백만 달러로 변환
merged["Total Debt"] /= 1e6
merged["Closing Balance Today"] /= 1e6

# 시각화

fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)

ax.plot(
    merged["Record Date"],
    merged["Total Debt"],
    label="총부채",
    linewidth=2,
    color="blue",
)
ax.plot(
    merged["Record Date"],
    merged["Closing Balance Today"],
    label="법정 부채한도",
    linestyle="--",
    linewidth=2,
    color="black",
)

ax.set_ylim(28, 43)
# ax.set_ylim(20, 43)


# 단위
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


# 제목 및 레이아웃
ax.text(
    0.0,
    -0.15,
    "출처: Daily Treasury Statement, U.S. Department of Treasury",
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)

plt.grid(True, linestyle="--", color="gray", linewidth=0.7, alpha=0.7)
ax.legend()

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
