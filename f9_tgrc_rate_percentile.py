## [그림 9] 1일만기 국채담보 단기금융거래 이자율

## NY Fed Markets Data fetch 함수
## from nyfed_api_all_rates import fetch_all_secured_rates



import matplotlib.pyplot as plt
import platform

# 폰트 설정
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False


# Fetch Data from NY FED Markets Data, Reference Rates

from nyfed_api_all_rates import fetch_all_secured_rates

start = "2023-01-01"
end = "2025-12-31"

df_all = fetch_all_secured_rates(start_date=start, end_date=end)

## tgcr, sofr, bgcr, sofrai, effr, obfr 등 선택가능

rate_type_filter = "tgcr"

df_tgcr = df_all[df_all["Type"] == rate_type_filter.upper()].copy()

# 날짜 정렬

df_tgcr = df_tgcr.sort_values("Date")

#--------------------
# FRED Data fetch
# Overnight Reverse Repurchase Agreements Award Rate:
# Treasury Securities Sold by the Federal Reserve in the Temporary Open Market Operations
# (RRPONTSYAWARD)
# Units: Percent,Not Seasonally Adjusted
# Frequency: Daily

from fred_api import fetch_fred_series

df_onrrp = fetch_fred_series('RRPONTSYAWARD', start_date=start, end_date=end)


# 그래프
fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)

ax.plot(df_tgcr["Date"], df_tgcr["Rate"], label="TGCR", color="red", linewidth=2)
ax.plot(df_onrrp["observation_date"], df_onrrp["RRPONTSYAWARD"], label="O/N RRP", color="blue", linewidth=2)

# Percentile 구간을 면적(band)으로 표현
ax.fill_between(df_tgcr["Date"], df_tgcr["Percentile25"], df_tgcr["Percentile75"],
                 color="green", alpha=1, label="25th–75th Percentile")
ax.fill_between(df_tgcr["Date"], df_tgcr["Percentile1"], df_tgcr["Percentile99"],
                 color="lightgray", alpha=0.5, label="1st–99th Percentile")
ax.set_ylim(4.0,5.5)

# 점선 스타일 그리드 표시
ax.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)

plt.legend()

# 단위 표시 및 출처
ax.text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
         fontsize=12, rotation=0, transform=ax.transAxes,)
ax.text(0.0, -0.15, "출처: New York FED, FRED", fontsize=10, ha='left', transform=ax.transAxes,)



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



