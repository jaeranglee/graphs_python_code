# %% [markdown]
# # [그림 1] 은행예금 잔액과 은행업 ETF가격
#
# ## 이 코드가 하는 일
# 두 곳에서 자료를 받아 그림 두 개를 나란히 그린다.
# - FRED(세인트루이스 연준의 경제통계 사이트)에서 미국 전체 은행과 중소은행의 예금 잔액을 받는다.
# - Yahoo Finance에서 은행주를 묶은 ETF(S&P Banks ETF, 종목기호 KBE)의 주가를 받는다.
#
# ## 그림이 다루는 내용
# 2022년 연준이 금리를 빠르게 올리자 예금이 은행을 떠나기 시작했고,
# 2023년 3월 실리콘밸리은행(SVB)이 파산하면서 은행주 가격이 크게 떨어졌다.
# 왼쪽 그림으로 예금이 줄어드는 모습을, 오른쪽 그림으로 은행주가 떨어지는 모습을 확인한다.
#
# ## 결과물
# pic_jpg/f1_bank_deposits.jpg(화면용)와 pic_tif/f1_bank_deposits.tif(인쇄용)가 저장되고, 화면에도 그림이 나타난다.
#
# ## 이 코드에서 새로 배우는 것
# 1. yfinance 패키지로 주식가격을 받는 방법
# 2. 다른 파일(defs/fred_api.py)에 저장해 둔 함수를 불러와 쓰는 방법
#
# 첫 셀은 필요한 패키지를 불러온다. yfinance는 Yahoo Finance 자료를 쉽게 받게 해 주는 무료 패키지이며,
# 관례에 따라 yf라는 짧은 이름으로 부른다. 파이썬은 파일마다 쓸 패키지를 처음에 불러와야 한다.
# %%
# %matplotlib inline

import platform
from datetime import date

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import yfinance as yf

# %% [markdown]
# 그래프에 한글이 깨지지 않도록 폰트를 정한다.
# 맥(Darwin)이면 AppleGothic, 윈도우면 맑은 고딕을 쓴다.
# 마지막 줄은 음수 부호(-)가 네모로 깨져 보이는 것을 막는다.
# %%

if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
else:
    plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# %% [markdown]
# [그림 2]에서는 FRED 자료를 받는 함수를 코드 안에 직접 만들었다.
# 이번에는 같은 일을 하는 함수를 따로 저장해 둔 파일에서 불러와 쓴다.
# 여러 그림이 같은 함수를 쓰므로, 한곳에 두면 고칠 때도 한 번만 고치면 된다.
#
# - 공통 함수 파일은 이 폴더가 아니라 한 단계 위의 defs 폴더에 있다.
#   처음 몇 줄은 defs 폴더를 찾아 파이썬이 그 안의 파일을 불러올 수 있게 한다.
# - from fred_api import fetch_fred_series는 "fred_api.py 파일에서 fetch_fred_series 함수를 가져오라"는 뜻이다.
# - fetch_fred_series(자료 이름, start_date=시작일, end_date=종료일)처럼 쓰면 dataframe(표 형태의 자료)을 돌려준다.
#   첫째 열은 날짜(observation_date), 둘째 열은 자료 값이며 열 이름은 자료 이름과 같다.
# - 시작일은 2022년 1월 1일, 종료일은 오늘(date.today())로 정해 가장 최근 자료까지 받는다.
# %%
# 공통 함수 폴더(defs)를 import 경로에 추가
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
_defs = next(
    d
    for p in (_here, *_here.parents)
    for d in (p / "defs", p / "codes" / "defs")
    if d.is_dir()
)
sys.path.insert(0, str(_defs))

from fred_api import fetch_fred_series

"""
이용할 자료의 시작 시점과 마지막 시점을 정했다. 2022년 1월부터 가장 최신 자료까지 불러온다.
"""

start = "2022-01-01"
# end = "2025-12-01"
end = date.today()
"""
FRED API에서 자료를 불러온다. 은행 예금총액 'DPSACBM027NBOG'를 불러와서 df0에 할당하고,
소규모은행 예금총액 'DPSSCBM027NBOG'를 불러와서 df1에 할당했다. 각각
Deposits, All Commercial Banks 그리고, Deposits, Small Domestically Chartered Commercial Banks에 해당한다.
fetch_fred_serie() 함수에는 파라미터가 3개 들어간다. 맨앞에 series_id 값을 적고, start_date, end_date 순서로 적는다.
"""


