# [그림 53] 전세계 금 보유량, 국가별 보유량

# 같은 디렉토리에 필요한 파일

# plot_def.py
# imf_api.py        : IMF Data, no api key required

import matplotlib.dates as mdates
import platform

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# 한글 폰트 설정
# Set font depending on the platform
from plot_def import *
set_fonts()

start = "1999-01-01"
end = "2025-06-01"


# imf_api 가져오기
from imf_api import *

indicator_id = ['RGV_REVS', 'RGOLDMV_REVS', 'TRGMV_REVS']

country_id = ['G001','USA','DEU','ITA', 'FRA',
              'CHN', 'CHE','IND','JPN','TUR']
unit_id = ['FTO', 'XDR']


# world total gold volume
df_world_gold = fetch_gold_data(country_id[0], indicator_id[0],
    unit_id[0], start_period=start, end_period=end)
df_world_gold = df_world_gold.rename(columns={"OBS_VALUE":"World Holdings"}).copy()

# world total gold value in SDR
df_world_gold_value = (fetch_gold_data(country_id[0], indicator_id[1],
    unit_id[1], start_period=start, end_period=end)
        .rename(columns={"OBS_VALUE":"World Gold Values"}).copy())

# world total reserves in SDR
df_world_reserves = (fetch_gold_data(country_id[0], indicator_id[2],
    unit_id[1], start_period=start, end_period=end)
        .rename(columns={"OBS_VALUE":"World Reserves"}).copy())

df_merged = pd.merge(df_world_gold_value, df_world_reserves, on="Date", how="inner")
df_merged['share'] = df_merged['World Gold Values'] / df_merged['World Reserves'] * 100

# List of country codes and labels
countries = ['DEU', 'CHN', 'IND', 'JPN', 'TUR']
labels = ['독일', '중국', '인도', '일본', '터키']
colors = ['blue', 'red', 'orange', 'black', 'green']

# countries' gold holdings volume data fetch

all_data = {}
for country in countries:
    df = fetch_gold_data(country, indicator_id[0],
        unit_id[0], start_period=start, end_period=end)

    df.rename(columns={df.columns[-1]: "value"}, inplace=True)
    all_data[country] = df.set_index("Date")['value'].to_dict()
df_pivot = pd.DataFrame(all_data)


# 시각화
fig, ax = plt.subplots(1,2, figsize=(9, 4.5), constrained_layout=True)

# Gold volume, and Reserve share

ax_left = ax[0]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(df_world_gold['Date'], df_world_gold['World Holdings']/1e6, label='전세계 금 보유량(좌축)', lw=2, color='red')
ax_right.plot(df_merged['Date'], df_merged['share'], label='금 보유액/외환보유액(우축)', lw=2, color='blue')

# 과학적 표기 (1e6 등) 방지
ax[0].ticklabel_format(style='plain', axis='y')

ax_left.legend(loc='upper left',bbox_to_anchor=(0, 1.0))
ax_right.legend(loc='upper left',bbox_to_anchor=(0, 0.92))
ax_left.yaxis.label.set_visible(True)
ax_left.text(0, 1.00, '(백만 troy oz)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)
ax_right.text(1, 1.00, '(%)', ha='right', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)

ax[0].xaxis.set_major_locator(mdates.YearLocator(4))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[0].text(0.0, -0.15, "출처: IFS, IMF", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(True, linestyle='--', which='major', alpha=0.5, axis='y')


ax_left1 = ax[1]
ax_right1 = ax_left1.twinx()  # Create right-side y-axis



# 독일(최축)

ax_left1.plot(df_pivot.index, df_pivot['DEU']/1e6, label='독일(좌축)', lw=2, color='blue')

# 다른 나라(우축)
# Plot each country with its corresponding color

for country, label, color in zip(countries[1:], labels[1:], colors[1:]):
    ax_right1.plot(df_pivot.index, df_pivot[country]/1e6, label=label+"(우측)", lw=2, color=color)


# 과학적 표기 (1e6 등) 방지
ax_left1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:,.0f}'))

ax[1].xaxis.set_major_locator(mdates.YearLocator(4))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax_left1.legend(loc='upper left',bbox_to_anchor=(0.2, 0.99))
ax_right1.legend(loc='upper left',bbox_to_anchor=(0.63, 0.7))


ax[1].text(0, 1.00, '(백만 troy oz)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(1, 1.0, '(백만 troy oz)', ha='right', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[1].transAxes)

ax[1].text(0.0, -0.15, "출처: IFS, IMF", transform=ax[1].transAxes, fontsize=10, ha='left')

ax[1].grid(True, linestyle='--', which='major', alpha=0.5, axis='y')




# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()