# NFP와 ADP 월별 증가인원, JOLT 구인건수

# 이용되는 API data fetch function

# from fred_api import fetch_fred_series
# from plot_def import set_fonts
# from plot_def import plot_save



from fred_api import fetch_fred_series
import pandas as pd

start = '2022-07-01'
end = '2025-12-31'

# Total Nonfarm Private Payroll Employment (ADPWNUSNERSA), person, sa, weekly

# All Employees, Total Nonfarm (PAYEMS), thousand person, sa, monthly
# Job Openings: Total Nonfarm (JTSJOL)

# Initial Claims (ICSA), number, sa
# Continued Claims (Insured Unemployment) (CCSA), number, sa


series_ids ={

    "NFP": 'PAYEMS',
    'ADP': 'ADPWNUSNERSA',
    'Job Openings': 'JTSJOL'
}

# 모든 데이터 가져오기
# 이름을 Fred series_id를 공식명칙으로 변환

all_data = {}
for term, sid in series_ids.items():
    df = fetch_fred_series(sid, start_date=start, end_date=end)
    df.rename(columns={df.columns[-1]: "value"}, inplace=True)

    # Series로 변환
    s = df.set_index("observation_date")["value"]


    # Weekly or Daily to Monthly
    s = s.resample("ME").mean()
    s.index = s.index.to_period("M").to_timestamp(how="start")  # 월초로 통일

    all_data[term] = s


# 병합
df_all = pd.DataFrame(all_data)

series_names = list(series_ids.keys())

# ADP 취업자수 천명 단위로 전환
df_all[series_names[1]]=df_all[series_names[1]]/1000

# NFP, ADP를 전월 대비 증감으로 변환
for s in series_names[:2]:
    df_all[s] = df_all[s].diff(periods=1).copy()


import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 한글 폰트 설정
from plot_def import set_fonts
set_fonts()

colors =['red','blue']

# 강조할 달
nfp_highlight_month = "2023-09"
nfp_highlight_month = pd.to_datetime(nfp_highlight_month)

jolt_highlight_month = "2023-08"
jolt_highlight_month = pd.to_datetime(jolt_highlight_month)

# ADP 색상 지정 (9월만 연한색)
colors_adp = [
    "lightblue" if d.month == 8 and d.year == nfp_highlight_month.year else colors[1]
    for d in df_all.index
]

# NFP 색상 지정 (9월만 연한색)
colors_nfp = [
    "orange" if d.month == 9 and d.year == nfp_highlight_month.year else colors[0]
    for d in df_all.index
]

# JOLT 색상 지정 (8월만 파란색, 나머지는 기본색)
colors_jolt = [
    "blue" if d.month == 9 and d.year == jolt_highlight_month.year else colors[0]
    for d in df_all.index
]



# plot
# NFP, ADP 전월대비 증감

fig, ax = plt.subplots(1,2, figsize=(8, 4.5), constrained_layout=True)

# 막대 폭 (timedelta로 설정)
#bar_offset = pd.Timedelta(days=10)

# x축 위치 (DatetimeIndex → numeric 변환 가능하지만, timedelta offset도 가능)
#x = df_all.index

# x축을 숫자형으로 변환
x = mdates.date2num(df_all.index.to_pydatetime())

# 막대 폭 (숫자 단위: 일 = 1.0)
bar_width = 20        # 막대 폭 (약 20일)
offset = bar_width/2  # 좌우로 반만큼 이동

# ---- (1) NFP, ADP side-by-side ----

ax[0].bar(x - offset,
      df_all[series_names[0]],   # NFP
      width=offset,
      label=series_names[0],
      color=colors_nfp)

ax[0].bar(x + offset,
      df_all[series_names[1]],   # ADP
      width=offset,
      label=series_names[1],
      color=colors_adp)

ax[0].xaxis_date()
ax[0].xaxis.set_major_locator(mdates.YearLocator())
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[0].legend(loc='upper left',bbox_to_anchor=(0.3, 1.0))
ax[0].legend(loc='upper left',bbox_to_anchor=(0.3, 0.94))
ax[0].yaxis.label.set_visible(True)

ax[0].text(0, 1.00, '(천명)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax[0].transAxes)

ax[0].text(0.0, -0.15, "출처: FRED, 연한색은 2023년 9월", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.3)

# plot
# JOLT 전월대비 증감

ax[1].bar(df_all.index,
       df_all[series_names[2]],
       width=20,
       label=series_names[2],
       color=colors_jolt)

ax[1].xaxis_date()
ax[1].xaxis.set_major_locator(mdates.YearLocator())
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# 단위 표시 및 출처
ax[1].legend(loc='upper left', bbox_to_anchor=(0.3, 1.0))
ax[1].legend(loc='upper left', bbox_to_anchor=(0.3, 0.94))
ax[1].yaxis.label.set_visible(True)

ax[1].text(0, 1.00, '(천명)', ha='left', va='bottom', color='black',
        fontsize=12, rotation=0, transform=ax[1].transAxes)

ax[1].text(0.0, -0.15, "출처: FRED, 파란색은 2023년 8월", transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.3)

# 그림파일로 저장

from plot_def import plot_save
plot_save()