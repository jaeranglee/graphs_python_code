


%matplotlib inline
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import platform





if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'
else:
    plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False





import requests






api_key = "4ead954629a702c25c55aa77e52d9070"
# api_key = "your api key"






start = '2022-01-01'
end = '2025-10-01'

def fetch_fred_series(series_id, start_date=start, end_date=end):

    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json',
        'observation_start': start_date,
        'observation_end': end_date
    }
    r = requests.get(url, params=params)
    data = r.json()

    df = pd.DataFrame(data['observations'])
    df['date'] = pd.to_datetime(df['date'])
    df[series_id] = pd.to_numeric(df['value'], errors='coerce')
    return df[['date', series_id]]






df0 = fetch_fred_series('H41RESPPALDKNWW',
                        start_date=start, end_date=end)
df1 = fetch_fred_series('RIFSPFFNB',
                        start_date=start, end_date=end)





print(df0.head())








fig, ax = plt.subplots(1,2, figsize=(8, 4.5), constrained_layout=True)

ax[0].plot(df0['date'], df0['H41RESPPALDKNWW']/1e2,
           label='BTFP', color='blue', lw=2)
ax[0].axhline(y=0, color='gray', linestyle='--')

ax[0].xaxis.set_major_locator(mdates.YearLocator())
ax[0].legend(loc='upper left',bbox_to_anchor=(0.2, 0.7))
ax[0].yaxis.label.set_visible(True)
ax[0].text(0, 1.00, '(억 달러)', ha='left', va='bottom', color='black',
           fontsize=12, rotation=0, transform=ax[0].transAxes)

ax[0].text(0.0, -0.15, "출처: FRED, 음영은 BTFP 실시기간",
           transform=ax[0].transAxes, fontsize=10, ha='left')
ax[0].grid(False)





ax[1].plot(df1['date'], df1['RIFSPFFNB'],
           label='Effective Federal Funds Rate', color='blue', lw=2)
ax[1].axhline(y=0, color='gray', linestyle='--')
ax[1].legend(loc='upper left',bbox_to_anchor=(0.35, 0.7))
ax[1].xaxis.set_major_locator(mdates.YearLocator())

ax[1].text(0, 1.00, '(%)', ha='left', va='bottom', color='black',
           fontsize=12, rotation=0, transform=ax[1].transAxes)
ax[1].text(0.0, -0.15, "출처: FRED, 음영은 BTFP 실시기간",
           transform=ax[1].transAxes, fontsize=10, ha='left')
ax[1].grid(False)





from datetime import datetime
shaded_periods = [(datetime(2023, 3, 12),datetime(2024, 3, 11))]

for i in [0,1]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color='gray', alpha=0.2)






import os
from PIL import Image

try:
    base_filename = os.path.splitext(os.path.basename(__file__))[0]
except NameError:
    base_filename = "default_filename"

# 저장 경로를 설정하고 파일 이름을 정해준다.
image_path_tif = f"pic_tif/{base_filename}.tif"
image_path_jpg = f"pic_jpg/{base_filename}.jpg"

# 저장 경로가 없으면 자동으로 생성하도록 했다.
os.makedirs("pic_tif", exist_ok=True)
os.makedirs("pic_jpg", exist_ok=True)

# 그래프를 파일로 저장한다.
plt.savefig(image_path_tif, dpi=300)
plt.savefig(image_path_jpg, dpi=300)

# 그래프를 저장한 그림파일의 색공간을 JPEG와 CMYK로 각각 변환한다. JPEG는 주로 모니터 출력용, CMYK는 인쇄용으로 사용된다.
# 마지막 줄이 그래프를 모니터로 보여준다.

img = Image.open(image_path_jpg).convert("CMYK")
img.save(image_path_jpg, "JPEG")
plt.show()