df0 = fetch_fred_series("DPSACBM027NBOG", start_date=start, end_date=end)
df1 = fetch_fred_series("DPSSCBM027NBOG", start_date=start, end_date=end)

# %% [markdown]
# ### yfinance로 은행주 ETF 가격 받기
# ETF는 여러 주식을 묶어 하나의 주식처럼 거래하는 펀드이다. KBE는 미국 은행주들을 묶은 ETF라서
# 은행업 전체의 주가 흐름을 보여준다.
#
# 1. yf.Ticker("KBE")로 KBE 종목을 지정해 bkx라는 변수에 담는다.
#    종목기호(ticker)는 미국 주식마다 붙은 짧은 이름이며, 정확히 적어야 오류 없이 자료가 온다.
# 2. history(start=..., end=...)로 2022년 1월 1일부터 2025년 12월 31일까지의 가격을 받아 data에 담는다.
# 3. 그중 2022년 1월 1일부터 2024년 12월 31일까지만 다시 골라낸다. 책의 그림과 같은 기간이다.
# 4. 자료의 첫 날짜와 마지막 날짜, 그리고 처음 10줄을 출력해 제대로 받았는지 확인한다.
#
# 다른 주식을 그리고 싶으면 KBE 자리에 그 종목기호를 넣으면 된다.
# 기간을 바꾸려면 날짜를 'yyyy-mm-dd' 형식으로 따옴표 안에 적는다.
# %%

bkx = yf.Ticker("KBE")
data = bkx.history(start="2022-01-01", end="2025-12-31")
data = data[(data.index >= "2022-01-01") & (data.index <= "2024-12-31")]

"""
자료가 잘 호출되었는지 확인하기 위해 data로 들어온 자료의 시작일과 종료일을 출력하고,
data에 들어있는 처음 5개 자료를 출력해 본다.
"""

print(data.index.min(), data.index.max())
print(data.head(10))

"""
자료가 잘 들어왔다면, 자료의 시작일은 2022-01-01, 종료일은 2024-12-31로 나온다.
data의 첫 번째 열의 이름은 Close이며 그 날짜의 주식 종가를 의미한다. data에는 날짜가 인덱스로 사용되었음을 확인할 수 있다.
"""

# %% [markdown]
# 이제 그림을 그린다. plt.subplots(1, 2, ...)는 한 줄에 그림 두 개를 만든다는 뜻이다.
# fig는 그림 전체, ax[0]은 왼쪽 그림, ax[1]은 오른쪽 그림이다.
# figsize=(8, 4.5)는 가로 8인치, 세로 4.5인치이고, constrained_layout=True는 글자가 겹치지 않게 간격을 자동으로 맞춘다.
# %%

fig, ax = plt.subplots(1, 2, figsize=(8, 4.5), constrained_layout=True)


# %% [markdown]
# ### 왼쪽 그림: 전체 은행 예금과 중소은행 예금
# 전체 은행 예금은 약 17조 달러, 중소은행 예금은 그보다 훨씬 작다.
# 한 개의 y축에 같이 그리면 작은 쪽의 움직임이 거의 보이지 않으므로 y축을 왼쪽과 오른쪽에 하나씩 둔다.
#
# - ax_left = ax[0]: 왼쪽 y축(전체 은행 예금)
# - ax_right = ax_left.twinx(): x축은 함께 쓰고 y축만 오른쪽에 하나 더 만든다(중소은행 예금).
# - FRED 자료는 10억 달러 단위라서 1e3(=1,000)으로 나누어 조 달러 단위로 바꾼다.
# - 중소은행 예금은 점선(ls="--")으로 그려 구별한다.
# - 축이 두 개라 범례도 두 개가 생기므로, 두 범례를 하나로 합쳐 왼쪽 위에 놓는다.
# - 그림 위쪽 양옆에 단위 (조 달러)를, 아래에 출처를 적는다.
# %%

ax_left = ax[0]
ax_right = ax_left.twinx()

ax_left.plot(
    df0["observation_date"],
    df0["DPSACBM027NBOG"] / 1e3,
    label="은행 예금",
    color="blue",
    lw=2,
)
ax_right.plot(
    df1["observation_date"],
    df1["DPSSCBM027NBOG"] / 1e3,
    label="중소은행 예금",
    color="blue",
    lw=2,
    ls="--",
)


# 첫 번째 그래프의 x축 날짜 간격, 선그래프 라벨, 단위표시, 자료출처 표시를 지정하는 곳이다.

