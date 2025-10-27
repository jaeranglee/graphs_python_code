# %% [markdown]
# # [그림 56] 소비자물가지수와 PCE물가지수 상승률
# ## 같은 디렉토리에 필요한 file
#   - plot_def.py : 한글폰트 추가, 그래프 저장
#   - fred_api.py
# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 한글 폰트 설정

from plot_def import set_fonts
set_fonts()

from fred_api import fetch_fred_series

# 사용자 정의 기간으로 호출
start = "1990-01-01"
end = "2026-01-01"


# 소비자물가지수, 근원물가지수, not seasonally adjusted
df_cpins = fetch_fred_series('CPIAUCNS', start_date=start, end_date=end)
df_corens = fetch_fred_series('CPILFENS', start_date=start, end_date=end)

# 소비자물가지수, 근원물가지수, seasonally adjusted
df_cpis = fetch_fred_series('CPIAUCSL', start_date=start, end_date=end)
df_cores= fetch_fred_series('CPILFESL', start_date=start, end_date=end)

# PCE Price Index
pce_df = fetch_fred_series("PCEPI", start_date=start, end_date=end)
pce_core_df = fetch_fred_series("PCEPILFE", start_date=start, end_date=end)

# Calculate YoY inflation rate

df_cpins['YoY_Inflation'] = df_cpins['CPIAUCNS'].pct_change(periods=12, fill_method=None) * 100
df_corens['YoY_Inflation'] = df_corens["CPILFENS"].pct_change(periods=12, fill_method=None) * 100
pce_df['YoY_pce'] = pce_df["PCEPI"].pct_change(periods=12, fill_method=None) * 100
pce_core_df['YoY_pcecore'] = pce_core_df["PCEPILFE"].pct_change(periods=12, fill_method=None) * 100

df_cpins['YoY_Inflation'] = pd.to_numeric(df_cpins['YoY_Inflation'], errors='coerce')
df_corens['YoY_Inflation'] = pd.to_numeric(df_corens['YoY_Inflation'], errors='coerce')
pce_df['YoY_pce'] = pd.to_numeric(pce_df['YoY_pce'], errors='coerce')
pce_core_df['YoY_pcecore'] = pd.to_numeric(pce_core_df['YoY_pcecore'], errors='coerce')

# Filter for >=2000
df_cpins = df_cpins[(df_cpins['observation_date'] >= '2000-01-01')].copy()
df_corens = df_corens[(df_corens['observation_date'] >= '2000-01-01')].copy()

pce_df = pce_df[pce_df['observation_date'] >= '2000-01-01'].copy()
pce_core_df = pce_core_df[pce_core_df['observation_date'] >= '2000-01-01'].copy()

# Plot
# CPI, PCE (왼쪽그림), Core CPI, Core PCE(오른쪽)
# CPI, PCE (왼쪽그림)

fig, ax = plt.subplots(1,2, figsize=(9, 4.5), constrained_layout=True )


ax[0].plot(df_cpins['observation_date'], df_cpins['YoY_Inflation'], color='blue', lw=2, label='소비자 물가지수')
ax[0].plot(pce_df['observation_date'], pce_df['YoY_pce'], color='black', lw=2, label='PCE 물가지수')


# Core CPI, Core PCE(오른쪽)
ax[1].plot(df_corens['observation_date'], df_corens['YoY_Inflation'], lw=2, color='blue', label='근원소비자 물가지수')
ax[1].plot(pce_core_df['observation_date'], pce_core_df['YoY_pcecore'], lw=2, color='black', label='근원PCE 물가지수')


# 음영 구간 추가, 2000년, 2025년
from datetime import datetime
shaded_periods = [
    (datetime(2000, 1, 1), datetime(2000, 12, 31)),
    (datetime(2025, 1, 1), datetime(2025, 12, 31))]

for i in [0,1]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color='gray', alpha=0.2)

        # Y축 눈금 (좌우 그림 높이를 대칭으로 만드는 부분)
        ax[i].set_ylim(-2, 9)

        # X축 눈금
        ax[i].xaxis.set_major_locator(mdates.YearLocator(3))
        ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

        # Add horizontal line at y = 2
        ax[i].axhline(y=2, color='gray', linestyle='--', linewidth=1)

        # 단위 표시 및 출처
        ax[i].text(0, 1.00, '(%, 전년동월대비)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[i].transAxes)

        ax[i].text(0.0, -0.15, "출처: BLS, BEA, FRED; 음영은 2000년, 2025년", transform=ax[i].transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')

        # 범례 (하나만 표시하거나 합칠 수도 있음)
        ax[i].legend(loc='upper left')
        ax[i].grid(False)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

from plot_def import plot_save
plot_save()