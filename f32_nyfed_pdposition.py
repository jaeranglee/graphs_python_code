# [그림 32] 프라이머리 딜러 국채 포지션

# 같은 디렉토리에 있어야 하는 함수 파일

# fred_api.py
# nyfed_api.py
# plot_def.py


import pandas as pd
import matplotlib.pyplot as plt


# 폰트 설정

from plot_def import *
set_fonts()


# New York Fed Markets Data API 에서 자료 추출


# PD Position all timeseries securities list description download
# run it for just one time to check the list

from nyfed_api import fetch_series_list

#ny fed의 pd positions data를
#'data/TimesSeries.csv'로 저장

des = fetch_series_list()
des.to_csv('data/nyfed_pdposition.csv')


from nyfed_api import fetch_pdpositions
fetch_pdpositions()

#'data/TimesSeries.csv'를 dataframe으로 read

df = pd.read_csv('data/TimeSeries.csv')
df["As Of Date"] = pd.to_datetime(df["As Of Date"])
df['Value (millions)'] = pd.to_numeric(df['Value (millions)'], errors='coerce')

df['Value (millions)'] = df['Value (millions)'] / 1e3
df = df.set_index('As Of Date')



# PD Bills position
bills = df[df["Time Series"]=="PDPOSGS-B"]


notes11 = df[df["Time Series"]=="PDPOSGSC-G11L21"]


notes2 = df[df["Time Series"]=="PDPOSGSC-L2"]
notes23 = df[df["Time Series"]=="PDPOSGSC-G2L3"]
notes36 = df[df["Time Series"]=="PDPOSGSC-G3L6"]
notes67 = df[df["Time Series"]=="PDPOSGSC-G6L7"]
notes711 = df[df["Time Series"]=="PDPOSGSC-G7L11"]

#PD Bonds Position
notes10 = df[df["Time Series"]=="PDPOSGSC-G11"]

#PD Notes Position
notes = notes2 + notes23 + notes36 + notes67 + notes711

#PD Bonds Position
bonds = df[df["Time Series"]=="PDPOSGSC-G21"] + notes11

#PD total Treasuries Position
treasuries = df[df["Time Series"]=="PDPOSGST-TOT"]

cb = df[df["Time Series"]=="PDPOSCS-TOT"]
agencies = df[df["Time Series"]=="PDPOSFGS-TOT"]



# 그래프 그리기

fig, ax = plt.subplots(figsize=(8, 4.5),constrained_layout=True)


ax.plot(treasuries.index, treasuries["Value (millions)"], label="Total Treasuries", color="blue", lw=2)
ax.plot(bills.index, bills["Value (millions)"], label="Bills", color="red", lw=2)
ax.plot(notes.index, notes["Value (millions)"], label="Notes", color="orange", lw=2)

# Bond position 데이터
ax.plot(bonds.index, bonds["Value (millions)"], label="Bonds", color="green", lw=2)
ax.plot(notes10.index, notes10["Value (millions)"], label=None, color="green", lw=2)


ax.text(0, 1.00, '(십억 달러)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)

ax.text(0.0, -0.15, "출처: NY Fed, Primary Dealer Statistics", transform=ax.transAxes,
         fontsize=12, verticalalignment='bottom', horizontalalignment='left', color='black')
ax.legend()
ax.grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.4)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()