# %% [markdown]
# # Fetch from ECOS
#   - BOK Ecos OPEN API 에서 데이터 가져오는 루틴
#   - 다른 곳에서 호출하는 법
# # 아래와 같이 호출
# ```pythoon# 이 파일을 호출
# import fetch_ecos_series from bok_ecos_api
#
# # 원하는 항목을 지정
# # 아래는 항목명, 항목코드, 세부항목코드, 주기
# # Ecos API 홈페이지에서 확인 후 직접 추가해야 함
#
# series_list = [
#     ["CPI", "901Y009", "0", "M"],
#     ["Gold", "902Y003", "040101", "M"],  # hypothetical daily gold data
# ]
#
# # 추출하고자 하는 항목의 시계열 시작, 종료 지정
# # 월별 자료는 202501 형식
#
# start_date = "200001"
# end_date = "202512"
#
#
# dfs = {}
# for name, stat_code, item_code, cycle in series_list:
#     dfs[name] = fetch_ecos_series(name, stat_code, item_code, cycle, start_date, end_date, API_KEY_ECOS)
#
#
# # 중복 검증
#
# for name in dfs:
#     dfs[name] = dfs[name].drop_duplicates(subset='Date').reset_index(drop=True)
#
# for name, df in dfs.items():
#     dup_count = df.duplicated().sum()
#     print(f"{name}: {dup_count} duplicates")
# ```
# ## EOS_API_KEY: 'ECOS 가입후 발급 받은 api key를 따옴표 안에 기입'
#   - 옵션으로 .env 파일에 기록하는 방법도 있음. .env 파일을 같은 디렉토리에 넣어 놓아야 함.
# %%
#%config InlineBackend.close_figures = False
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dotenv import load_dotenv
import os
import requests
import pandas as pd

# 🔑 Load API key
load_dotenv()
#API_KEY_ECOS = os.getenv("ECOS_API_KEY")
API_KEY_ECOS = "HP80FXOW6VNZ6PP270RZ"

# %% [markdown]
# ## ECOS date 형식대신 "%Y-%m-%d" 형식으로 입력할 수 있는 루틴
# %%
def convert_date_format(date_str, cycle):
    dt = datetime.strptime(date_str, "%Y-%m-%d")

    if cycle == "D":
        return dt.strftime("%Y%m%d")
    elif cycle == "M":
        return dt.strftime("%Y%m")
    elif cycle == "Q":
        quarter = (dt.month - 1) // 3 + 1
        return f"{dt.year}Q{quarter}"
    elif cycle == "Y":
        return str(dt.year)
    else:
        raise ValueError("Unsupported cycle type. Use 'D', 'M', 'Q', or 'Y'.")


def calculate_length(start_date, end_date, cycle):
    start = datetime.strptime(start_date, "%Y-%m-%d" if cycle in ['M', 'Q', 'Y'] else "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d" if cycle in ['M', 'Q', 'Y'] else "%Y-%m-%d")

    if cycle == "D":
        diff = (end - start).days + 1
    elif cycle == "M":
        diff = (end.year - start.year) * 12 + end.month - start.month + 1
    elif cycle == "Q":
        diff = ((end.year - start.year) * 12 + end.month - start.month) // 3 + 1
    elif cycle == "Y":
        diff = end.year - start.year + 1
    else:
        raise ValueError("Unsupported cycle type. Use 'D', 'M', 'Q', or 'Y'.")
    return diff
