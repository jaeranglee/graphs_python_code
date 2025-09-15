# [그림 12] 연방기금금리와 정책금리

# 이용되는 API data fetch function
#
# from fred_api import fetch_fred_series

import matplotlib.pyplot as plt
import platform

# Set font depending on the platform
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'Malgun Gothic'

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False



# api를 이용해 FRED 자료 fetch

start='2022-01-01'
end='2025-12-31'

from fred_api import fetch_fred_series


# FRED api로 한번에 1개의 시리즈 호출

# EFFR Daily
# Upper Target Daily, 7-Day
# Lower Target Daily, 7-Day


df0 = fetch_fred_series('RIFSPFFNB', start_date=start, end_date=end)
df1 = fetch_fred_series('DFEDTARU', start_date=start, end_date=end)
df2 = fetch_fred_series('DFEDTARL', start_date=start, end_date=end)

merged_df = df0.copy()
#---------------------


# 그래프 그리기
fig, ax = plt.subplots(figsize=(9, 4.5),constrained_layout=True)

# 보조 y축: Effective Federal Funds Rate
ax.plot(merged_df['observation_date'], merged_df['RIFSPFFNB'], label='실효연방기금금리', color='red', lw=2)

ax.fill_between(df1['observation_date'],df1['DFEDTARU'], df2['DFEDTARL'],label='정책금리 범위', alpha=0.2)
ax.text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes)

ax.tick_params(axis='y', labelcolor='b')

# 제목 및 레이아웃
ax.text(0.0, -0.15, "출처: FRED",transform=ax.transAxes,
         fontsize=11, verticalalignment='bottom', horizontalalignment='left', color='black')



plt.grid(False)
ax.legend()

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