ax[0].xaxis.set_major_locator(mdates.YearLocator())
# 두 축의 범례를 하나로 합친다.
h1, l1 = ax_left.get_legend_handles_labels()
h2, l2 = ax_right.get_legend_handles_labels()
ax_left.legend(h1 + h2, l1 + l2, loc="upper left")
ax_left.yaxis.label.set_visible(True)
ax_left.text(
    0,
    1.00,
    "(조 달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax_right.text(
    1.0,
    1.00,
    "(조 달러)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax[0].text(0.0, -0.15, "출처: FRED", transform=ax[0].transAxes, fontsize=10, ha="left")
ax[0].grid(False)


# %% [markdown]
# ### 오른쪽 그림: S&P Banks ETF 가격
# x축에 날짜, y축에 종가(Close, 그날 마지막으로 거래된 가격)를 놓고 선그래프를 그린다.
# 앞에서 출력해 본 것처럼 yfinance 자료는 날짜가 열이 아니라 각 줄의 이름(index)으로 들어 있다.
# 그래서 x축에 data.index를 넣는다.
# %%

ax[1].plot(data.index, data["Close"], label="S&P Banks ETF", color="blue", lw=2)


ax[1].legend(loc="upper left", bbox_to_anchor=(0.3, 1))
ax[1].xaxis.set_major_locator(mdates.YearLocator())
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax[1].text(
    0,
    1.00,
    "(달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)

ax[1].text(
    0.0,
    -0.15,
    "출처: Yahoo Finance, S&P",
    transform=ax[1].transAxes,
    fontsize=10,
    ha="left",
)
ax[1].grid(False)

# %% [markdown]
# ### 그림 저장
# 다른 그림 코드들은 마지막 줄의 plot_save() 한 줄로 그림을 저장한다(defs/plot_def.py).
# 이 파일은 저장 과정을 보여주려고 plot_save()가 하는 일을 코드에 그대로 풀어 적었다. 결과 파일도 같다.
# 1. 이 파일의 이름(f1_bank_deposits)을 그대로 그림 파일 이름으로 쓴다.
# 2. pic_tif, pic_jpg 폴더가 없으면 만든다.
# 3. y축 숫자에 세 자리마다 쉼표를 넣는다. 소수점 자리수는 눈금 값에 맞춰 정한다.
#    예: 눈금이 1000, 2000이면 '1,000', '2,000' / 2.5, 3.0이면 '2.5', '3.0'
# 4. 해상도 300dpi로 tif와 jpg 두 가지로 저장한다. tif는 LZW 방식으로 압축한다.
#    LZW는 화질을 그대로 두고 파일 크기만 줄이는 압축이다(무손실 압축, 크기 약 1/10).
# 5. jpg를 RGB 색 체계로 바꿔 다시 저장한다. RGB는 모니터에서 쓰는 빨강·초록·파랑 색 체계이다.
# 6. plt.show()로 그림을 화면에 띄운다.
#
# os는 파일과 폴더를 다루는 기본 모듈이고, PIL(Image)은 그림 파일을 다루는 패키지이다(pip install pillow).
# %%

import os

from matplotlib.ticker import StrMethodFormatter
from PIL import Image

# 1. 그림 파일 이름 = 이 .py 파일 이름
try:
    base_filename = os.path.splitext(os.path.basename(__file__))[0]
except NameError:  # jupyter처럼 __file__이 없을 때
    base_filename = "f1_bank_deposits"

image_path_tif = f"pic_tif/{base_filename}.tif"
image_path_jpg = f"pic_jpg/{base_filename}.jpg"

# 2. 저장 폴더가 없으면 만든다.
os.makedirs("pic_tif", exist_ok=True)
os.makedirs("pic_jpg", exist_ok=True)

# 3. 모든 y축에 천 단위 쉼표. 눈금 값을 정확히 나타내는 가장 적은 소수점 자리수(0~6)를 고른다.
for a in plt.gcf().axes:
    ticks = a.get_yticks()
    d = 0
    while d < 6 and any(abs(t - round(t, d)) > 1e-9 * max(1.0, abs(t)) for t in ticks):
        d += 1
    a.yaxis.set_major_formatter(StrMethodFormatter(f"{{x:,.{d}f}}"))

# 4. 300dpi로 저장. tif는 무손실 LZW 압축
plt.savefig(image_path_tif, dpi=300, pil_kwargs={"compression": "tiff_lzw"})
plt.savefig(image_path_jpg, dpi=300)

# 5. jpg를 RGB로 바꿔 다시 저장
img = Image.open(image_path_jpg).convert("RGB")
img.save(image_path_jpg, "JPEG")

# 6. 화면에 띄우기
plt.show()

# %%