# %% [markdown]
# ## item 코드를 3개까지 입력하여야 할 경우 사용하는 def (필요시 활성화하여 사용)
# ```python
# def fetch_ecos_series(stat_name, stat_code, item_code, item_code2, item_code3, cycle,
#                       start_date, end_date,
#                       cache_dir="ecos_cache", use_cache=False):
#
#     os.makedirs(cache_dir, exist_ok=True)
#
#     # Convert dates
#     start_fmt = convert_date_format(start_date, cycle)
#     end_fmt = convert_date_format(end_date, cycle)
#
#     ## item_code2가 없으면 "0"으로 처리
#     #item_code2 = item_code2 if item_code2 is not None else "?"
#     #item_code3 = item_code3 if item_code2 is not None else "?"
#     cache_path = os.path.join(
#         cache_dir,
#         f"{stat_name}_{start_fmt}_{end_fmt}_{item_code}_{item_code2}_{item_code3}_{cycle}.csv"
#     )
#
#     if use_cache and os.path.exists(cache_path):
#         print(f"📥 Loaded from cache: {stat_name}")
#         return pd.read_csv(cache_path, parse_dates=["Date"])
#
#     length = calculate_length(start_date, end_date, cycle)
#     # 기본 URL
#     # item_code2, item_code3가 None일 경우 URL 단축
#     url = [
#         f"http://ecos.bok.or.kr/api/StatisticSearch/{API_KEY_ECOS}/xml/kr/1/{length}",
#         stat_code, cycle, start_fmt, end_fmt, item_code
#     ]
#
#     if item_code2:  # 있을 때만 추가
#         url.append(item_code2)
#     if item_code3:  # 있을 때만 추가
#         url.append(item_code3)
#
#     url = "/".join(url)
#
#     print("🔗 URL:", url)
#
#     response = requests.get(url)
#     print(response.text)
#     if response.status_code != 200:
#         print("❌ HTTP error:", response.status_code)
#         return pd.DataFrame()
#
#     root = ET.fromstring(response.content)
#     rows = root.findall(".//row")
#
#     if not rows:
#         print(f"❌ No data found for {stat_name} - item_code: {item_code}, item_code2: {item_code2}, item_code3: {item_code3}")
#         return pd.DataFrame()
#
#     data = []
#     for row in rows:
#         time = row.find("TIME").text
#         value = row.find("DATA_VALUE").text
#         try:
#             data.append({"Date": time, "Value": value})
#         except ValueError:
#             continue
#     df = pd.DataFrame(data)
#
#     # 날짜 형식 파싱
#     if cycle == "D":
#         df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
#     elif cycle == "M":
#         df["Date"] = pd.to_datetime(df["Date"], format="%Y%m")
# #    elif cycle == "Q":
# #        df["Date"] = pd.to_datetime(df["Date"].str.replace("Q", "-Q"), format="%Y%Q")
#     elif cycle == "Q":
#         df["Date"] = df["Date"].apply(
#             lambda x: pd.Timestamp(year=int(x[:4]), month=(int(x[-1]) - 1) * 3 + 1, day=1)
#         )
#
#     elif cycle == "A":
#         df["Date"] = pd.to_datetime(df["Date"], format="%Y")
#
#     # 숫자 변환 (문자 → float, 변환 안 되면 NaN)
#     df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
#     df.to_csv(cache_path, index=False)
#     print(f"✅ Fetched and cached: {stat_name}")
#     return df
# ```
# %% [markdown]
# ## item 코드를 1개만 입력하는 경우 사용하는 def
# %%
def fetch_ecos_series(stat_name, stat_code, item_code, cycle, start_date, end_date, cache_dir="ecos_cache",
                      use_cache=True):
    os.makedirs(cache_dir, exist_ok=True)

    # Convert dates to ECOS format
    start_fmt = convert_date_format(start_date, cycle)
    end_fmt = convert_date_format(end_date, cycle)
    api_key = API_KEY_ECOS

    cache_path = os.path.join(cache_dir, f"{stat_name}_{start_fmt}_{end_fmt}_{item_code}_{cycle}.csv")

    if use_cache and os.path.exists(cache_path):
        print(f"📥 Loaded from cache: {stat_name}")
        return pd.read_csv(cache_path, parse_dates=["Date"])

    length = calculate_length(start_date, end_date, cycle)

    url = (
        f"http://ecos.bok.or.kr/api/StatisticSearch/"
        f"{api_key}/xml/en/1/{length}/"
        f"{stat_code}/{cycle}/{start_fmt}/{end_fmt}/{item_code}/"
    )

    response = requests.get(url)
    if response.status_code != 200:
        print("❌ HTTP error:", response.status_code)
        return pd.DataFrame()

    root = ET.fromstring(response.content)
    rows = root.findall(".//row")

    if not rows:
        print(f"❌ No data found for {stat_name} - item_code: {item_code}")
        return pd.DataFrame()

    data = []
    for row in rows:
        time = row.find("TIME").text
        value = row.find("DATA_VALUE").text
        try:
            data.append({"Date": time, "Value": float(value)})
        except ValueError:
            continue

    df = pd.DataFrame(data)

    # 날짜 형식 파싱
    if cycle == "D":
        df["Date"] = pd.to_datetime(df["Date"], format="%Y%m%d")
    elif cycle == "M":
        df["Date"] = pd.to_datetime(df["Date"], format="%Y%m")
    elif cycle == "Q":
        df["Date"] = pd.to_datetime(df["Date"].str.replace("Q", "-Q"), format="%Y-%Q")
    elif cycle == "Y":
        df["Date"] = pd.to_datetime(df["Date"], format="%Y")

    df.to_csv(cache_path, index=False)
    print(f"✅ Fetched and cached: {stat_name}")
    return df
# %% [markdown]
# ## test code, item code 1개만 넣는 경우임
# ```python
# series_list = [
#     ["CPI",     "901Y009",  "0",        "M"],
#     ["Gold",    "902Y003",  "040101",   "M"],
#     ["Dollar",  "731Y001",  "0000001",  "D"]# hypothetical daily gold data
# ]
#
# # 추출하고자 하는 항목의 시계열 시작, 종료 지정
# # 월별 자료는 202501 형식
# # 📦 Fetch all
#
# start_date = "2000-01-01"
# end_date = "2025-12-31"
# cycle = "D"
#
#
#
# dfs = {}
# for name, stat_code, item_code, cycle in series_list:
#     dfs[name] = fetch_ecos_series(name, stat_code, item_code, cycle, start_date, end_date)
#
#
# # 중복 검증
#
# for name in dfs:
#     dfs[name] = dfs[name].drop_duplicates(subset='Date').reset_index(drop=True)
#
# for name, df in dfs.items():
#     dup_count = df.duplicated().sum()
#     print(f"{name}: {dup_count} duplicates")
#
# #print(dfs)
#
#
# df=dfs['Gold']
# print(df)
# ```