# %% [markdown]
# # [그림 54] 수입증가율과 재고투자 증가율
# ## 같은 디렉토리에 필요한 file
#   - plot_def.py : 한글폰트 추가, 그래프 저장
#   - fred_api.py       : FRED, api key required
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 폰트 설정
from plot_def import *
set_fonts()

start='2020-01-01'
end='2026-01-01'

# Fetch series
#---------------------
from fred_api import fetch_fred_series

# 각 시리즈에서 필요한 열 추출
bopimp = fetch_fred_series('BOPTIMP', start_date=start, end_date=end)
imp0004 = fetch_fred_series('IMP0004', start_date=start, end_date=end)
businv = fetch_fred_series('BUSINV', start_date=start, end_date=end)
# Contributions to percent change in real gross domestic product: Gross private domestic investment: Change in private inventories (A014RY2Q224SBEA)
invq1 = fetch_fred_series('A014RY2Q224SBEA', start_date=start, end_date=end)
invq = fetch_fred_series('NA000342Q', start_date=start, end_date=end)


# 전년동기대비 (YoY) 계산
bopimp['YoY'] = bopimp['BOPTIMP'].pct_change(12) * 100
imp0004['YoY'] = imp0004['IMP0004'].pct_change(12) * 100

# 전월대비 (MoM) 계산
#businv['MoM'] = businv['BUSINV'].pct_change() * 100
invq['MoM'] = invq['NA000342Q'].pct_change() * 100

# 2021년 이후로 필터링
bopimp = bopimp[bopimp['observation_date'] >= '2021-01-01']
imp0004 = imp0004[imp0004['observation_date'] >= '2021-01-01']
businv = businv[businv['observation_date'] >= '2021-01-01']
invq = invq[invq['observation_date'] >= '2021-01-01']

# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: 수입 (전년동기대비)
ax[0].plot(bopimp['observation_date'], bopimp['YoY'], label='국제수지기준 수입', lw=2, color='blue')
ax[0].plot(imp0004['observation_date'], imp0004['YoY'], label='통관기준 수입', lw=2, color='black')
ax[0].axhline(y=0, color='gray', linestyle='--')

ax[0].legend()
ax[0].xaxis.set_major_locator(mdates.YearLocator(1))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[0].text(0, 1.00, '(%, 전년동월대비)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)
ax[0].text(0.0, -0.15, "출처: BEA, FRED", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(False)

# 오른쪽: 재고 (전월대비)
#ax[1].plot(businv['observation_date'], businv['BUSINV'], label='BUSINV', lw=2, color='green')
ax[1].plot(invq1['observation_date'], invq1['A014RY2Q224SBEA'], label='GDP기준 재고투자', lw=2, color='black')
ax[1].plot(invq['observation_date'], invq['MoM'], label='GDP기준 수입', lw=2, color='blue')
ax[1].axhline(y=0, color='gray', linestyle='--')
ax[1].set_ylim(-5, 14)

ax[1].legend()
ax[1].xaxis.set_major_locator(mdates.YearLocator(1))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))


# 단위 표시 및 출처
ax[1].text(0, 1.00, '(%, 전기대비)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(0.0, -0.15, "출처: BEA, FRED", transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()