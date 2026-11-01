# %% [markdown]
# # [그림 2] BTFP 잔액과 정책금리
#
# ## 이 코드가 하는 일
# FRED에서 자료 두 개를 받아 그림 두 개를 나란히 그린다.
# - 왼쪽: BTFP 대출 잔액(매주 수요일 기준)
# - 오른쪽: 실효연방기금금리(미국 은행들이 서로 하루 동안 돈을 빌려줄 때 실제로 적용된 평균 금리)
#
# ## 그림이 다루는 내용
# BTFP(Bank Term Funding Program)는 2023년 3월 SVB 파산 직후 연준이 만든 긴급 대출 제도이다.
# 은행이 가진 국채 등을 담보로 맡기면 최장 1년 동안 돈을 빌려주었다. 금리가 올라 국채 가격이 떨어졌는데도
# 담보 가치를 액면가 그대로 쳐 주었기 때문에, 은행이 손해를 보고 국채를 팔지 않아도 예금 인출에 대응할 수 있었다.
# 신규 대출은 2024년 3월 11일에 끝났다. 오른쪽 그림은 같은 시기 정책금리가 0%대에서 5%대로 오른 모습을 보여준다.
#
# ## 결과물
# pic_jpg/f2_btfp.jpg, pic_tif/f2_btfp.tif가 저장되고 화면에도 그림이 나타난다.
#
# ## 1. FRED API key 받기
# API는 프로그램이 다른 사이트에 자료를 요청하는 통로이고, API key는 그 통로를 쓰는 개인 비밀번호이다.
# 1. 검색 엔진에서 'fred api'를 검색해 FRED API 홈페이지로 간다.
# 2. 오른쪽 'API Keys' 링크를 누르면 회원가입이 필요하다고 나온다. 'Register'에서 이메일로 가입한다.
# 3. 'Sign in'으로 로그인한 뒤 다시 'Request or view your API keys'로 가서 신청 양식을 내면 바로 key가 나온다.
#    사용 목적은 'Personal Study' 정도로 적으면 된다.
# 4. key는 영어와 숫자로 된 긴 문자열이다. 복사해 두고 남에게 보이지 않게 한다.
#
# ## 2. 코드 실행하기
# 1. PyCharm에서 f2_btfp.py를 연다.
# 2. api_key = "your api key"에서 your api key를 지우고 따옴표 안에 내 key를 넣는다.
#    예: api_key = 'aaabbbbcccdddeeefff11122233344'
# 3. 윈도우는 shift + control + f10을 함께 누르고, 맥은 오른쪽 위에서 '현재 파일'을 고른 뒤 세모 버튼을 누른다.
# 4. 정상적으로 끝나면 화면에 그림이 나타난다.
#
# ## 3. 코드의 네 단계
# 다른 그림의 코드도 대체로 같은 순서로 되어 있다.
# 1. 준비: 패키지를 불러오고 한글 폰트를 정한다.
# 2. 자료 받기: FRED에서 자료를 받아 변수에 담는다. 기간을 정하고 필요하면 단위를 바꾼다.
# 3. 그리기: 그래프를 그리고 단위, 범례, 출처를 붙인다.
# 4. 저장: 그림을 파일로 저장하고 화면에 보여준다.
#
# ## 4. 패키지 불러오기 (아래 셀)
# - matplotlib.dates (mdates): x축 날짜 표시 형식을 정한다.
# - matplotlib.pyplot (plt): 그래프를 그린다.
# - pandas (pd): 표 형태의 자료(dataframe)를 다룬다. 이 책의 모든 그림은 자료를 dataframe으로 다룬다.
# 패키지 이름을 mdates, plt, pd처럼 줄여 쓰는 것은 관례이니 그대로 따라 하면 된다.
# 설치되지 않은 패키지는 pip install 패키지이름으로 설치한다.
#
# ※ 책과 달라진 점: 따옴표 안에 key를 넣지 않고 그대로 두면 defs/.env 파일에 적어 둔 FRED_API_KEY를 대신 읽는다.
# FRED 요청이 실패하면 FRED가 보낸 오류 메시지를 보여주고 멈춘다. 오른쪽 그림의 범례는 선과 겹치지 않도록 오른쪽 아래로 옮겼다.
# %%
# %matplotlib inline
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

