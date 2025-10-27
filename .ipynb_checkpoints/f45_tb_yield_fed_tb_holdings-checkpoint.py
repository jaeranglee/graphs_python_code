# %% [markdown]
# # [그림 45] 미국채 수익률
# # [그림 46] 연준의 미국채 보유액
# ## 같은 디렉토리에 필요한 file
#   - plot_def.py : 한글폰트 추가, 그래프 저장
#   - fred_api.py
# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 폰트 설정
from plot_def import *
set_fonts()

start='2002-01-01'
end='2099-12-31'

# Fetch from FRED

# 데이터 수집
df0 = fetch_fred_series('DGS10', start_date=start, end_date=end)
df1 = fetch_fred_series('DGS2', start_date=start, end_date=end)
df2 = fetch_fred_series('WSHOTSL', start_date=start, end_date=end)
df3 = fetch_fred_series('WSHONBNL', start_date=start, end_date=end)

tb1 = pd.merge(df0, df1, on='observation_date').copy()


# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: 국채금리
ax[0].plot(tb1['observation_date'], tb1['DGS10'], label='10년물', lw=1.5, color='black')
ax[0].plot(tb1['observation_date'], tb1['DGS2'], label='2년물', lw=1.5, color='blue')


ax[0].legend(loc='upper left',bbox_to_anchor=(0.35, 1))
ax[0].xaxis.set_major_locator(mdates.YearLocator(3))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[0].text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)
ax[0].text(0.0, -0.15, "출처: FRED, 음영은 국채 바이백 기간", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(False)

# 오른쪽: 연준 국채보유액

ax[1].plot(df2['observation_date'], df2['WSHOTSL']/1e6, label='국채', lw=2, color='black')
ax[1].plot(df3['observation_date'], df3['WSHONBNL']/1e6, label='중장기 국채', lw=2, color='blue')

ax[1].legend(loc='upper left',bbox_to_anchor=(0.35, 1))
ax[1].xaxis.set_major_locator(mdates.YearLocator(3))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[1].text(0, 1.00, '(조 달러)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(0.0, -0.15, "출처: FRED, 음영은 국채 바이백 기간", transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)

# 음영 구간 추가: 바이백 실시 시기
from datetime import datetime
shaded_periods = [
    #(datetime(2014, 1, 1), datetime(2023, 12, 31)),
    (datetime(2024, 5, 1), datetime(2025, 12, 31))]

for i in [0,1]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color='gray', alpha=0.2)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()