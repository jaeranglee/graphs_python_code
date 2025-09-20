# [그림 37] 은행 지급준비금과 1일물 금리(2024년 이후)
# [그림 38] 은행 지급준비금과 1일물 금리(2023년)
# [그림 39] IORB와 TGCR, SOFR 차이

# 같은 디렉토리에 필요한 파일

# plot_def.py
# fred_api.py
# nyfed_api_all_rates.py


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# setting Korean fonts
from plot_def import *
set_fonts()

# FRED fetch 함수
from fred_api import fetch_fred_series


start0 ='2017-01-01'
end = '2025-12-31'

# fetch data
# IOER (2008~2021.06)
df_ioer = fetch_fred_series('IOER', start_date=start0, end_date=end)

df0 = fetch_fred_series('WRESBAL', start_date=start0, end_date=end)
df1 = fetch_fred_series('IORB', start_date=start0, end_date=end)
df2 = fetch_fred_series('SOFR', start_date=start0, end_date=end)
df3 = fetch_fred_series('RIFSPFFNB', start_date=start0, end_date=end)
df4 = fetch_fred_series('DFEDTARU', start_date=start0, end_date=end)
df4_l = fetch_fred_series('DFEDTARL', start_date=start0, end_date=end)  # Lower Target 추가


# merge df to make plots
df1_new = pd.concat([df_ioer, df1]).drop_duplicates('observation_date').sort_values('observation_date')
df1_new = df1_new.rename(columns={'value': 'IORB_new'})


df4['DFEDTARL'] = df4_l['DFEDTARL']  # 상하한 결합


# New York Fed Markets Data API fetch def
# nyfed_api_all_rates.py로 만든 def 호출

from nyfed_api_all_rates import fetch_all_secured_rates


# fetch all types of rates data from NY Fed Markets Data
df_all = fetch_all_secured_rates(start_date=start0, end_date=end, rate_type_filter='all')

# select 'TGCR' from df_all
rate_type_filter = "tgcr"

dftr = df_all[df_all["Type"] == rate_type_filter.upper()].copy()
dftr = dftr.rename(columns={"Date": "observation_date"})


# 필터링 함수
def filter_dataframes(start, end=None):
    if end:
        df0_f = df0[(df0['observation_date'] >= start) & (df0['observation_date'] <= end)].copy()
        df1_f = df1[(df1['observation_date'] >= start) & (df1['observation_date'] <= end)].copy()
        df2_f = df2[(df2['observation_date'] >= start) & (df2['observation_date'] <= end)].copy()
        dftr_f = dftr[(dftr['observation_date'] >= start) & (dftr['observation_date'] <= end)].copy()
        df3_f = df3[(df3['observation_date'] >= start) & (df3['observation_date'] <= end)]
        df4_f = df4[(df4['observation_date'] >= start) & (df4['observation_date'] <= end)]
    else:
        df0_f = df0[df0['observation_date'] >= start].copy()
        df1_f = df1[df1['observation_date'] >= start].copy()
        df2_f = df2[df2['observation_date'] >= start].copy()
        dftr_f = dftr[dftr['observation_date'] >= start].copy()
        df3_f = df3[df3['observation_date'] >= start]
        df4_f = df4[df4['observation_date'] >= start]

    return df0_f, df1_f, df2_f, dftr_f, df3_f, df4_f

# 루프
for i in [1, 2, 3]:
    if i == 1:
        # print("2023년 자료로 그리는 중...")
        # 그림 38 data
        start, end = '2023-01-01', '2023-12-31'
        df0_f, df1_f, df2_f, dftr_f, df3_f, df4_f = filter_dataframes(start, end)


    elif i==2:
        # print("2024년 이후 자료로 그리는 중...")
        # 그림 37 data
        start = '2024-01-01'
        df0_f, df1_f, df2_f, dftr_f, df3_f, df4_f = filter_dataframes(start)


    elif i==3:

        # print("2021년 9월 이후 자료로 그리는 중...")
        # 그림 39 data
        df0_f, df1_f, df2_f, dftr_f, df3_f, df4_f = filter_dataframes("2021-09-01")

        diff = pd.merge(df1_f, dftr_f, on='observation_date', how='inner')
        diff = pd.merge(diff, df2_f, on='observation_date', how='inner')


        # Data for f39
        diff['spread'] =  diff['Rate'] -diff['IORB']
        diff['sofr_spread'] = diff['SOFR'] - diff['IORB']


        # 시각화
        #
        fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

        ax.plot(diff['observation_date'], diff['sofr_spread'], label='SOFR', lw=2, color='green')
        ax.plot(diff['observation_date'], diff['spread'], label='TGCR', lw=2, color='blue')


        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.text(0, 1.00, '(%)', ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
        ax.text(0, -0.15, '출처: FRED, NY FED', transform=ax.transAxes, fontsize=10)
        ax.axhline(y=0, color='red', linestyle='-', linewidth=2, label='IORB')
        ax.grid(True, linestyle='--', color='black', alpha=0.3)
        ax.legend(loc='upper left', bbox_to_anchor=(0.35, 1))
        ax.set_ylim(-0.25, 0.25)

    if i in [1, 2]:

        # 시각화
        fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

        # 왼쪽: 지급준비금
        ax[0].plot(df0_f['observation_date'], df0_f['WRESBAL'] / 1e3, label='지급준비금', lw=2, color='red')
        ax[0].legend(loc='upper left', bbox_to_anchor=(0.35, 1))
        ax[0].xaxis.set_major_locator(mdates.MonthLocator(interval=4))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax[0].text(0, 1.00, '(조 달러)', ha='left', va='bottom', transform=ax[0].transAxes, fontsize=12)
        ax[0].text(0, -0.15, '출처: FRED', transform=ax[0].transAxes, fontsize=10)
        ax[0].grid(False)

        # 오른쪽: 금리들
        ax[1].plot(df1_f['observation_date'], df1_f['IORB'], label='IORB', lw=2, color='red')
        ax[1].plot(df2_f['observation_date'], df2_f['SOFR'], label='SOFR', lw=2, color='green')
        ax[1].plot(dftr_f['observation_date'], dftr_f['Rate'], label='TGCR', lw=2, color='blue')
        ax[1].fill_between(df4_f['observation_date'], df4_f['DFEDTARU'], df4_f['DFEDTARL'], color='gray', alpha=0.2,
                           label='Target Range')

        ax[1].legend(loc='upper left', bbox_to_anchor=(0.63, 0.65))
        ax[1].xaxis.set_major_locator(mdates.MonthLocator(interval=4))
        ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax[1].text(0, 1.00, '(%)', ha='left', va='bottom', transform=ax[1].transAxes, fontsize=12)
        ax[1].text(0, -0.15, '출처: FRED, NY Fed', transform=ax[1].transAxes, fontsize=10)
        ax[1].grid(False)


    # 저장 및 출력
    # python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
    plot_save(i=i)