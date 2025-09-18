# NPF 수정 데이터를 불러와서 csv 파일로 저장하는 코드
# "data/nfp_revisions.csv" 이렇게 저장됨


import pandas as pd
import requests
import time
import os

from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv


# Load your FRED API key from .env
load_dotenv()

# Please replace  os.getenv("FRED_API_KEY") with your actual FRED API key.
API_KEY = os.getenv("FRED_API_KEY")

# Series ID for total nonfarm payrolls
SERIES_ID = "PAYEMS"
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Select target month
start = '1990-01-01'
end = '2025-09-04'


def generate_target_months(start, end):
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    months = pd.date_range(start=start_date, end=end_date, freq='MS').strftime('%Y-%m-%d').tolist()
    return months


target_months = generate_target_months(start, end)


def get_vintage_dates(series_id, api_key):
    """Fetches all available vintage dates for a FRED series."""
    url = f"https://api.stlouisfed.org/fred/series/vintagedates?series_id={series_id}&api_key={api_key}&file_type=json"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        return data.get('vintage_dates', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching vintage dates: {e}")
        return []


def fetch_monthly_change(vintage_date, target_month):
    """Fetches the month-over-month change for a specific vintage and target month."""
    month_dt = pd.to_datetime(target_month)
    prev_month_dt = month_dt - relativedelta(months=1)
    prev_month = prev_month_dt.strftime("%Y-%m-%d")

    params = {
        "series_id": SERIES_ID,
        "api_key": API_KEY,
        "file_type": "json",
        "realtime_start": vintage_date,
        "realtime_end": vintage_date,
        "observation_start": prev_month,
        "observation_end": target_month
    }
    try:
        # Adding a small delay to be respectful of the API rate limits
        time.sleep(0.5)
        r = requests.get(BASE_URL, params=params)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.HTTPError as e:
        # This is now a more informative error message
        if e.response.status_code == 400:
            print(
                f"Bad request for {vintage_date} | {target_month}. Check API key or parameters. Message: {e.response.text}")
        else:
            print(f"HTTPError for {vintage_date} | {target_month}: {e}")
        return None

    observations = data.get('observations', [])
    if len(observations) != 2:
        return None

    try:
        # The FRED API doesn't guarantee the order, so we need to sort by date
        observations.sort(key=lambda x: x['date'])
        val1 = float(observations[0]['value'])
        val2 = float(observations[1]['value'])
        return val2 - val1, val2
    except (ValueError, KeyError) as e:
        print(f"Invalid numeric values or keys in observations for {vintage_date} | {target_month}: {e}")
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

    rev_2_minus_1 = (changes[1] - changes[0]) if all(c is not None for c in changes[:2]) else None
    rev_3_minus_2 = (changes[2] - changes[1]) if all(c is not None for c in changes[1:]) else None
    rev_3_minus_1 = (changes[2] - changes[0]) if all(c is not None for c in [changes[0], changes[2]]) else None

    return {
        '1st': changes[0],
        '2nd': changes[1],
        '3rd': changes[2],
        '2nd - 1st': rev_2_minus_1,
        '3rd - 2nd': rev_3_minus_2,
        '3rd - 1st': rev_3_minus_1,
        'val2_first_vintage': val2_first  # 👈 new column
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
            (all_vintages_dt.year == release_month.year) &
            (all_vintages_dt.month == release_month.month)
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
        print("Could not retrieve vintage dates. This might be due to an invalid API key or network issues. Exiting.")
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
                revision['month'] = month
                revision['vintage_completeness'] = completeness
                revision['1st_vintage_key'] = vintage_keys[0] # <<< MODIFIED: Added this line as requested.
                results.append(revision)
            else:
                print(f"Skipping {month} — revision calculation failed.")

        valid_results = [r for r in results if isinstance(r, dict) and 'month' in r]
        if not valid_results:
            print("\nNo valid data to build DataFrame.")
        else:
            print("\n--- Revision Analysis Results ---")
            df_day = pd.DataFrame(valid_results).set_index('month')
            print(df_day)

            # <<< MODIFIED SECTION: Added the logic below to create the new column >>>
            # Ensure the index is a DatetimeIndex and sorted for correct time-series operations.
            df_day.index = pd.to_datetime(df_day.index)
            df_day.sort_index(inplace=True)

            # Create the new column by summing the lagged values from the specified columns.
            # .shift(1) gets the value from 1 month ago.
            # .shift(2) gets the value from 2 months ago.
            lag_1_rev_2_1 = df_day['2nd - 1st'].shift(1)
            lag_2_rev_3_2 = df_day['3rd - 2nd'].shift(2)
            df_day['revision1'] = lag_1_rev_2_1
            df_day['revision2'] = lag_2_rev_3_2
            # <<< END OF MODIFIED SECTION >>>

            print("\n--- Revision Analysis Results ---")
            print(df_day)

            output_filename = "nfp_revisions.csv"

            # 디렉토리 없으면 자동 생성
            os.makedirs("data", exist_ok=True)

            # csv 파일 저장
            df_day.to_csv(f'data/{output_filename}')