# %% [markdown]
# ### 한글 폰트 정하기
# matplotlib은 기본 폰트에 한글이 없어서 그대로 두면 한글이 네모로 깨진다.
# 아래 코드는 후보 폰트를 차례로 확인해 컴퓨터에 설치된 첫 번째 폰트를 쓴다.
# - 맥: AppleGothic, 윈도우: Malgun Gothic, 리눅스나 Colab: NanumGothic, 마지막 대안: DejaVu Sans
# - 하나도 없으면 한글 폰트를 설치하라는 안내를 출력한다.
# 마지막 줄은 음수 부호(-)가 깨져 보이는 것을 막는다.
# %%

import os

import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from matplotlib.ticker import StrMethodFormatter

# 후보 폰트 리스트 (운영체제별로 다르게 설치되어 있을 수 있음)
font_candidates = [
    "AppleGothic",  # macOS
    "Malgun Gothic",  # Windows
    "NanumGothic",  # Linux (Colab 등)
    "DejaVu Sans",  # fallback (영문/일부 한글 지원)
]

# 설치된 폰트 중 사용 가능한 것 찾기
available_fonts = set(f.name for f in fm.fontManager.ttflist)
selected_font = None
for font in font_candidates:
    if font in available_fonts:
        selected_font = font
        break

if selected_font:
    plt.rcParams["font.family"] = selected_font
else:
    print("한글 폰트를 찾을 수 없습니다. 시스템에 폰트를 설치하세요.")

plt.rcParams["axes.unicode_minus"] = False

# %% [markdown]
# ### 2단계: 자료 받기
# 이제 FRED에 자료를 요청한다. 인터넷으로 요청을 보내고 답을 받는 일은 requests 패키지가 맡는다.
# Path(pathlib)는 폴더와 파일 경로를 다루는 기본 모듈이며, 캐시 폴더를 찾고 만들 때 쓴다.
# %%
from pathlib import Path

import requests

# %% [markdown]
# ### API key 넣기
# 발급받은 key를 api_key 변수에 담는다. key는 반드시 따옴표 안에 적는다.
# 여기서는 예시로 "your api key"라는 가짜 값을 넣어 두었다.
#
# key를 바꾸지 않고 그대로 두면, 아래 if 문이 defs/.env 파일에서 FRED_API_KEY를 찾아 대신 넣는다.
# .env는 key를 코드와 따로 보관하는 파일이며 다른 그림의 코드들도 함께 쓴다(README 참고).
# %%


api_key = "your api key"

# 키를 직접 넣지 않았다면 환경변수나 defs/.env의 FRED_API_KEY를 쓴다.
if api_key == "your api key":
    from dotenv import load_dotenv

    _here = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
    for _p in (_here, *_here.parents):
        if (_p / "defs" / ".env").is_file():
            load_dotenv(_p / "defs" / ".env")
            break
    api_key = os.getenv("FRED_API_KEY", api_key)

# %% [markdown]
# ### 자료를 받는 함수 만들기
# def는 함수를 만든다는 뜻이다. 함수는 자주 하는 일을 묶어 이름을 붙인 것이며, 여기서는 fetch_fred_series라고 이름 붙였다.
# 괄호 안의 값(파라미터) 세 개를 주면 그 자료를 받아 dataframe으로 돌려준다.
# - series_id: FRED가 자료마다 붙인 이름. FRED 홈페이지 검색창에서 'BTFP'를 검색하고 원하는 자료를 누르면 볼 수 있다.
#   BTFP 대출 잔액의 이름은 'H41RESPPALDKNWW'이다.
# - start_date: 시작일. start 변수에 '2022-01-01'을 담아 두었다.
# - end_date: 종료일. end 변수에 '2025-10-01'을 담아 두었다. 아직 오지 않은 날짜를 넣으면 있는 자료까지만 온다.
#
# FRED는 일별·월별·분기별·연간 자료 모두 그 기간의 첫날로 날짜를 적는다.
# 예를 들어 2022년 1분기는 '2022-01-01', 2분기는 '2022-04-01', 2023년 연간 자료는 '2023-01-01'이다.
#
# 함수 안에서 하는 일
# 1. 캐시 파일이 있으면 FRED에 요청하지 않고 그 파일을 읽는다(아래 '캐시' 설명).
# 2. 없으면 requests.get()으로 FRED에 요청을 보내고, 받은 답을 r.json()으로 읽는다.
# 3. 답에 'observations'(관측값)가 없으면 요청이 실패한 것이므로 FRED의 오류 메시지(예: key가 틀림)를 보여주고 멈춘다.
# 4. 관측값을 dataframe으로 바꾸고 날짜와 값을 각각 날짜형, 숫자형으로 바꾼 뒤 캐시 파일로 저장한다.
# 5. 첫째 열이 'date', 둘째 열이 series_id인 dataframe을 돌려준다.
#
# ### 캐시(cache)
# 캐시는 한 번 받은 자료를 컴퓨터에 저장해 두었다가 다음에 다시 쓰는 것이다.
# 코드를 여러 번 실행해도 FRED에 같은 요청을 반복하지 않아 빠르고, 인터넷이 끊겨도 그림을 다시 그릴 수 있다.
# - 저장 폴더: defs 폴더 옆의 cache/fred_cache. 다른 그림 코드가 쓰는 defs/fred_api.py와 같은 폴더를 쓴다.
#   처음 실행할 때 폴더가 없으면 mkdir()이 만든다.
# - 파일 이름: '자료이름.시작일.종료일.parquet' (예: RIFSPFFNB.2022-01-01.2025-10-01.parquet).
#   이름 규칙이 fred_api.py와 같아서 두 코드가 서로의 캐시를 그대로 쓴다.
# - parquet는 표 형태의 자료를 빠르게 읽고 쓰는 파일 형식이다(pyarrow 패키지 필요).
# - 새로 받고 싶으면 use_cache=False를 넣거나 캐시 파일을 지운다.
# %%

