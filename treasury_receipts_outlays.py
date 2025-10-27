# %% [markdwon]
# - Monthly Treasury Statement (MTS),
#   - Summary of Receipts and Outlays of the US Government, Table
# 홈피에서 CSV 파일로 다운
# ```python
# file_path="data/MTS_RcptSrcOutlyAgcy_20150331_20250831.csv"
# def fetch_receipts_outlays_csv(start_date, end_date,
#                           file_path=None):
# start = '2020-01-01'
# end =' 2025-12-31'
# from treasury_receipts_outlays_csv(start_date=start, end_date=end)
# ```
# 미국 연방 정부 월별 지출, 수입 데이터 parsing
# ## parameters
# | Parameter    | Type  | Description                                     |
# |--------------|-------|-------------------------------------------------|
# | `file_path`  | `str` | path and data file name, None, use with new file|
# | `start_date` | `str` | start date, 'YYYY-MM-DD'                        |
# | `end_date`   | `str` | end date, 'YYYY-MM-DD'                          |
# %%
#%config InlineBackend.close_figures = False
import pandas as pd

def treasury_receipts_outlays_csv(start_date, end_date, file_path=None):
    file_path = "data/MTS_RcptSrcOutlyAgcy_20150331_20250831.csv"
    df = pd.read_csv(file_path)
    df = df.rename(columns={
        'Record Date': 'observation_date'
    })
    df['observation_date'] = pd.to_datetime(df['observation_date'])
    df['Current Month Receipt or Outlay Amount'] = pd.to_numeric(
        df['Current Month Receipt or Outlay Amount'], errors="coerce" )

    return df