# [그림 29] 연준의 국채보유액과 연방정부의 연준예금(TGA)잔액

# 사용하는 함수 파일

# fred_api.py
# plot_def.py


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from plot_def import *
set_fonts()


# Assets: Securities Held Outright:
# U.S. Treasury Securities: Notes and Bonds, Nominal: Wednesday Level (WSHONBNL)
# in Million USD

#Assets: Securities Held Outright:
# U.S. Treasury Securities: Bills: Wednesday Level (WSHOBL)
# in Million USD

#Assets: Securities Held Outright:
# U.S. Treasury Securities: Notes and Bonds, Inflation-Indexed: Wednesday Level (WSHONBIIL)
# in Million USD

#Assets: Securities Held Outright:
# U.S. Treasury Securities: Wednesday Level (WSHOTSL)
# in Million USD

#Liabilities and Capital: Liabilities:
# Deposits with F.R. Banks, Other Than Reserve Balances:
# U.S. Treasury, General Account: Wednesday Level (WDTGAL)
# in Million USD


start='2020-01-01'
end='2025-12-31'


# FRED 상의 시리즈 ID (Constant Maturity Treasury Rates)
series_ids = {
    "Notes and Bonds": "WSHONBNL",
    "Bills": "WSHOBL",
    "TIPS": "WSHONBIIL",
    "Treasuries": "WSHOTSL",
    "TGA": "WDTGAL"
}


from fred_api import fetch_fred_series


# 모든 데이터 가져오기
all_data = {}
for term, sid in series_ids.items():
    df = fetch_fred_series(sid,start_date=start, end_date=end)

    df.rename(columns={df.columns[-1]: 'value'}, inplace=True)
    all_data[term] = df.set_index("observation_date")['value'].to_dict()


# 병합
soma = pd.DataFrame(all_data)


'''
# NY FED Markets Data 에서 soma holding 국채 잔액을 fetch 하는 함수.
# FRED에서 fetch하는 것과 동일함
# FRED api 사용을 권장
 
from nyfed_api import fetch_soma_holdings

soma = fetch_soma_holdings(start_date=start, end_date=end)

print(soma)
'''

# 시각화
fig, ax = plt.subplots(1,2, figsize=(8, 4.5), constrained_layout=True)

# 왼쪽:
ax[0].plot(soma.index, soma['Notes and Bonds']/1e6, label='Notes and Bonds', lw=2, color='red')
ax[0].plot(soma.index, soma['Bills']/1e6, label='Bills', lw=2, color='blue')

# 책에는 사용하지 않음
#ax[0].plot(soma.index, soma['TIPS']/1e6, label='TIPS', lw=2, color='orange')

ax[1].plot(soma.index, soma['TGA']/1e6, label='TGA', lw=2, color='blue')


for i in [0,1]:
    ax[i].legend(loc='upper left', bbox_to_anchor=(0.4, 0.7), fontsize= 12)


    ax[i].xaxis.set_major_locator(mdates.YearLocator())
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax[i].text(0, 1.00, '(조 달러)',  ha='left', va='bottom', transform=ax[i].transAxes, fontsize=12)
    ax[i].text(0, -0.15, '출처: FRED', transform=ax[i].transAxes, fontsize=12)

    ax[i].grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.7)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()