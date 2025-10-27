# %% [markdown]
# # [그림 13] 정책금리 기대확률(2025년 9월 17일 FOMC)
# 이용되는 data는 CME Fed Watch 사이트에서 csv 파일로 다운로드한 것이다.
# CME는 무료로 공개된 Open API는 없다. Fed Watch 사이트에 가면 일부 자료를 화면으로 보여주거나
# csv 파일로 공개한다.
# https://www.cmegroup.com/ko/markets/interest-rates/cme-fedwatch-tool.html
# 이중에 historical 쪽 자료를 받은 것이다.
# ## required file
#   - plot_def.py
# ## required packages
# ```python
# pip install datetime
# ```
# %%
import matplotlib.dates as mdates
from datetime import datetime

# 한글 폰트 설정
from plot_def import *
set_fonts()

# 'data/FedMeeting_20250917.csv' CME에서 받은 파일의 경로와 이름을 넣어준다.
df_pro = pd.read_csv('data/FedMeeting_20250917.csv')
df_pro['Date'] = pd.to_datetime(df_pro['Date'])

# 현재 날짜 가져오기
access_date = datetime.today().strftime('%Y-%m-%d')

# 시각화
fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)


ax.plot(df_pro['Date'], df_pro['(375-400)']*100, label='50bp 인하(3.75-4.00%)', ls='--', lw=2, color='black')
ax.plot(df_pro['Date'], df_pro['(400-425)']*100, label='25bp 인하(4.00-4.25%)', lw=2, color='blue')
ax.plot(df_pro['Date'], df_pro['(425-450)']*100, label='동결(4.25-4.5%)', lw=1, ls=":", color='blue')


ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

ax.text(0, 1.00, '(%)', ha='left', va='bottom',transform=ax.transAxes, fontsize=12, color='black')
ax.legend(loc='upper left',bbox_to_anchor=(0.0, 1))

ax.text(0, -0.15, f'출처: CME FedWatch, 자료 작성일: {access_date}', transform=ax.transAxes, fontsize=10)
ax.grid(True, linestyle='--', color='gray', alpha=0.3)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

from plot_def import plot_save
plot_save()