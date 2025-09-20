# [그림 40] 연준의 RP 거래

# 같은 디렉토리에 필요한 파일

# plot_def.py

# 두개 가운데 하나를 선택. 동일한 그래프 출력

# fred_api.py       : FRED, api key required
# nyfed_api_rp.py   : NY Fed Markets Data, no api key required


import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set font depending on the platform
from plot_def import *
set_fonts()


start = '2023-01-01'
end = '2025-12-31'

'''
# fetch from FRED
# same results as with NY FED Markets Data 
# Overnight Repurchase Agreements: Total Securities Purchased by the Federal Reserve
# in the Temporary Open Market Operations (RPONTTLD) in Billion US Dollars

from fred_api import fetch_fred_series

df = fetch_fred_series(series_id="RPONTTLD", start_date=start, end_date=end)

# 그래프 그리기

fig, ax = plt.subplots(figsize=(8, 4.5),constrained_layout=True)

ax.plot(df['observation_date'], df['RPONTTLD'], label='RP', color='blue', lw=2)


ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

ax.text(0, 1.00, '(십억 달러)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)
plt.grid(False)

ax.text(0.0, -0.15, "출처: FRED", transform=ax.transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')
'''


# fetch from NY FED Markets Data, case wise
# FRED 와 동일한 결과

from nyfed_api_rp import *
df = fetch_rp_operation(start_date=start, end_date=end)

# 데이터 전처리
# 날짜, 숫자 변환

df['Accepted'] = pd.to_numeric(df['Accepted'], errors='coerce') / 1e9
df['Limit'] = pd.to_numeric(df['Limit'], errors='coerce') / 1e9

# 날짜 변환 실패(NaT) 행 제거
df.dropna(subset=['Date'], inplace=True)


# 필요한 증권 종류만 필터링
type_to_plot = "Repo"

df_filtered = df[df['Type']==type_to_plot]

# Sum accepted amount by day
# NY Fed has term filter, [overnight, term]
df_daily_sum = df_filtered.groupby(df['Date'].dt.date)['Accepted'].sum().reset_index()



# --- 시각화 ---

fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

ax.plot(df_daily_sum['Date'], df_daily_sum['Accepted'], label='RP', lw=2, color='blue')


ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # 6 month 간격으로 눈금 표시
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # year-month 표시

ax.text(0, 1.00, '(10억 달러)', ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
ax.text(0, -0.15, '출처: NY Fed Markets Data', transform=ax.transAxes, fontsize=10)
ax.grid(False)

plt.legend()



# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()