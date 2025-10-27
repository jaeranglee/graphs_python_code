# %% [markdown]
# # [그림 47] 월별 미재무부 국채 바이백 낙찰규모
# ## 같은 디렉토리에 필요한 file
#   - plot_def.py : 한글폰트 추가, 그래프 저장
#   - treasury_buybacks_api.py  : Treasury Fiscal Data, Treasury Buybacks Data Fetch
# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 폰트 설정
from plot_def import *
set_fonts()

#=================================
# 필요시 자료를 fetch 해서 csv로 저장하는 def

from treasury_buybacks_api import fetch_buybacks

start = "2024-01-01"
end = "2025-12-31"

output_path = fetch_buybacks(start_date=start, end_date=end)
#=================================


output_path = "data/treasury_buybacks.csv"


df=pd.read_csv(output_path)


# --- 3. 데이터 전처리 ---
# 날짜, 숫자 변환
df['operation_date'] = pd.to_datetime(df['operation_date'])
df['coupon_rate_pct'] = pd.to_numeric(df['coupon_rate_pct'], errors='coerce')
df['maturity_date'] = pd.to_datetime(df['maturity_date'])
df['par_amt_accepted'] = pd.to_numeric(df['par_amt_accepted'], errors='coerce')
df['weighted_avg_accepted_price'] = pd.to_numeric(df['weighted_avg_accepted_price'], errors='coerce')

# 숫자 단위 조정 (단위: 백만 달러)
df['par_amt_accepted'] = df['par_amt_accepted']/1e9

# 월(month) 컬럼 생성
df['month'] = df['operation_date'].dt.month
df['day'] = df['operation_date'].dt.day
df['year_month'] = df['operation_date'].dt.to_period('M')

# 필요한 증권 종류만 필터링
# 잔존 만기 10년 이상 필터링
df = df[df['operation_date']<'2025-12-31']

# 잔존 만기 계산 (일 단위)
df['tenor_days'] = (df['maturity_date'] - df['operation_date']).dt.days

# 잔존 만기가 10년(3650일) 이상인 것만 선택
df_long = df[df['tenor_days'] >= 3650]
df_short = df[df['tenor_days'] < 365]

monthly_sum = df.groupby('year_month', as_index=False)["par_amt_accepted"].sum()
monthly_sum['year_month'] = monthly_sum['year_month'].dt.to_timestamp()

long_monthly_sum = df_long.groupby('year_month', as_index=False)["par_amt_accepted"].sum()
long_monthly_sum['year_month'] = long_monthly_sum['year_month'].dt.to_timestamp()


# --- Plot ---
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

# set bar width as 10 days
bar_width = pd.Timedelta(days=10)

ax.bar(monthly_sum['year_month'] - bar_width/2,
       monthly_sum['par_amt_accepted'],
       width=bar_width,
       label='Total',
       color='blue')

ax.bar(long_monthly_sum['year_month'] + bar_width/2,
       long_monthly_sum['par_amt_accepted'],
       width=bar_width,
       label='Matures after 10 years',
       color='black')


# 축 및 서식
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

ax.text(0, 1.02, '(십억 달러)', ha='left', va='bottom',
             transform=ax.transAxes, fontsize=12)
ax.legend(loc='upper left')
ax.grid(True, linestyle='--', color='gray', alpha=0.3)
ax.text(0, -0.15, '출처: Treasury Fiscal Data, Treasury Buybacks Data', transform=ax.transAxes, fontsize=10)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()