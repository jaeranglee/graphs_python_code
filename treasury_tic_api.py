# %% [markdown]
# # Toreign US Treasury Holdings 데이터 가져오기
# ## TIC, table 5, foreign holdings
# requests, BeautifulSoup 이용
# 개인컴만 가능
# %%
#%config InlineBackend.close_figures = False
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

def download_tic_holdings_soup(file_path, force_update=False):
    # 파일이 없거나 강제로 업데이트할 때만 다운로드
    if not os.path.exists(file_path) or force_update:

        url = "https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table5.html"
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
        df0.to_excel(file_path, index=False, engine='openpyxl')
    else:
        print("Using cached file:", file_path)

    # 공통 부분
    return pd.ExcelFile(file_path, engine='openpyxl')

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
        df.to_excel(file_path, index=False, engine='openpyxl')
    else:
        print("Using cached file:", file_path)

    # 공통 부분
    return pd.ExcelFile(file_path, engine='openpyxl')

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
        df01.to_excel(file_path, index=False, engine='openpyxl')
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
#```
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
        df1.to_excel(file_path, index=False, engine='openpyxl')
    else:

        # 엑셀 파일로 저장
        print("Using cached file:", file_path)
    return pd.ExcelFile(file_path)


