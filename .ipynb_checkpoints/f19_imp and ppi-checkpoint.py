# %% [markdown]
# # [그림 18] 수입물가와 생산자물가
# ## required file
#   - plot_def.py
#   - fred_api.py
# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# 한글 폰트 설정
from plot_def import *
set_fonts()

start='2020-01-01'
end='2025-12-31'

# Fetch series

from fred_api import *

# Fetch series
# Import Price Index (End Use): All Commodities (IR)
df0 = fetch_fred_series('IR', start_date=start, end_date=end)

# Producer Price Index by Commodity: All Commodities (PPIACO)
df1 = fetch_fred_series('PPIACO', start_date=start, end_date=end)

df= pd.merge(df0, df1, on='observation_date', how='inner').copy()

#---------------------

# Calculate YoY inflation rate

df['YoY_IMP'] = df['IR'].pct_change(periods=12, fill_method=None) * 100
df['YoY_PPI'] = df['PPIACO'].pct_change(periods=12, fill_method=None) * 100

df['MoM_IMP'] = df['IR'].pct_change(fill_method=None) * 100
df['MoM_PPI'] = df['PPIACO'].pct_change(fill_method=None) * 100

df = df[(df['observation_date'] >= '2021-01-01')].copy()

df['YoY_IMP'] = pd.to_numeric(df['YoY_IMP'], errors='coerce').copy()
df['YoY_PPI'] = pd.to_numeric(df['YoY_PPI'], errors='coerce').copy()
df['MoM_IMP'] = pd.to_numeric(df['MoM_IMP'], errors='coerce').copy()
df['MoM_PPI'] = pd.to_numeric(df['MoM_PPI'], errors='coerce').copy()


# Identify the specific date
highlight_date = '2024-08'

# Convert date format to match DataFrame
highlight_date = pd.to_datetime(highlight_date)

# Find the corresponding data point in dff

highlight_point_imp_yoy = df[df['observation_date'] == highlight_date]
highlight_point_ppi_yoy = df[df['observation_date'] == highlight_date]

highlight_point_imp_mom = df[df['observation_date'] == highlight_date]
highlight_point_ppi_mom = df[df['observation_date'] == highlight_date]


# Plot
# 전년동월비 (왼쪽그림), 전월비(오른쪽)
fig, ax = plt.subplots(1,2, figsize=(9, 4.5), constrained_layout=True )

ax[0].plot(df['observation_date'], df['YoY_IMP'], lw=2, color='blue')
ax[0].plot(df['observation_date'], df['YoY_PPI'], lw=2, color='black')

# Add horizontal line at y = 2
ax[0].axhline(y=0, color='gray', linestyle='--', linewidth=1)

# Plot the highlighted point with a larger marker
ax[0].scatter(highlight_point_imp_yoy['observation_date'], highlight_point_imp_yoy['YoY_IMP'],
              color='blue', marker='o', s=100, linewidth=2, label="2024년 8월 수입물가")
ax[0].scatter(highlight_point_ppi_yoy['observation_date'], highlight_point_ppi_yoy['YoY_PPI'],
           color='black', marker='x', s=100, linewidth=2, label="2024년 8월 생산자물가")

# Add a legend for clarity
ax[0].legend()


# Formatting

ax[0].text(0, 1.00, '(%, 전년동월대비)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)

# Turn off scientific notation on y-axis
ax[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
# Set major ticks to years
ax[0].xaxis.set_major_locator(mdates.YearLocator())  # Every year

ax[0].grid(False)

ax[0].text(0.0, -0.15, "출처: BLS, FRED", transform=ax[0].transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')


# Plotting the inflation rate 전월비 (오른쪽)

ax[1].plot(df['observation_date'], df['MoM_IMP'], lw=2, color='blue')
ax[1].plot(df['observation_date'], df['MoM_PPI'], lw=2, color='black')

ax[1].scatter(highlight_point_imp_mom['observation_date'], highlight_point_imp_mom['MoM_IMP'],
           color='blue', marker='o', s=100, linewidth=2, label="2024년 8월 수입물가")
ax[1].scatter(highlight_point_ppi_mom['observation_date'], highlight_point_ppi_mom['MoM_PPI'],
           color='black', marker='x', s=100, linewidth=2, label="2024년 8월 생산자물가")

# Add horizontal line at y = 0
ax[1].axhline(y=0, color='gray', linestyle='--', linewidth=1)

# Set major ticks to years
ax[1].xaxis.set_major_locator(mdates.YearLocator())  # Every year

# 단위 표시
ax[1].text(0, 1.00, '(%, 전월대비)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
# 출처표시
ax[1].text(0.0, -0.15, "출처: BLS, FRED", transform=ax[1].transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')


plt.grid(False)
plt.legend()


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()