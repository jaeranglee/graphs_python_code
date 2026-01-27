# %% [markdown]
# 그래프와 관련된 함수입니다.
#
# ## def nber_recession(start, end)
# 그래프에 미국의 경기침체기(NBER 기준)를 음영으로 넣어주는 함수
# 입력 파라미터 start, end가 반드시 있어야 합니다.
# 자료 시작일 start, 자료 종료일 end 날짜를 그래프와 같게 하여야 합니다.
#
# 다음과 같은 코드를 원하는 plot line 아래에 넣어야 합니다.
# ```python
# recession_periods = nber_recession(start=start, end=end)
# for peak, trough in recession_periods:
#    ax.axvspan(peak, trough, color='gray', alpha=0.3)
# ```
# ## def plot_save(i=None):
#
# 그래프를 파일로 저장하는 함수
# 그래프를 그리는 코드의 이름을 파일 이름으로 사용합니다.
# 현재보다 하위에 있는 'pic_jpg' 디렉토리에 '파일이름.jpg, 그리고
# 'pic_tif' 디렉토리에 '파일이름.tif'파일로 저장합니다.
# 입력 파라미터 i는 그림의 번호입니다.
# 그림을 한 개만 그리는 코드에는 i 값을 지정하지 않아도 됩니다.
# for 루프로 그림을 여러개 그리는 코드에는 코드의 루핑 횟수 값 지징변수를 가져와서 넣어야
# 그림별로 다른 파일로 저장됩니다.
# ```python
# # 그림이 한개 일 때
# plot_save()
#
# # 그림이 여러개 일 경우
# plot_save(i=i)

# ```
# %matplotlib inline
# %%

import platform
import os

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from matplotlib.ticker import StrMethodFormatter
from matplotlib.ticker import FuncFormatter

from datetime import date, timedelta
import matplotlib.dates as mdates

import pandas as pd

def set_fonts():

    # 후보 폰트 리스트 (운영체제별로 다르게 설치되어 있을 수 있음)
    font_candidates = [
        "AppleGothic",     # macOS
        "Malgun Gothic",   # Windows
        "NanumGothic",     # Linux (Colab 등)
        "DejaVu Sans"      # fallback (영문/일부 한글 지원)
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

from fred_api import fetch_fred_series

# USREC 기준으로 recession 음영 처리 (확장기: 0, 침체기: 1)
def nber_recession(start, end):

    # USREC 데이터 불러오기
    df_usrec = fetch_fred_series('USREC',start_date=start, end_date=end)

    recession_periods = []
    in_recession = False

    for i in range(len(df_usrec)):
        rec = df_usrec['USREC'].iloc[i]
        date = df_usrec['observation_date'].iloc[i]

        if rec == 1 and not in_recession:
            start = date
            in_recession = True
        elif rec == 0 and in_recession:
            end = date
            recession_periods.append((start, end))
            in_recession = False

    recession_periods = []
    in_recession = False

    for i in range(len(df_usrec)):
        rec = df_usrec['USREC'].iloc[i]
        date = df_usrec['observation_date'].iloc[i]

        if rec == 1 and not in_recession:
            start = date
            in_recession = True
        elif rec == 0 and in_recession:
            end = date
            recession_periods.append((start, end))
            in_recession = False

    # 만약 마지막 달까지 recession이면
    if in_recession:
        recession_periods.append((start, df_usrec['observation_date'].iloc[-1]))

    return(recession_periods)


def plot_save(i=None):

    # 저장 및 출력
    # python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
    import os
    from PIL import Image
    import inspect

    """
        이 함수를 호출한 .py 파일 이름을 기반으로 그래프를 tif, jpg로 저장합니다.
    """
    # 호출한 파일 경로 추출
    caller_frame = inspect.stack()[1]
    caller_filepath = caller_frame.filename
    base_filename = os.path.splitext(os.path.basename(caller_filepath))[0]

    # i가 있으면 _i 형식으로 suffix 추가
    suffix = f"_{i}" if i is not None else ""

    # 저장 경로 설정
    image_path_tif = f"pic_tif/{base_filename}{suffix}.tif"
    image_path_jpg = f"pic_jpg/{base_filename}{suffix}.jpg"

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
