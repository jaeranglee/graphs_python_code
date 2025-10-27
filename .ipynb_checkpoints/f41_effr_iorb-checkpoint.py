# [그림 41] 1일물 단기자금 거래 규모
# [그림 42] EFFR 수준과 금리 분포

# 같은 디렉토리에 필요한 파일

# plot_def.py

# fred_api.py               : FRED, api key required
# nyfed_api_all_rates.py    : NY Fed Markets Data, for all overnight rates
# nyfed_api_rate_volume.py  : NY Fed Markets Data, for all overnight rate volume

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 폰트 설정
from plot_def import *
set_fonts()


start='2024-01-01'
end='2025-12-31'

# FRED API 호출 함수
from fred_api import fetch_fred_series

iorb = fetch_fred_series('IORB', start_date=start, end_date=end)

target_u = fetch_fred_series('DFEDTARU', start_date=start, end_date=end)
target_l = fetch_fred_series('DFEDTARL', start_date= start, end_date=end)  # Lower Target 추가


# New York Fed Markets Data API 자료 추출

from nyfed_api_all_rates import fetch_all_secured_rates
from nyfed_api_rate_volume import fetch_all_secured_rates_vol

df_all = fetch_all_secured_rates(start_date=start, end_date=end)
df_vol_all = fetch_all_secured_rates_vol(start_date=start, end_date=end)

df_all.rename(columns={'Date':'observation_date'}, inplace=True)
df_vol_all.rename(columns={'Date':'observation_date'}, inplace=True)

# tgcr, sofr, bgcr, sofrai, effr, obfr 등 선택가능


tgcr = df_all[df_all["Type"] == 'TGCR'].copy()
effr = df_all[df_all["Type"] == "EFFR"].copy()

sofr_vol = df_vol_all[df_vol_all["Type"] == 'SOFR'].copy()
tgcr_vol = df_vol_all[df_vol_all["Type"] == 'TGCR'].copy()
effr_vol = df_vol_all[df_vol_all["Type"] == "EFFR"].copy()

for i in [1,2]:

    # 시각화: SOFR, TGCR, EFFR Volume
    if i == 1:

        fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

        # 그림 41
        # 왼쪽:

        ax.plot(sofr_vol['observation_date'], sofr_vol['Volume'], label='SOFR', lw=2, color='black')
        ax.plot(tgcr_vol['observation_date'], tgcr_vol['Volume'], label='TGCR', lw=2, color='blue')
        ax.plot(effr_vol['observation_date'], effr_vol['Volume'], label='EFFR', lw=2, color='gray')

        ax.legend(loc='upper right', bbox_to_anchor=(1, 0.7))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.text(0, 1.00, '(10억 달러)',  ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
        ax.text(0, -0.15, '출처: FRED, NY FED', transform=ax.transAxes, fontsize=10)

        ax.grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.7)

    # 시각화:

    elif i == 2:

        # 그림 42
        # 시각화: SOFR,EFFR Rate
        fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

        ax.plot(effr['observation_date'], effr['Rate'], label='EFFR', lw=2, color='blue')
        ax.plot(iorb['observation_date'], iorb['IORB'], label='IORB', lw=2, color='black')
        #ax.plot(tgcr['observation_date'], tgcr['Rate'], label='TGCR', lw=2, color='green')
        ax.fill_between(effr["observation_date"], effr["Percentile1"], effr["Percentile99"],
                color="lightgray", alpha=0.8, label="1st–99th Percentile")
        ax.fill_between(effr["observation_date"], effr["Percentile25"], effr["Percentile75"],
                color="lightblue", alpha=0.9, label="25th–75th Percentile")

        ax.plot(target_u['observation_date'], target_u['DFEDTARU'],  color='black', ls='--', alpha=0.7, label='Target Range')
        ax.plot(target_l['observation_date'], target_l['DFEDTARL'], color='black', ls='--', alpha=0.7, label=None)


        ax.legend(loc='upper right', bbox_to_anchor=(1, 0.7))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.text(0, 1.00, '(%)', ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
        ax.text(0, -0.15, '출처: FRED, NY FED', transform=ax.transAxes, fontsize=10)

        ax.grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.7)


    # 저장 및 출력
    # python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

    plot_save(i=i)