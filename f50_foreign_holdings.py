# %% [markdown]
# # [그림 50] 국가별 미국채 보유액과 순매입액
#
# ## 이 코드가 하는 일
# 미국 재무부 TIC(국제자본 통계) 자료를 내려받아 나라별 미국 국채 보유액과 순매입액을 그린다.
#
# ## 그림이 다루는 내용
# 외국은 미국 국채의 큰 보유자이다. 일본, 영국, 중국이 얼마나 가지고 있는지,
# 그리고 최근에 사고 있는지(순매입) 팔고 있는지(순매도) 본다.
# - 왼쪽: 외국 전체(총액)와 그중 외국 정부·중앙은행(외국정부)의 보유액. 일본·영국·중국 보유액도 골라 두지만 그리지는 않는다.
# - 오른쪽: 2021년 3월 이후 일본·영국·중국과 외국 전체의 순매입액
#
# ## 결과물
# pic_jpg/f50_foreign_holdings.jpg, pic_tif/f50_foreign_holdings.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - treasury_tic_api.py: TIC 자료를 내려받는 함수
#
# ## 자료 받기
# - download_tic_holdings_soup(): 나라별 보유액 표를 data/f_foreign_holdings1.xlsx로 받는다(이미 있으면 다시 받지 않는다).
# - download_tic_sales_soup(): 나라별 순매입액 표를 data/TIC_data.xlsx로 받는다.
# - 엑셀 표의 위쪽 설명 줄을 건너뛰고(skiprows) 필요한 나라만 골라낸다.
# %%
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates


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

from treasury_tic_api import download_tic_holdings_soup

# 한글 폰트 설정
from plot_def import *

set_fonts()


##---------------------------------------------
## Foreign US Treasury Holdings 데이터 가져오기
## requests, BeautifulSoup 이용
##
##---------------------------------------------


# Load the Excel file
file_path = "data/f_foreign_holdings1.xlsx"

# treasury_tic_api.py file function
excel_data = download_tic_holdings_soup(
    file_path=file_path, force_update=False, table_no=5
)
df = excel_data.parse("Sheet1", skiprows=5)

# Filter for both target rows
target_countries = [
    "Grand Total",
    "Of Which: Foreign Official",
    "Japan",
    "United Kingdom",
    "China, Mainland",
]
target_rows = df[df["Country"].isin(target_countries)]
target_rows = target_rows.set_index("Country")

reshaped = target_rows.transpose()
reshaped.index.name = "Date"
reshaped = reshaped.reset_index()

reshaped.iloc[:, 1:] = reshaped.iloc[:, 1:].apply(pd.to_numeric)

# Convert date strings to datetime
reshaped["Date"] = pd.to_datetime(reshaped["Date"], format="%Y-%m")

# Custom labels for Korean legend
label_map1 = {"Grand Total": "총액", "Of Which: Foreign Official": "외국정부"}
color_map = {"Grand Total": "black", "Of Which: Foreign Official": "blue"}

##---------------------------------------------
## Net US Long Term Securities Sales 데이터 가져오기
## Beautiful Soup 이용
##
##---------------------------------------------
## treasury_tic_api.py file function

file_path1 = "data/TIC_data.xlsx"
from treasury_tic_api import *

excel_data = download_tic_sales_soup(file_path=file_path1, force_update=False)

# Properly parse the data
df1 = excel_data.parse("Sheet1", skiprows=7)
df1 = df1.iloc[1:, 0:9]

# Clean up columns
df1["Country"] = df1["Country"].str.strip()

# Filter target countries
target_countries = ["Japan", "United Kingdom", "China, Mainland", "Grand Total"]
filtered_df = df1[df1["Country"].isin(target_countries)].copy()

# Convert types
filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])

# Filter from March 2024 onward
filtered_df = filtered_df[filtered_df["Date"] >= "2021-03-01"]
filtered_df["Net U.S. Sales.1"] = pd.to_numeric(
    filtered_df["Net U.S. Sales.1"], errors="coerce"
)

# Change millions to billions

filtered_df["Net U.S. Sales.1"] = filtered_df["Net U.S. Sales.1"] / 1000

# Pivot for plotting
pivot_df = filtered_df.pivot(index="Date", columns="Country", values="Net U.S. Sales.1")
pivot_df = pivot_df.interpolate().dropna()

# Custom labels for Korean legend
label_map = {
    "Grand Total": "총액",
    "Of Which: Foreign Official": "외국정부",
    "China, Mainland": "중국",
    "Japan": "일본",
    "United Kingdom": "영국",
}

colors_map = {
    "Grand Total": "black",
    "Of Which: Foreign Official": "gray",
    "China, Mainland": "blue",
    "Japan": "blue",
    "United Kingdom": "blue",
}

ls_map = {
    "Grand Total": "-",
    "Of Which: Foreign Official": "--",
    "China, Mainland": "-",
    "Japan": "-",
    "United Kingdom": ":",
}
colors = [
    "lightblue",  # medium blue
    "gray",  # light gray
]

# Plotting Foreign US Treasuries Holds (왼쪽그림), Net US sales(오른쪽)
fig, ax = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)

# Plotting Foreign US Treasuries Holds (왼쪽그림)
ax[0].fill_between(
    reshaped["Date"], reshaped[reshaped.columns[-2]] / 1000, alpha=0.8, color=colors[0]
)
ax[0].fill_between(
    reshaped["Date"], reshaped[reshaped.columns[-1]] / 1000, alpha=0.8, color=colors[1]
)
for column in reshaped.columns[-2:]:  # Skip 'Date'  # '총액', '외국정부' 포함
    ax[0].set_ylim([3, 10])
    ax[0].plot(
        reshaped["Date"],
        reshaped[column] / 1000,
        label=label_map.get(column, column),
        color=color_map.get(column, column),
        lw=2,
    )


ax[0].text(
    0,
    1.00,
    "(조 달러, 월말기준)",
    ha="left",
    va="bottom",
    color="blue",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax[0].text(
    0.0,
    -0.15,
    "출처: 미국 재무부 Treasury International Capital (TIC) System",
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
    transform=ax[0].transAxes,
)

ax[0].legend(loc="upper left", bbox_to_anchor=(0.15, 1))

# Plotting Net US sales(오른쪽)
for country in target_countries:
    lw = 3 if country == "China, Mainland" else 1.5  # thicker line for China
    ax[1].plot(
        pivot_df.index,
        pivot_df[country],
        label=label_map.get(country, country),
        lw=lw,
        color=colors_map.get(country, country),
        ls=ls_map.get(country, country),
    )

    # Add horizontal line at y = 0
    ax[1].axhline(y=0, color="gray", linestyle="--", linewidth=1)


ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax[1].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

ax[1].text(
    0,
    1.00,
    "(십억 달러, 매월기준)",
    ha="left",
    va="bottom",
    color="blue",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)
ax[1].legend(loc="upper left", bbox_to_anchor=(0.5, 0.95))

# save plot file and show on screen

plot_save()
