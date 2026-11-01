# %% [markdown]
# # NFP 수정 내역 만들기 (data/nfp_revisions.csv)
#
# ## 이 코드가 하는 일
# NFP(비농업 고용)가 처음 발표된 값과 그 뒤 두 번 수정된 값을 모아 data/nfp_revisions.csv 파일로 저장한다.
# 그림을 그리지는 않는다. [그림 15] f15_nfp_revision_1st_final.py와 [그림 16] f16_nfp_2month_revisions.py가 이 파일을 읽는다.
#
# ## 다루는 내용
# FRED는 가장 최근에 수정된 값만 보여준다. 과거 어느 날 발표됐던 값을 보려면 ALFRED(FRED의 과거 발표치 서비스)를 써야 한다.
# ALFRED는 자료가 발표되거나 수정될 때마다 그 시점의 값(vintage)을 따로 보관한다.
#
# ## 하는 순서
# 1. PAYEMS(비농업 고용자 수)의 발표 날짜(vintage) 목록을 받는다.
# 2. 1990년부터 달마다 첫 발표, 두 번째 발표, 세 번째 발표 때의 값을 받아 전월 대비 증감을 구한다.
# 3. 1st, 2nd, 3rd 값과 그 차이(수정 폭)를 표로 만들어 csv로 저장한다.
#
# ## 필요한 파일
# - fred_api.py (defs): fetch_fred_vintage_dates(), fetch_fred_as_of()
# - defs/.env의 FRED_API_KEY
#
# 요청을 많이 보내므로 실행에 몇 분 걸린다.
# %%
import os
import time

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
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

from dotenv import load_dotenv

# FRED 요청 함수는 defs/fred_api.py에 있음 (vintage 날짜 목록, 특정 발표 시점의 값)
from fred_api import fetch_fred_as_of, fetch_fred_vintage_dates

# Load your FRED API key from .env
load_dotenv(_defs / ".env")

# Please replace  os.getenv("FRED_API_KEY") with your actual FRED API key.
API_KEY = os.getenv("FRED_API_KEY")

# Series ID for total nonfarm payrolls
SERIES_ID = "PAYEMS"
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Select target month
start = "1990-01-01"
end = "2025-09-04"


def generate_target_months(start, end):
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    months = (
        pd.date_range(start=start_date, end=end_date, freq="MS")
        .strftime("%Y-%m-%d")
        .tolist()
    )
    return months


target_months = generate_target_months(start, end)


def get_vintage_dates(series_id, api_key):
    """Fetches all available vintage dates for a FRED series."""
    # api_key는 예전 호출 형식을 지키려고 남겨 둠 (키는 fred_api가 .env에서 읽음)
    return fetch_fred_vintage_dates(series_id)


def fetch_monthly_change(vintage_date, target_month):
    """Fetches the month-over-month change for a specific vintage and target month."""
    month_dt = pd.to_datetime(target_month)
    prev_month_dt = month_dt - relativedelta(months=1)
    prev_month = prev_month_dt.strftime("%Y-%m-%d")

    try:
        # Adding a small delay to be respectful of the API rate limits
        time.sleep(0.5)
        observations = fetch_fred_as_of(SERIES_ID, vintage_date, prev_month, target_month)
    except requests.exceptions.HTTPError as e:
        # This is now a more informative error message
        if e.response.status_code == 400:
            print(
                f"Bad request for {vintage_date} | {target_month}. Check API key or parameters. Message: {e.response.text}"
            )
        else:
            print(f"HTTPError for {vintage_date} | {target_month}: {e}")
        return None

    if len(observations) != 2:
        return None

    try:
        # The FRED API doesn't guarantee the order, so we need to sort by date
        observations.sort(key=lambda x: x["date"])
        val1 = float(observations[0]["value"])
        val2 = float(observations[1]["value"])
        return val2 - val1, val2
    except (ValueError, KeyError) as e:
        print(
            f"Invalid numeric values or keys in observations for {vintage_date} | {target_month}: {e}"
        )
        return None


