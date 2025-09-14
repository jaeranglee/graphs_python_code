# [그림 10] MMF의 RRP와 TGCR 거래 규모

# 이용되는 API data fetch function
# from nyfed_api_rate_volume import fetch_all_secured_rates_vol
# from nyfed_rrp_vol import fetch_rrp_vol
# from fred_api import fetch_fred_series

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# 폰트 설정
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# New York Fed Markets Data API 에서 자료 추출
# FRED series 호출
from nyfed_api_rate_volume import fetch_all_secured_rates_vol
from nyfed_rrp_vol import fetch_rrp_vol
from fred_api import fetch_fred_series

# 사용자 정의 기간

start = "2020-01-01"
end = "2025-12-31"

# Fetch Volume data from NY FED Markets Data
df_all = fetch_all_secured_rates_vol(start_date=start, end_date=end)

tgcr = df_all[df_all["Type"] == "TGCR"].copy()
bgcr = df_all[df_all["Type"] == "BGCR"].copy()
sofr = df_all[df_all["Type"] == "SOFR"].copy()
effr = df_all[df_all["Type"] == "EFFR"].copy()

# Fetch RRP data from FRED
# Liabilities and Capital: Liabilities: Reverse Repurchase Agreements: Week Average (WLRRAA)
# Units: Millions of U.S. Dollars,
# Not Seasonally Adjusted
# Frequency: Weekly,

df_rrp = fetch_fred_series('WLRRAA', start_date=start, end_date=end)

# Fetch Total RRP data from NY FED Markets Data,
ny_rrp = fetch_rrp_vol(start_date=start, end_date=end)[0]

# Fetch MMF's RRP data from NY FED Markets Data,
mmf_rrp = fetch_rrp_vol(start_date=start, end_date=end)[1]
mmf_rrp = mmf_rrp[mmf_rrp['Counterparty Type']=='mmf'].copy()


# 시각화
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)


ax_left = ax
ax_right = ax_left.twinx()  # Create right-side y-axis

#왼쪽 TGCR volume
ax_left.plot(tgcr['Date'], tgcr['Volume']/1e3, label='TGCR trading volume', lw=2, color='red')

# 오른쪽: FED RRP total volume, FED RRP with mmf volume
ax_right.plot(ny_rrp['Date'], ny_rrp['Total Volume']/1e12, label='RRP Total', linestyle='-', lw=2, color='green')
ax_right.plot(mmf_rrp['Date'], mmf_rrp['Amount Accepted']/1e12, label='MMF RRP', linestyle='-', lw=2, color='blue')


ax_right.set_ylim(-0.1,3)
ax_left.set_ylim(-0.1,3)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

ax_left.text(0, 1.00, '(조 달러)', ha='left', va='bottom',transform=ax.transAxes, fontsize=12, color='black')
ax_right.text(1, 1, '(조 달러)', ha='right', va='bottom', transform=ax.transAxes, fontsize=12, color='black')
ax_left.legend(loc='upper left',bbox_to_anchor=(0.0, 0.85))
ax_right.legend(loc='upper left',bbox_to_anchor=(0.0, 0.99))



ax.text(0, -0.15, '출처: NY FED', transform=ax.transAxes, fontsize=10)
ax.grid(True, linestyle='--', color='gray', alpha=0.3)


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
