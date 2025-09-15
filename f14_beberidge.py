# [그림 14] 베버리지커브: 구인율과 실업률

# 이용되는 API data fetch function

# from fred_api import fetch_fred_series

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter
import platform


# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# 폰트 설정
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'Malgun Gothic'




#Job Openings: Total Nonfarm (JTSJOR)
#Observations
#Jun 2025: 4.4
#Updated: Jul 29, 2025 9:08 AM CDT
#Next Release Date: Sep 3, 2025
#Units:Rate,Seasonally Adjusted
#Frequency: Monthly

# Fetch from FRED, def를 fred_api.py로 따로 저장함

from fred_api import fetch_fred_series

# 사용자 정의 기간으로 호출
start = "2000-12-01"
end = "2029-12-31"

# Fetch series
#Job Openings: Total Nonfarm (JTSJOR)
#Observations
#Jun 2025: 4.4
#Updated: Jul 29, 2025 9:08 AM CDT
#Next Release Date: Sep 3, 2025
#Units:Rate,Seasonally Adjusted
#Frequency: Monthly
df0 = fetch_fred_series('JTSJOR', start_date=start, end_date=end)

#Unemployment Rate (UNRATE)
#Observations
#Jul 2025: 4.2
#Updated: Aug 1, 2025 7:49 AM CDT
#Next Release Date: Sep 5, 2025
#Units: Percent,Seasonally Adjusted
#Frequency:Monthly
df1 = fetch_fred_series('UNRATE', start_date=start, end_date=end)

df=pd.merge(df0, df1, on='observation_date')

# 변경할 컬럼 이름들을 dict로 정의
rename_dict = {
    "observation_date": "Date",
    'JTSJOR': 'Job openings rate',
    'UNRATE': 'Unemployment rate'
}

# 이름 변경 적용
df = df.rename(columns=rename_dict)

# 정렬
df = df.sort_values('Date')

# 2024년 8월 데이터 필터링
highlight_row = df[df['Date'] == pd.Timestamp('2024-08-01')]

# 2025년 4월 데이터 필터링
highlight_row1 = df[df['Date'] == pd.Timestamp('2025-04-01')]


# 시각화 시작
fig, ax = plt.subplots(figsize=(8, 4.5),constrained_layout=True)
#plt.figure(figsize=(12, 6),constrained_layout=True)

date = df['Date'].max()
last_month = '{date.year}.{date.month}'.format(date=date)

# 기간별 색상 설정
periods = [
    ('2000-12-01', '2001-02-28', 'red', '2000.12 - 2001.2'),
    ('2001-03-01', '2001-11-30', 'orange', '2001.3 - 2001.11'),
    ('2001-12-01', '2007-11-30', 'green', '2001.12 - 2007.11'),
    ('2007-12-01', '2009-06-30', 'blue', '2007.12 - 2009.6'),
    ('2009-07-01', '2020-02-29', 'purple', '2009.7 - 2020.2'),
    ('2020-03-01', '2020-04-30', 'brown', '2020.3 - 2020.4'),
    ('2020-05-01', df['Date'].max(), 'black', '2020.5 - 2025.7'),
    ('2020-05-01', df['Date'].max(), 'black', f"2020.5 - {last_month}")

]

# 궤적선을 기간별로 나누어 그림
for start, end, color, label in periods:
    mask = (df['Date'] >= pd.Timestamp(start)) & (df['Date'] <= pd.Timestamp(end))
    sub_df = df[mask]
    if len(sub_df) >= 2:  # 선 그리기 위해 최소 2개 이상의 포인트 필요
        ax.plot(
            sub_df['Unemployment rate'],
            sub_df['Job openings rate'],
            color=color,
            linewidth=2,
            alpha=0.9,
            label=label
        )

# 기본 점들
ax.scatter(
    df['Unemployment rate'],
    df['Job openings rate'],
    s=20,
    color='gray',
    alpha=0.6,
    marker='o',
#    label='Monthly Data'
)

# 2024년 8월 점 강조
if not highlight_row.empty:
    ax.scatter(
        highlight_row['Unemployment rate'],
        highlight_row['Job openings rate'],
        s=90,
        color='red',
        edgecolors='black',
        label='2024.8'
    )

# 2025년 4월 점 강조
if not highlight_row1.empty:
    ax.scatter(
        highlight_row1['Unemployment rate'],
        highlight_row1['Job openings rate'],
        s=80,
        color='blue',
        edgecolors='black',
        label=last_month
    )

# 축 설정 및 포맷

ax.text(0, 1.00, '(구인율)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)
ax.text(1, -0.1, '(실업률)', ha='right', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)

ax.xaxis.set_major_formatter(PercentFormatter())
ax.yaxis.set_major_formatter(PercentFormatter())

ax.text(0.0, -0.15, "출처: BLS",
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black', transform=ax.transAxes)

plt.grid(False)
plt.legend()


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
import os
from PIL import Image


## 현재 작업 중인 파일 이름 추출 (확장자 제거)

try:
    base_filename = os.path.splitext(os.path.basename(__file__))[0]
except NameError:
    base_filename = "default_filename"

# 저장 경로 설정
image_path_tif = f"pic_tif/{base_filename}.tif"
image_path_jpg = f"pic_jpg/{base_filename}.jpg"

# 디렉토리 없으면 자동 생성
os.makedirs("pic_tif", exist_ok=True)
os.makedirs("pic_jpg", exist_ok=True)

# 그래프 저장
plt.savefig(image_path_tif, dpi=300)
plt.savefig(image_path_jpg, dpi=300)

# JPEG → CMYK 변환 후 덮어쓰기
img = Image.open(image_path_jpg).convert("CMYK")
img.save(image_path_jpg, "JPEG")
plt.show()
