# [그림 11] 1일물 금리
#
# 이용되는 API data fetch function
#
# from fred_api import fetch_fred_series
# from nyfed_api_rate_volume import fetch_all_secured_rates_vol



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


# FRED API 호출 함수
from fred_api import fetch_fred_series

start='2024-08-01'
end='2025-10-31'

# fetch IORB and SOFR from FRED

iorb = fetch_fred_series('IORB', start_date=start, end_date=end)
sofr = fetch_fred_series('SOFR', start_date=start, end_date=end)

# Effective Federal Funds Rate (EFFR)

effr = fetch_fred_series('EFFR', start_date=start, end_date=end)

# Fed Target upper bound and lower bound
target_u = fetch_fred_series('DFEDTARU', start_date=start, end_date=end)
target_l = fetch_fred_series('DFEDTARL', start_date= start, end_date=end)  # Lower Target 추가

target_u['DFEDTARL'] = target_l['DFEDTARL']  # 상하한 결합

# O/N RRP rates
# Overnight Reverse Repurchase Agreements Award Rate:
# Treasury Securities Sold by the Federal Reserve in the Temporary
# Open Market Operations (RRPONTSYAWARD)
rrp = fetch_fred_series("RRPONTSYAWARD", start_date=start, end_date=end)

# New York Fed Markets Data fetch
# nyfed_api_all_rates.py로 만든 def 호출

from nyfed_api_all_rates import fetch_all_secured_rates


# fetch secured over night rates

df_all = fetch_all_secured_rates(start_date=start, end_date=end, rate_type_filter=None)

# tgcr, sofr, bgcr, sofrai, effr, obfr 등 선택가능


tgcr = df_all[df_all["Type"] == 'TGCR'].copy()
effr1 = df_all[df_all["Type"] == "EFFR"].copy()



# 그래프 그리기
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

# 왼쪽:
ax.plot(iorb['observation_date'], iorb['IORB'], label='IORB', lw=2, color='red')
ax.plot(sofr['observation_date'], sofr['SOFR'], label='SOFR', lw=2, color='orange')
ax.plot(tgcr['Date'], tgcr['Rate'], label='TGCR', lw=2, color='blue')



ax.plot(effr1['Date'], effr1['Rate'], label='EFFR', lw=2, color='black')
ax.plot(rrp['observation_date'], rrp['RRPONTSYAWARD'], label="O/N RRP", lw=1, ls="--", color='black')

# target rate bound in filled lines
ax.fill_between(target_u['observation_date'], target_u['DFEDTARU'], target_u['DFEDTARL'], color='gray', alpha=0.2, label='Target Range')


ax.legend(loc='upper right', bbox_to_anchor=(1, 1))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.text(0, 1.00, '(%)',  ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
ax.text(0, -0.15, '출처: FRED, NY FED', transform=ax.transAxes, fontsize=10)

# grid with dashed lines
ax.grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.7)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
import os
from PIL import Image

# 현재 작업 중인 파일 이름 추출 (확장자 제거)

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

plt.savefig(image_path_tif, dpi=300)
plt.savefig(image_path_jpg, dpi=300)

# RGB → CMYK 변환
img = Image.open(image_path_jpg).convert("CMYK")
img.save(image_path_jpg, "JPEG")

plt.show()
