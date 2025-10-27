# %% [markdown]
# # [그림 30] 미국 연방정부 국채 잔액
# ## 같은 디렉토리에 필요한 file
#   - plot_def.py : 한글폰트 추가, 그래프 저장
#   - treasury_api.py : Treasury Fiscal Data에서 받아놓은 json file을 parsing 하는 파일
# ## data 디렉토리에 필요한 파일
#   - Treasury Fiscal Data에서 받아놓은 json file
#       - data/MSPD_SumSecty_20010131_20250731.json
#   - 각자 직접 홈페이지에서 다운로드하기를 추천
#   - api fetch 시간이 너무 오래 걸림
# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates


# Set font depending on the platform
from plot_def import *
set_fonts()


'''
# 데이터 요청
url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/public_debt_transactions"

params = {
    'filter': 'record_date:gte:2020-01-01,record_date:lte:2025-07-30,security_market:eq:Marketable',
    'fields': 'record_date,transaction_type,security_market,security_type,transaction_today_amt,transaction_mtd_amt,transaction_fytd_amt',
    'page[size]': 1000,
    'page[number]': 1
}


all_data = []

while True:
    response = requests.get(url, params=params)
    print(f"Fetching page {params['page[number]']} - Status code: {response.status_code}")
    if response.status_code != 200:
        break

    page_data = response.json().get("data", [])
    if not page_data:
        break

    all_data.extend(page_data)
    params['page[number]'] += 1

df = pd.DataFrame(all_data)

print(df.head())
df.to_csv("data/marketable_debt_transactions.csv", index=False)
print(f"Total Marketable records fetched: {len(df)}")

'''


from treasury_api import *

#-----------
# Public Debt Outstanding, Monthly Statement of the Public Debt
# 받아놓은 jason file에서

start="1990-01-01"
end = "2025-12-31"
file_path1="data/MSPD_SumSecty_20010131_20250731.json"

outstanding = fetch_debt_outstanding_json(start_date=start, end_date=end, json_path=file_path1)
outstanding= outstanding.reset_index()

result = outstanding.groupby(['Record Date'])["Amount"].sum().reset_index()

print(result)
# 국채 종류별 발행 잔액 그림

outstanding= outstanding.set_index('Record Date')

# 시각화
fig, ax = plt.subplots(figsize=(8,4.5), constrained_layout=True)
# unique classes
classes = outstanding['Class'].unique()

# build blue/black palette
colors = sns.color_palette("Blues", n_colors=len(classes))
colors[0] = 'black'  # make first one black for contrast

# numeric dash patterns
dash_patterns = [
    (),            # solid
    (5, 2),        # dashed
    (3, 1, 1, 1),  # dash-dot
    (1, 1)         # dotted
]

# assign to each class
dashes = {cls: dash_patterns[i % len(dash_patterns)] for i, cls in enumerate(classes)}
palette = {cls: colors[i % len(colors)] for i, cls in enumerate(classes)}

sns.lineplot(
    ax=ax,
    data=outstanding,
    x=outstanding.index,
    y='Amount',
    hue='Class',
    style='Class',
    palette=palette,
    dashes=dashes,      # numeric tuples now ✅
    lw=2,
    errorbar=None,      # replaces deprecated ci=None
    legend='brief'
)

ax.legend(title=None, loc='best')


ax.text(0, 1.00, '(조 달러)', ha='left', va='bottom', color='black',
                fontsize=12, rotation=0, transform=ax.transAxes)

ax.xaxis.set_major_locator(mdates.YearLocator(5))  # 1년 간격으로 눈금 표시
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  # 연도만 표시
#fig.autofmt_xdate()  # x축 날짜 자동 회전 및 정렬


# Add a grid and ensure a tight layout
ax.grid(True, which='major', linestyle='--', linewidth='0.5', color='grey')


#ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
#ax.set_title('월별 발행액', size=16)
ax.set_xlabel('')
ax.set_ylabel('')
ax.text(0.0, -0.15, "Data: Monthly Statement of the Public Debt, U.S. Treasury ",
         fontsize=12, verticalalignment='bottom', horizontalalignment='left', color='black', transform=ax.transAxes)




# Show ticks on both sides, inside the box
ax.yaxis.set_ticks_position('both')
ax.tick_params(axis='y', direction='in', length=6)
#ax.set_ylim(-800,800)

# 그림 파일 저장

plot_save()