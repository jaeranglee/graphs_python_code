# %% [markdown]
# # [그림 16] 직전 2개월 NFP 수정치
# ## required file
#   - plot_def.py
#   - fred_api.py
#   - nfp_revision.py : NPF 수정 데이터를 불러와서 csv 파일로 저장
#   - "data/nfp_revisions.csv": 위 코드로 불러온 데이터
# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy.dialects.mssql.information_schema import columns

from plot_def import set_fonts
set_fonts()

# Load the data from the CSV file
df = pd.read_csv("data/nfp_revisions.csv", index_col='month', parse_dates=True)


# Apply the conditional logic to create a new column with the value to plot
df['plot_value'] = np.where(
    df['vintage_completeness'] == '3 vintage(s)',  # Condition 1
    df['3rd - 1st'],                               # Value if Condition 1 is true
    np.where(
        df['vintage_completeness'] == '2 vintage(s)', # Condition 2
        df['2nd - 1st'],                              # Value if Condition 2 is true
        np.nan                                        # Value if neither condition is true
    )
)

# Filter out rows that don't have a value to plot
plot_data = df.dropna(subset=['plot_value'])

df['revisions'] = df['revision1']+df['revision2']

plot_data2 = df[['1st_vintage_key', 'revision1', 'revision2', 'revisions']]



plot_data2.index = pd.to_datetime(plot_data2['1st_vintage_key'])
plot_data2 = plot_data2.drop(columns=['1st_vintage_key'])


bar_width = 29.5
plot_data2 = plot_data2.reset_index()
plot_data2 = plot_data2.rename(columns={'1st_vintage_key': 'date'}).copy()

plot_data2 = plot_data2[plot_data2['date']>='2007-01-01']

# Base colors

base_colors = np.where(
    (plot_data2['date'] == '2023-11-03') | (plot_data2['date'] == '2025-08-01'),
    'black',
    np.where(plot_data2['revisions'] >= 0, 'blue', 'black')
)


# 월별 고용 발표일(Vintage Date)에 전월과 전전월 실적 수정 폭(인원수) 그려줌
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)


# Plot revisions
ax.bar(plot_data2['date'], plot_data2['revisions'], width=bar_width, color=base_colors)

ax.text(0, 1.00, '(천명)', ha='left', va='bottom', color='black',
                fontsize=12, rotation=0, transform=ax.transAxes)

# Add a grid
ax.grid(True, which='major', linestyle='--', linewidth='0.5', color='grey', alpha=0.3)

# 0에서 가로줄
ax.axhline(0, color='black', linewidth=0.8, linestyle='--')


# 출처 표시
ax.text(0.0, -0.15, "출처: BLS, ALFRED, FRED",
         fontsize=12, verticalalignment='bottom', horizontalalignment='left', color='black', transform=ax.transAxes)


# 그림파일 저장, 화면출력

from plot_def import plot_save
plot_save()