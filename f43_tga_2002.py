# [그림 43] 재무부 TGA 잔고 장기추이

# 같은 디렉토리에 필요한 파일

# plot_def.py
# fred_api.py               : FRED, api key required

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set font depending on the platform
from plot_def import set_fonts
set_fonts()

start = '2002-01-01'
end = '2099-12-31'

# Fetch series

from fred_api import fetch_fred_series

# D2WLTGAL (TGA Wednesday, NY FED)
df = fetch_fred_series('D2WLTGAL',start_date=start, end_date=end)

df_filtered = df.copy()

#---------------------
# Identify the specific date
highlight_date = '2025-03-19'
# Convert date format to match DataFrame
highlight_date = pd.to_datetime(highlight_date)

# Find the corresponding data point in dff

highlight_point = df_filtered[df_filtered['observation_date'] == highlight_date]


# 그래프 그리기

fig, ax = plt.subplots(figsize=(9, 4.5),constrained_layout=True)
ax.plot(df_filtered['observation_date'], df_filtered['D2WLTGAL']/1000, color='blue', lw=2)


# Add horizontal line at y = 2
ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)

ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))


# USREC 기준으로 recession 음영 처리 (확장기: 0, 침체기: 1)

from plot_def import *

recession_periods = nber_recesssion(start=start, end=end)

# 두 그래프에 음영 처리
for peak, trough in recession_periods:
    ax.axvspan(peak, trough, color='gray', alpha=0.3)



ax.text(0, 1.00, '(십억 달러)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)
plt.grid(False)

ax.text(0.0, -0.15, "출처: FRED; 수요일 뉴욕연준 기준, 음영구간은 recession", transform=ax.transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')

# plot file save and show on screen
plot_save()