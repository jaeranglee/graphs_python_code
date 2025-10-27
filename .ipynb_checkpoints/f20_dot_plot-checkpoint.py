# %% [markdown]
# # [그림 20] Dot Plot (2024.9.18)
# ## required file
#   - plot_def.py
#   - fred_api.py
# ## data 디렉토리에 필요한 파일
#   - f_Dot_plot.xlsx
# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# 한글 폰트 설정
from plot_def import *
set_fonts()

# 엑셀 파일 불러오기
df = pd.read_excel("data/f_Dot_plot.xlsx")

# year가 문자열인지 확인 후 정렬 순서 지정
df['year'] = df['year'].astype(str)
unique_years = sorted(df['year'].unique().tolist())

# 그래프 설정
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

# 점 찍기: (year, rate) 중복 방지 및 퍼트리기

for i, year in enumerate(unique_years):

    # 중앙값 계산

    values = []

    valid = df[df['year'] == year]
    for _, row in valid.iterrows():
        target = row['rate']
        values.extend([target])

    median_val = np.median(values)
    print(median_val)

    year_data = df[df['year'] == year]
    counts = year_data.groupby('rate').size()

    for rate in counts.index:
        count = counts[rate]

        # 중앙값 위치는 빨강, 나머지는 파랑
        color = "black" if rate == median_val else "blue"

        if count == 1:
            ax.scatter(i, rate, s=50, c=color, marker='o', edgecolors='black', alpha=0.8)
        else:
            spacing = 0.07
            mid = (count - 1) / 2
            for j in range(count):
                x = i + spacing * (j - mid)
                ax.scatter(x, rate, s=50, c=color, marker='o', edgecolors='black', alpha=0.8)

ax.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)

# 기존 y축 틱 가져오기
yticks = ax.get_yticks()

# 중간 보조선 추가
midlines = [(yticks[i] + yticks[i + 1]) / 2 for i in range(len(yticks) - 1)]
all_ticks = sorted(list(yticks) + midlines)

# y축 틱 설정
ax.set_yticks(ticks=all_ticks)
ax.set_yticklabels([f"{tick:.2f}" for tick in all_ticks])

# x축 설정
ax.set_xticks(ticks=range(len(unique_years)))
ax.set_xticklabels(unique_years)

ax.text(0, 1, '(정책금리, %)', ha='left', va='bottom', color='black',
        fontsize=12, rotation=0, transform=ax.transAxes)

# 출처 표기
ax.text(0.0, -0.150, "출처: FRB, 붉은 점은 중앙값", transform=ax.transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()