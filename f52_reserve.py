# [그림 52] 전세계 외환보유액의 주요 통화별 구성

# 같은 디렉토리에 필요한 파일

# plot_def.py
# imf_api.py        : IMF Data, no api key required



import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform
from matplotlib.ticker import FuncFormatter

import matplotlib.ticker as mtick
import numpy as np

# 한글 폰트 설정

# Set font depending on the platform
from plot_def import *
set_fonts()

# fetch data from IMF Data
from imf_api import *

currencies = {
    "USD": "CI_USD",
    "EUR": "CI_EUR",
    "JPY": "CI_JPY",
    "GBP": "CI_GBP",
    "CNY": "CI_CNY"
}

# 기준 날짜 설정
start = "1999-Q1"
end = "2025-Q1"


# 통합 DataFrame 생성
dfs_usd = []
dfs_share = []

for name, code in currencies.items():
    df_usd = fetch_cofer_data(code, "NV_USD", start_period=start, end_period=end)
    df_usd.rename(columns={"NV_USD": name}, inplace=True)
    dfs_usd.append(df_usd.set_index("Date"))

    df_share = fetch_cofer_data(code, "SHRO_PT", start_period=start, end_period=end)
    df_share.rename(columns={"SHRO_PT": name}, inplace=True)
    dfs_share.append(df_share.set_index("Date"))

# 날짜 기준으로 병합
df_usd_all = pd.concat(dfs_usd, axis=1)
df_share_all = pd.concat(dfs_share, axis=1)


# 부족 분을 기타로 계산
df_with_other = df_share_all.copy()

df_with_other['기타'] = 100 - df_with_other.sum(axis=1)


### 시각화


# Plot
# 왼쪽: 달러 쉐어 그래프:

df_with_other.index = pd.to_datetime(df_with_other.index)


fig, ax = plt.subplots( 1,2,figsize=(9, 4.5), constrained_layout=True, sharex=False, sharey=False)

df_with_other.plot.area(ax=ax[0], stacked=True, alpha=0.6)

# 과학적 표기 (1e6 등) 방지
ax[0].ticklabel_format(style='plain', axis='y')
ax[0].set_xlabel("")

# 범례
ax[0].legend(loc='upper left',bbox_to_anchor=(0, 0.8))

# 단위 표시 및 출처
ax[0].text(0, 1.00, '(구성비율, %)', ha='left', va='bottom', color='blue',
         fontsize=12, rotation=0, transform=ax[0].transAxes)

ax[0].text(0.0, -0.15, "출처: COFER, IMF", transform=ax[0].transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')



# Value (오른쪽 축) : # 달러 규모 그래프
# 모든 통화 열을 조 달러 단위로 나누기
for curr in currencies.keys():

    df_usd_all[curr] = (df_usd_all[curr] / 1e12).copy()
    ax[1].plot(df_usd_all.index, df_usd_all[curr], label=curr, lw=2)



# sharex=True이므로, 대표로 ax[1]의 X축 눈금을 설정하면 모두에게 적용됩니다.
ax[1].xaxis.set_major_locator(mdates.YearLocator(5)) # 4년마다 큰 눈금
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y')) # '2024' 형식으로 표시


# 단위 표시 및 출처
ax[1].text(0, 1.00, '(금액, 조 달러)', ha='left', va='bottom', color='blue',
         fontsize=12, rotation=0, transform=ax[1].transAxes)

# 과학적 표기 (1e6 등) 방지
ax[1].ticklabel_format(style='plain', axis='y')

# 백만 단위로 변환된 값 표시: 예 → 6, 12, 45
ax[1].yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}"))
ax[1].text(0.0, -0.15, "출처: COFER, IMF", transform=ax[1].transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')

# 범례 (하나만 표시하거나 합칠 수도 있음)
ax[1].legend(loc='upper left')
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()