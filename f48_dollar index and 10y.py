# [그림 48] 달러 인덱스와 10년물 미국채 수익률
# 같은 디렉토리에 필요한 파일

# plot_def.py
# fred_api.py               : FRED, api key required


import pandas as pd
import matplotlib.pyplot as plt

# 폰트 설정
from plot_def import *
set_fonts()

# 데이터 수집
start = '2024-01-01'
end = '2025-12-31'
from fred_api import fetch_fred_series

dgs10_df = fetch_fred_series('DGS10', start_date=start, end_date=end)
bdxy_df = fetch_fred_series('DTWEXBGS', start_date=start, end_date=end)


# 날짜 기준으로 두 데이터프레임 병합 (공통 날짜 기준)

merged_df = pd.merge(dgs10_df, bdxy_df, on='observation_date')

selected_terms_to_plot = ['observation_date', 'DGS10', 'DTWEXBGS']
merged_df = merged_df.dropna(subset=selected_terms_to_plot)[selected_terms_to_plot].copy()


# 그래프 그리기
fig, ax1 = plt.subplots(figsize=(9, 4.5),constrained_layout=True)

# 보조 y축: S&P 500
ax1.plot(merged_df['observation_date'], merged_df['DTWEXBGS'], label='달러인덱스(좌측)', color='blue', lw=2)


ax1.text(0, 1.00, '(연준달러인덱스, 2006=100)', ha='left', va='bottom', color='blue',
         fontsize=12, rotation=0, transform=ax1.transAxes)

ax1.tick_params(axis='y', labelcolor='b')
ax1.grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.7)

# DGS10 (10년물 금리)
ax2 = ax1.twinx()
ax2.plot(merged_df['observation_date'], merged_df['DGS10'], label='10년물 국채수익률(우측)', color='r', lw=1)

ax2.text(1, 1.00, '(10년물 국채 수익률, %)', ha='right', va='bottom', color='red',
         fontsize=12, rotation=0, transform=ax1.transAxes)

ax2.tick_params(axis='y', labelcolor='r')


# 제목 및 레이아웃

ax2.text(0.0, -0.15, "출처: Federal Reserve Bank of St. Louis",transform=ax1.transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')
ax1.legend(loc='upper left',bbox_to_anchor=(0.35, 0.9))
ax2.legend(loc='upper left',bbox_to_anchor=(0.35, 0.83))



# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()