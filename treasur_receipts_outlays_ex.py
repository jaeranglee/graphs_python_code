# %% [markdown]
# Treasury TIC Data Fetch
# %%
#%config InlineBackend.close_figures = False
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from plot_def import *
set_fonts()

start = '2020-01-01'
end =' 2025-12-31'
from treasury_receipts_outlays import *
df = treasury_receipts_outlays_csv(start_date=start, end_date=end)

cols = [df.columns]
print(cols)

# convert in Million Dollars
df['Current Month Receipt or Outlay Amount'] =  df['Current Month Receipt or Outlay Amount']/1e9

labels=['Interest on Treasury Debt Securities (Gross)',
        'Department of Defense--Military Programs',
        'Customs Duties']


df0 = df[df['Classification Description'].isin(['Interest on Treasury Debt Securities (Gross)'])]
df1 = df[df['Classification Description'].isin(['Department of Defense--Military Programs'])]
df2 = df[df['Classification Description'].isin(['Customs Duties'])]

fig, ax = plt.subplots(figsize=(8, 4.5),constrained_layout=True)

ax.plot(df0['observation_date'], df0['Current Month Receipt or Outlay Amount'], label=labels[0], color='red', lw=2)
ax.plot(df2['observation_date'], df2['Current Month Receipt or Outlay Amount'], label=labels[2], color='blue', lw=2)


# Add horizontal line at y = 2
#ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)

ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

ax.legend(loc='upper left',bbox_to_anchor=(0.0, 1))

# 현재 날짜 가져오기
from datetime import datetime
access_date = datetime.today().strftime('%Y-%m-%d')

ax.text(0, 1.00, '(십억 달러)', ha='left', va='bottom', transform=ax.transAxes, fontsize=12, color='black')
ax.text(0, -0.15, f'출처: Treasury Fiscal Data, 자료 작성일: {access_date}', transform=ax.transAxes, fontsize=10)
ax.grid(True, linestyle='--', color='gray', alpha=0.3)

plot_save()
