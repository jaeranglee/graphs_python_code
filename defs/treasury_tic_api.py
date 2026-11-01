# %% [markdown]
# # 미국 재무부 TIC: 외국인 미국 국채 보유·장기증권 순매수
# ## file name
# - treasury_tic_api.py
#
# ## 기능
# - TIC(Treasury International Capital) 웹페이지의 표를 긁어 엑셀 파일로 저장하고, 그 엑셀을 `pd.ExcelFile`로 돌려준다.
# - 파일이 이미 있으면 다시 받지 않는다 (`force_update=True`면 다시 받음).
# - `_soup`판은 requests+BeautifulSoup, `_html`판은 `pd.read_html` (접속 환경에 따라 되는 쪽을 씀)
#
# ## 출처
# - Major Foreign Holders of Treasury Securities (SLT table 5): https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.html
# - Net U.S. Long-Term Securities Sales (SLT table 1): https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table1.html
# - API key 필요 없음
#
# ## download_tic_holdings_soup()
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from treasury_tic_api import *
#
# xls = download_tic_holdings_soup("data/tic_holdings.xlsx")                    # 있으면 그대로
# xls = download_tic_holdings_soup("data/tic_holdings.xlsx", force_update=True)  # 다시 받기
# df = xls.parse(xls.sheet_names[0])
#
# xls = download_tic_sales_soup("data/tic_sales.xlsx")
# ```
#
# ## parameters
# | Parameter      | Type   | Description                                      |
# |----------------|--------|--------------------------------------------------|
# | `file_path`    | `str`  | 저장·읽을 엑셀 파일 경로                          |
# | `force_update` | `bool` | True면 파일이 있어도 다시 받음 (기본 False)        |
# | `table_no`     | `int`  | (`download_tic_holdings_soup`) 받을 SLT 표 번호 (기본 3) |
#
# ## returned columns and values
# - `pd.ExcelFile`: 웹페이지 표를 시트로 저장한 엑셀. 국가별 보유액(십억 달러)·월별 순매수 표가 원본 모양 그대로 들어 있다.
#
# ## 함수
# | Function | Description |
# |----------|-------------|
# | `download_tic_holdings_soup(file_path, force_update=False, table_no=3)` | 외국인 국채 보유 (BeautifulSoup) |
# | `download_tic_holdings_html(file_path, force_update=False)` | 외국인 국채 보유 (`read_html`) |
# | `download_tic_sales_soup(file_path, force_update=False)` | 장기증권 순매수 (BeautifulSoup) |
# | `download_tic_sales_html(file_path, force_update=False)` | 장기증권 순매수 (`read_html`) |
#
# ## 사용하는 곳
# - `wallstreet/treasury_tic.py`, `wallstreet/f_foreign_holdings.py`, `graphs_python_code/f50_foreign_holdings.py`

# %% [markdown]
# # Toreign US Treasury Holdings 데이터 가져오기
# ## TIC, table 5, foreign holdings
# requests, BeautifulSoup 이용
# 개인컴만 가능
# %%
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup


def download_tic_holdings_soup(file_path, force_update=False, table_no=3):
    # 파일이 없거나 강제로 업데이트할 때만 다운로드
    if not os.path.exists(file_path) or force_update:

        url = f"https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table{table_no}.html"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the first table (you can customize this)
        table = soup.find("table")

        # Extract rows
        rows = []
        for row in table.find_all("tr"):
            cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
            rows.append(cols)

        # Convert to DataFrame
        df0 = pd.DataFrame(rows)
        df0 = df0[1:]
        # 엑셀 파일로 저장
        # Save to Excel
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df0.to_excel(file_path, index=False, engine="openpyxl")
    else:
        print("Using cached file:", file_path)

    # 공통 부분
    return pd.ExcelFile(file_path, engine="openpyxl")


# %% [markdown]
# ## TIC, table 5, foreign holdings
# read_html 이용
# 회사컴만 가능,
# 여러번 수행하면 시간이 걸리기 때문에 엑셀로 저장하여 반복 이용,
# 수동으로 excel로 저장해도 됨
# %%
def download_tic_holdings_html(file_path, force_update=False):
    # 파일이 없거나 강제로 업데이트할 때만 다운로드
    if not os.path.exists(file_path) or force_update:

        # 데이터가 있는 URL
        url = "https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.html"

        # HTML 테이블 읽기
        tables1 = pd.read_html(url)

        # 테이블 확인 (여러 개일 수 있으므로 첫 번째 테이블을 선택)
        df = tables1[0]
        # Save to Excel
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_excel(file_path, index=False, engine="openpyxl")
    else:
        print("Using cached file:", file_path)

    # 공통 부분
    return pd.ExcelFile(file_path, engine="openpyxl")


# %% [markdown]
# # TIC, table 1, Net US Long Term Securities Sales 데이터 가져오기
# ## TIC data fetch with beautiful soup
# %%
def download_tic_sales_soup(file_path, force_update=False):
    # 파일이 없거나 강제로 업데이트할 때만 다운로드
    if not os.path.exists(file_path) or force_update:
        url1 = "https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table1.html"

        response1 = requests.get(url1)
        response1.raise_for_status()  # 에러 체크
        soup1 = BeautifulSoup(response1.text, "html.parser")

        # Find the first table
        table1 = soup1.find("table")

        # Extract rows
        rows1 = []
        for row in table1.find_all("tr"):
            cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
            rows1.append(cols)

        # Convert to DataFrame
        df01 = pd.DataFrame(rows1)
        df01 = df01[1:]  # 첫 행 제거

        # Save to Excel
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df01.to_excel(file_path, index=False, engine="openpyxl")
        print("Data downloaded and saved to:", file_path)
    else:
        print("Using cached file:", file_path)

    # 공통 부분
    return pd.ExcelFile(file_path)


# %% [markdown]
# ## Net US Long Term Securities Sales, table 1 데이터 가져오기
# 미리 다운로드 받거나 read_html을 긁어와서 이용,
# 회사컴만 가능
# ## Example
# ```python
# 1) 파일 없으면 다운로드, 있으면 캐시 사용
# excel_data = download_tic_data(file_path1)
#
# 2) 무조건 업데이트하고 싶을 때
# excel_data = download_tic_data(file_path1, force_update=True)
# ```
# %%
def download_tic_sales_html(file_path, force_update=False):
    if not os.path.exists(file_path) or force_update:
        # 데이터가 있는 URL
        url1 = "https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table1.html"

        # HTML 테이블 읽기
        tables1 = pd.read_html(url1)

        # 테이블 확인 (여러 개일 수 있으므로 첫 번째 테이블을 선택)
        df1 = tables1[0]
        # Save to Excel
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df1.to_excel(file_path, index=False, engine="openpyxl")
    else:

        # 엑셀 파일로 저장
        print("Using cached file:", file_path)
    return pd.ExcelFile(file_path)