start = "2022-01-01"
end = "2025-10-01"

# 캐시 폴더: defs 폴더가 있는 곳의 cache/fred_cache (defs를 못 찾으면 이 파일 옆의 cache/fred_cache)
_here = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
_root = next(
    (d.parent for p in (_here, *_here.parents) for d in (p / "defs", p / "codes" / "defs") if d.is_dir()),
    _here,
)
CACHE_DIR = _root / "cache" / "fred_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)  # 처음 실행할 때 폴더를 만든다.


def fetch_fred_series(series_id, start_date=start, end_date=end, use_cache=True):

    cache_file = CACHE_DIR / f"{series_id}.{start_date}.{end_date}.parquet"

    # 캐시가 있으면 FRED에 요청하지 않고 읽는다.
    if use_cache and cache_file.exists():
        print(f"캐시 사용: {cache_file.name}")
        df = pd.read_parquet(cache_file)
        df["date"] = pd.to_datetime(df["date"])  # fred_api.py가 만든 캐시는 date가 글자로 저장돼 있다.
        return df[["date", series_id]]

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,
    }
    r = requests.get(url, params=params)
    data = r.json()
    if "observations" not in data:
        raise RuntimeError(f"FRED 요청 실패({series_id}): {data.get('error_message', data)}")

    df = pd.DataFrame(data["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df[series_id] = pd.to_numeric(df["value"], errors="coerce")

    # fred_api.py와 같은 열 구성으로 저장한다(observation_date 열도 넣는다).
    df["observation_date"] = df["date"]
    df.to_parquet(cache_file)
    return df[["date", series_id]]


# %% [markdown]
# ### 함수로 자료 받기
# 방금 만든 함수로 자료 두 개를 받는다.
# - df0: 'H41RESPPALDKNWW', BTFP 대출 잔액(매주 수요일, 백만 달러). 열 이름은 'date'와 'H41RESPPALDKNWW'
# - df1: 'RIFSPFFNB', 실효연방기금금리(%). 열 이름은 'date'와 'RIFSPFFNB'
# %%

df0 = fetch_fred_series("H41RESPPALDKNWW", start_date=start, end_date=end)
df1 = fetch_fred_series("RIFSPFFNB", start_date=start, end_date=end)

# %% [markdown]
# ### 받은 자료 확인하기
# df0.head()는 처음 다섯 줄을 보여준다. 자료가 잘 왔는지, dataframe이 어떻게 생겼는지 확인할 수 있다.
# 아래 결과처럼 맨 왼쪽 숫자(0, 1, 2, ...)는 각 줄의 번호(index)이고, 그 옆에 날짜(date)와 BTFP 잔액이 나온다.
# 2022년에는 BTFP가 없었으므로 값이 0.0이다. 다음 줄은 BTFP 잔액의 최댓값(백만 달러)을 출력한다.
# %%
print(df0.head())
print(df0["H41RESPPALDKNWW"].max())
# %% [markdown]
# ```python
#       date  H41RESPPALDKNWW
# 0 2022-01-05              0.0
# 1 2022-01-12              0.0
# 2 2022-01-19              0.0
# 3 2022-01-26              0.0
# 4 2022-02-02              0.0
# ```
# %% [markdown]
# ### 3단계: 그래프 그리기
# plt.subplots(1, 2, ...)는 한 줄에 그림 두 개를 만든다. fig는 그림 전체, ax[0]은 왼쪽, ax[1]은 오른쪽 그림이다.
# figsize=(8, 4.5)는 가로 8인치, 세로 4.5인치이고, constrained_layout=True는 글자가 겹치지 않게 간격을 맞춘다.
#
# 왼쪽 그림(ax[0])에서 하는 일
# - plot(): x축에 날짜, y축에 BTFP 잔액을 놓고 파란 선(굵기 2)을 그린다.
#   잔액을 1e2(=100)로 나누어 백만 달러를 억 달러 단위로 바꾼다.
# - axhline(y=0, ...): 0 높이에 회색 점선을 긋는다.
# - x축에는 연도만 표시하고, y축 숫자에는 세 자리마다 쉼표를 넣는다(StrMethodFormatter).
# - 범례(선 이름 'BTFP' 상자)는 선과 겹치지 않는 오른쪽 위에 둔다.
# - 그림 왼쪽 위에 단위 (억 달러)를, 아래에 출처와 음영 설명을 적는다.
# - grid(False): 격자선을 그리지 않아 깔끔하게 보이게 한다.
# %%
fig, ax = plt.subplots(1, 2, figsize=(8, 4.5), constrained_layout=True)

ax[0].plot(df0["date"], df0["H41RESPPALDKNWW"] / 1e2, label="BTFP", color="blue", lw=2)
ax[0].axhline(y=0, color="gray", linestyle="--")

ax[0].xaxis.set_major_locator(mdates.YearLocator())

from matplotlib.ticker import StrMethodFormatter

ax[0].yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))  # Comma every 3 digits