def calculate_revisions(target_month, vintage_keys):
    """Calculates revisions and captures val2 from the 1st vintage."""
    changes = []
    val2_first = None

    for idx, vintage in enumerate(vintage_keys):
        if vintage is not None:
            change, val2 = fetch_monthly_change(vintage, target_month)
        else:
            change, val2 = None, None

        changes.append(change)
        if idx == 0:
            val2_first = val2

    while len(changes) < 3:
        changes.append(None)

    rev_2_minus_1 = (
        (changes[1] - changes[0]) if all(c is not None for c in changes[:2]) else None
    )
    rev_3_minus_2 = (
        (changes[2] - changes[1]) if all(c is not None for c in changes[1:]) else None
    )
    rev_3_minus_1 = (
        (changes[2] - changes[0])
        if all(c is not None for c in [changes[0], changes[2]])
        else None
    )

    return {
        "1st": changes[0],
        "2nd": changes[1],
        "3rd": changes[2],
        "2nd - 1st": rev_2_minus_1,
        "3rd - 2nd": rev_3_minus_2,
        "3rd - 1st": rev_3_minus_1,
        "val2_first_vintage": val2_first,  # 👈 new column
    }


def get_monthly_release_vintages(target_month, all_vintage_dates):
    """
    Gets the 1st, 2nd, and 3rd release vintages for a target month by finding
    the first vintage date in each of the three subsequent months.
    """
    target_dt = pd.to_datetime(target_month)
    all_vintages_dt = pd.to_datetime(all_vintage_dates).sort_values()
    selected_vintages = []

    for i in range(1, 4):
        release_month = target_dt + pd.DateOffset(months=i)
        vintages_in_month = all_vintages_dt[
            (all_vintages_dt.year == release_month.year)
            & (all_vintages_dt.month == release_month.month)
        ]
        if not vintages_in_month.empty:
            selected_vintages.append(vintages_in_month[0].strftime("%Y-%m-%d"))
        else:
            selected_vintages.append(None)
    return selected_vintages


# --- Main Execution ---
if API_KEY == "your_key_here":
    print("FATAL: Please replace 'your_key_here' with your actual FRED API key.")
else:
    print("Fetching all available vintage dates from FRED...")
    vintages = get_vintage_dates(SERIES_ID, API_KEY)

    if not vintages:
        print(
            "Could not retrieve vintage dates. This might be due to an invalid API key or network issues. Exiting."
        )
    else:
        print(f"Found {len(vintages)} vintage dates.")
        print("\nDetermining correct vintage dates for each month...")
        selected_keys_by_month = {
            month: get_monthly_release_vintages(month, vintages)
            for month in target_months
        }

        for month, keys in selected_keys_by_month.items():
            print(f"{month}: {keys}")

        print("\nCalculating revisions for each month...")
        results = []
        for month in target_months:
            vintage_keys = selected_keys_by_month.get(month)
            if not vintage_keys or all(key is None for key in vintage_keys):
                print(f"Skipping {month} — no usable vintages found.")
                continue

            usable_keys = [key for key in vintage_keys if key is not None]
            completeness = f"{len(usable_keys)} vintage(s)"

            revision = calculate_revisions(month, vintage_keys)

            if revision is not None:
                revision["month"] = month
                revision["vintage_completeness"] = completeness
                revision["1st_vintage_key"] = vintage_keys[
                    0
                ]  # <<< MODIFIED: Added this line as requested.
                results.append(revision)
            else:
                print(f"Skipping {month} — revision calculation failed.")

        valid_results = [r for r in results if isinstance(r, dict) and "month" in r]
        if not valid_results:
            print("\nNo valid data to build DataFrame.")
        else:
            print("\n--- Revision Analysis Results ---")
            df_day = pd.DataFrame(valid_results).set_index("month")
            print(df_day)

            # <<< MODIFIED SECTION: Added the logic below to create the new column >>>
            # Ensure the index is a DatetimeIndex and sorted for correct time-series operations.
            df_day.index = pd.to_datetime(df_day.index)
            df_day = df_day.sort_index()

            # Create the new column by summing the lagged values from the specified columns.
            # .shift(1) gets the value from 1 month ago.
            # .shift(2) gets the value from 2 months ago.
            lag_1_rev_2_1 = df_day["2nd - 1st"].shift(1)
            lag_2_rev_3_2 = df_day["3rd - 2nd"].shift(2)
            df_day["revision1"] = lag_1_rev_2_1
            df_day["revision2"] = lag_2_rev_3_2
            # <<< END OF MODIFIED SECTION >>>

            print("\n--- Revision Analysis Results ---")
            print(df_day)

            output_filename = "nfp_revisions.csv"

            # 디렉토리 없으면 자동 생성
            os.makedirs("data", exist_ok=True)

            # csv 파일 저장
            df_day.to_csv(f"data/{output_filename}")
