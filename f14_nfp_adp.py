#[그림 14] 월별 구인건수와 고용 증감

# 사용하는 함수 파일

# fred_api.py
# plot_def.py




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
    'ADP': 'ADPMNUSNERSA',
    'Job Openings': 'JTSJOL'
}

# 데이터 가져오기
# Fred series_id를 일반 명칭으로 변환

all_data = {}
for term, sid in series_ids.items():
    df_temp = fetch_fred_series(sid, start_date=start, end_date=end)
    df_temp.rename(columns={df_temp.columns[-1]: "value"}, inplace=True)

    # Series로 변환
    s = df_temp.set_index("observation_date")["value"]


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


# NFP 색상 지정 (9월만 red)
colors_nfp = [
    "red" if d.month == 9 and d.year == nfp_highlight_month.year else colors[1]
    for d in df_all.index
]

# ADP 색상 지정 (9월만 red)
colors_adp = [
    "red" if d.month == 9 and d.year == nfp_highlight_month.year else colors[1]
    for d in df_all.index
]


# JOLT 색상 지정 (8월만 파란색, 나머지는 red)
colors_jolt = [
    "blue" if d.month == 8 and d.year == jolt_highlight_month.year else colors[0]
    for d in df_all.index
]



# plot 정의

fig, ax = plt.subplots(1,3, figsize=(8, 4.5), constrained_layout=True)



# x축
x = df_all.index


# plot
# ---- JOLT 건수

ax[0].bar(df_all.index,
       df_all[series_names[2]],
       width=20,
       label=series_names[2],
       color=colors_jolt)

# ---- ADP 전월대비 증감

ax[1].bar(x, df_all[series_names[1]], width=20, label=series_names[1], color=colors_adp)

# ---- NFP 전월대비 증감
ax[2].bar(x, df_all[series_names[0]], width=20, label=series_names[0], color=colors_nfp)


for i in [0,1,2]:
    ax[i].xaxis_date()
    ax[i].xaxis.set_major_locator(mdates.YearLocator())
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # 단위 표시 및 출처
    ax[i].legend(loc='upper left',bbox_to_anchor=(0.3, 1.0))
    ax[i].yaxis.label.set_visible(True)
    ax[i].text(0, 1.00, '(천명)', ha='left', va='bottom', color='black',
             fontsize=12, rotation=0, transform=ax[i].transAxes)

ax[0].text(0.0, -0.15, "출처: FRED, 파란색은 2023년 8월", transform=ax[0].transAxes, fontsize=10, ha='left')
ax[1].text(0.0, -0.15, "붉은색은 2023년 9월", transform=ax[1].transAxes, fontsize=10, ha='left')
ax[2].text(0.0, -0.15, "붉은색은 2023년 9월", transform=ax[2].transAxes, fontsize=10, ha='left')


# 그림 파일로 저장

from plot_def import plot_save
plot_save()