ax[0].legend(loc="upper right")
ax[0].yaxis.label.set_visible(True)
ax[0].text(
    0,
    1.00,
    "(억 달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)

ax[0].text(
    0.0,
    -0.15,
    "출처: FRED, 음영은 BTFP 실시기간",
    transform=ax[0].transAxes,
    fontsize=10,
    ha="left",
)
ax[0].grid(False)
# %% [markdown]
# 오른쪽 그림(ax[1])은 x축에 날짜, y축에 실효연방기금금리를 놓고 파란 선을 그린다.
# 선 이름은 'Effective Federal Funds Rate'이고, 범례는 선이 없는 오른쪽 아래에 둔다.
# 나머지(0 점선, 단위, 출처)는 왼쪽 그림과 같다.
# %%
ax[1].plot(
    df1["date"],
    df1["RIFSPFFNB"],
    label="Effective Federal Funds Rate",
    color="blue",
    lw=2,
)
ax[1].axhline(y=0, color="gray", linestyle="--")
ax[1].legend(loc="lower right")
ax[1].xaxis.set_major_locator(mdates.YearLocator())

ax[1].text(
    0,
    1.00,
    "(%)",
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
    "출처: FRED, 음영은 BTFP 실시기간",
    transform=ax[1].transAxes,
    fontsize=10,
    ha="left",
)
ax[1].grid(False)

# %% [markdown]
# ### 음영 넣기
# 두 그림 모두에 BTFP를 운영한 기간(2023년 3월 12일 ~ 2024년 3월 11일)을 회색으로 칠한다.
# axvspan(시작일, 종료일, ...)은 두 날짜 사이를 세로로 칠하고, alpha=0.2는 색을 옅게(투명도 20%) 한다.
# %%
from datetime import datetime

shaded_periods = [(datetime(2023, 3, 12), datetime(2024, 3, 11))]

for i in [0, 1]:
    for start_date, end_date in shaded_periods:
        ax[i].axvspan(start_date, end_date, color="gray", alpha=0.2)

# %% [markdown]
# ### 4단계: 그림 저장
# 다른 그림 코드들은 마지막 줄의 plot_save() 한 줄로 그림을 저장한다(defs/plot_def.py).
# 이 파일은 저장 과정을 보여주려고 plot_save()가 하는 일을 코드에 그대로 풀어 적었다. 결과 파일도 같다.
# 1. 이 파일의 이름(f2_btfp)을 그대로 그림 파일 이름으로 쓴다.
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
    base_filename = "f2_btfp"

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
