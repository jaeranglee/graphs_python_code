# [그림 50] 국가별 미국채 보유액과 순매입액

# 같은 디렉토리에 필요한 파일

# plot_def.py
# treasury_tic_api.py               : treasury TIC data fetch


import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
import matplotlib.dates as mdates


from wallstreet.treasury_tic_api import download_tic_holdings_soup

# 한글 폰트 설정
from plot_def import *
set_fonts()


##---------------------------------------------
## Foreign US Treasury Holdings 데이터 가져오기
## requests, BeautifulSoup 이용
##
##---------------------------------------------


# Load the Excel file
file_path = "data/f_foreign_holdings1.xlsx"

# treasury_tic_api.py file function
excel_data = download_tic_holdings_soup(file_path=file_path, force_update=False)
df = excel_data.parse('Sheet1', skiprows=5)

# Filter for both target rows
target_countries = ['Grand Total', 'Of Which: Foreign Official', 'Japan', 'United Kingdom', 'China, Mainland']
target_rows = df[df['Country'].isin(target_countries)]
target_rows = target_rows.set_index('Country')

reshaped = target_rows.transpose()
reshaped.index.name = 'Date'
reshaped.reset_index(inplace=True)

reshaped.iloc[:, 1:] = reshaped.iloc[:, 1:].apply(pd.to_numeric)

# Convert date strings to datetime
reshaped['Date'] = pd.to_datetime(reshaped['Date'], format='%Y-%m')

# Custom labels for Korean legend
label_map = {
    'Grand Total': '총액',
    'Of Which: Foreign Official': '외국정부'
}


##---------------------------------------------
## Net US Long Term Securities Sales 데이터 가져오기
## Beautiful Soup 이용
##
##---------------------------------------------
## treasury_tic_api.py file function

file_path1 = "data/TIC_data.xlsx"
from treasury_tic_api import *

excel_data = download_tic_sales_soup(file_path=file_path1, force_update=False)

# Properly parse the data
df1 = excel_data.parse('Sheet1', skiprows=7)
df1 = df1.iloc[ 1:, 0:9]

# Clean up columns
df1['Country'] = df1['Country'].str.strip()

# Filter target countries
target_countries = ['Japan', 'United Kingdom', 'China, Mainland', 'Grand Total']
filtered_df = df1[df1['Country'].isin(target_countries)].copy()

# Convert types
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

# Filter from March 2024 onward
filtered_df = filtered_df[filtered_df['Date'] >= '2021-03-01']
filtered_df['Net U.S. Sales.1'] = pd.to_numeric(filtered_df['Net U.S. Sales.1'], errors='coerce')

# Change millions to billions

filtered_df['Net U.S. Sales.1'] = filtered_df['Net U.S. Sales.1']/1000

# Pivot for plotting
pivot_df = filtered_df.pivot(index='Date', columns='Country', values='Net U.S. Sales.1')
pivot_df = pivot_df.interpolate().dropna()

# Custom labels for Korean legend
label_map = {
    'Grand Total': '총액',
    'Of Which: Foreign Official': '외국정부',
    'China, Mainland': '중국',
    'Japan': '일본',
    'United Kingdom': '영국'
}


# Plotting Foreign US Treasuries Holds (왼쪽그림), Net US sales(오른쪽)
fig, ax = plt.subplots(1,2, figsize=(10, 5), constrained_layout=True )

# Plotting Foreign US Treasuries Holds (왼쪽그림)
for column in reshaped.columns[-2:]:  # Skip 'Date'  # '총액', '외국정부' 포함
    ax[0].fill_between(reshaped['Date'], reshaped[column]/1000, alpha=0.2)
    ax[0].set_ylim([3, 10])
    ax[0].plot(reshaped['Date'], reshaped[column]/1000, label=label_map.get(column, column), lw=2)


ax[0].text(0, 1.00, '(조 달러, 월말기준)', ha='left', va='bottom', color='blue',
                fontsize=12, rotation=0,transform=ax[0].transAxes)
ax[0].text(0.0, -0.15, "출처: 미국 재무부 Treasury International Capital (TIC) System",
                fontsize=11, verticalalignment='bottom', horizontalalignment='left',
                color='black', transform=ax[0].transAxes)

ax[0].legend(loc='upper left',bbox_to_anchor=(0.15, 0.95))

# Plotting Net US sales(오른쪽)
for country in target_countries:
    lw = 3 if country == 'China, Mainland' else 1.5  # thicker line for China
    color ='red' if country == 'China, Mainland' else None
    ax[1].plot(pivot_df.index, pivot_df[country], label=label_map.get(country, country),
               lw=lw, color=color)

# Add horizontal line at y = 0
    ax[1].axhline(y=0, color='gray', linestyle='--', linewidth=1)


ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax[1].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

ax[1].text(0, 1.00, '(십억 달러, 매월기준)', ha='left', va='bottom', color='blue',
                fontsize=12, rotation=0,transform=ax[1].transAxes)
ax[1].legend(loc='upper left',bbox_to_anchor=(0.5, 0.95))

# save plot file and show on screen

plot_save()
