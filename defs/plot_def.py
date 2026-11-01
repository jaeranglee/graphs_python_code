# %% [markdown]
# # 그래프 공통 함수
# ## file name
# - plot_def.py
#
# ## 기능
# - 한글 폰트 설정, 그래프 저장, 미국·한국 경기침체기 음영, y축 천 단위 콤마 함수 모음.
# - 그림 스타일: 기본(classic)·BIS·BOK·econ_chart. 스타일 함수 한 줄로 모양을 바꾸고, 각 스타일은 book(인쇄)·ppt(슬라이드) 판이 있다.
# - `from plot_def import *`로 `plt`, `pd`, `mdates`, `date`, `timedelta`, `StrMethodFormatter`, `FuncFormatter`,
#   `fetch_fred_series`도 같이 들어온다 (스크립트들이 이를 이용하므로 "안 쓰는" import라도 지우지 말 것).
#
# ## 그림 스타일
# `set_fonts()` 바로 다음에 스타일 함수를 한 번 부른다. 그림 코드는 그대로 두면, `plot_save()`가 저장 직전에
# 그림 크기·글자 크기·선 굵기·색·축·범례·출처 위치를 그 스타일로 다듬는다 (econ_chart만 전용 econ_ 함수로 직접 그림).
# 스타일 함수는 하나만 부른다. 나중에 부른 것이 앞의 것을 끈다.
#
# | 스타일 | 부르는 법 | 모양 | 어울리는 곳 |
# |---|---|---|---|
# | 기본(classic) | 부르지 않음 | matplotlib 기본 + 한글 폰트 + y축 쉼표 | 화면 확인, 책 『이야기로 풀어가는 현실 국제금융론』 그림 |
# | BIS | `set_bis_style(medium="book")` | 옅은 회색 바탕, 흰 가로 grid, 아래 축선만, 눈금 표시 없음, 범례 테두리 없음, 파랑·먹색 두 톤 | 두 톤으로 인쇄하는 책 |
# | BOK | `set_bok_style(tone1=None, tone2=None, medium="book", **tones)` | 한국은행 통화정책보고서풍: 흰 바탕, 좌·우·아래 축선과 안쪽 눈금, 오른쪽 눈금 반복, 범례는 위 가로 한 줄, 0선 검정, 1월마다 점선, 날짜 `24.1  7  25.1`, 출처 `자료:` | 보고서처럼 보이는 그림 |
# | econ_chart | `set_econ_chart_style(medium="ppt")` | 교과서 이론 도식: 왼쪽·아래 축선, 축 끝 *P*·*Y*, 남색 곡선, Times 이탤릭 라벨, 분홍 설명 상자 | 자료 없는 이론 그림(AD-AS, IS-LM 등) |
#
# **book과 ppt** (모양은 같고 크기·글자·선 굵기만 다름. 값은 `BIS_MEDIA`, `BOK_MEDIA`, `ECON_MEDIA`)
#
# | medium | 그림 크기(인치) | 글자 | 저장 이름 |
# |---|---|---|---|
# | `"book"` | 패널 1개 3.6×2.6, 2개 이상 5.6×2.4(BIS)·5.6×2.8(BOK), econ 3.6×3.0 | 7~8pt | BIS·BOK `<이름>`, econ `<이름>_book` |
# | `"ppt"` | 8.0×5.33 (4:3 슬라이드 내용 칸에 100%), econ 6.4×5.34 | 12~14pt (econ 22~24pt) | BIS `<이름>_ppt`, BOK·econ `<이름>` |
#
# - BIS·BOK는 스크립트의 `figsize`를 무시하고 위 크기로 바꾼다 (패널 수로 1개/2개 이상 판단).
# - BOK는 book·ppt 저장 이름이 같아 덮어쓴다. 두 판이 다 필요하면 `plot_save(name="…")`로 이름을 준다.
#
# **스타일이 잘 먹게 쓰는 법**
# - 색은 `color="blue"`, `"black"`, `"darkblue"`, `"gray"` 네 이름으로 쓴다. 스타일이 자기 색으로 바꾼다.
#   BIS: black→먹색 `#222222`, blue→파랑 `#1f5fbf`, darkblue→남색 `#1b3a5c`, gray→회색 (다른 색상은 쓰지 않음).
#   BOK: `tone1`, `tone2`, `tone3=` … 로 톤의 개수와 색을 정함(이름은 `BOK_COLORS` 키·black·matplotlib 색·hex).
#   스크립트 색 이름이 톤에 있으면 그 톤, 없으면 남은 톤을 차례로. 톤을 안 주면 book = black·blue, ppt = blue·orange·gray·sky.
# - 단위는 `ax.text(0, 1.00, "(%)", transform=ax.transAxes)` (BOK는 오른쪽 위에도 복사),
#   출처는 `ax.text(0, -0.12, "출처: …", transform=ax.transAxes)` (BIS는 작은 회색, BOK는 `자료:`로 바꿈).
# - 범례는 `ax.legend()`만 부르면 스타일이 새 글자 크기로 다시 만든다(twinx 선 포함). BOK는 그림 위로 옮긴다.
#
# ```python
# from plot_def import *
#
# set_fonts()
# set_bis_style(medium="book")          # BIS 책 판
# # set_bis_style(medium="ppt")         # BIS 슬라이드 판 → <이름>_ppt.jpg
# # set_bok_style(medium="book")        # BOK 책 판 (black·blue)
# # set_bok_style("blue", "orange", medium="ppt")   # BOK 슬라이드 판, 파랑·황갈색
#
# fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)   # 크기는 스타일이 바꿈
# ax.plot(df["observation_date"], df["UNRATE"], color="blue", label="실업률")
# ax.plot(df["observation_date"], df["FEDFUNDS"], color="black", label="연방기금금리")
# ax.text(0, 1.00, "(%)", transform=ax.transAxes, va="bottom")
# ax.text(0, -0.12, "출처: FRED", transform=ax.transAxes)
# ax.legend()
# plot_save()
# ```
#
# econ_chart (이론 도식):
# ```python
# import numpy as np
# set_fonts()
# set_econ_chart_style(medium="ppt")    # 책이면 "book" → <이름>_book.jpg
# fig, ax = econ_figure()
# Y = np.linspace(10, 90, 50)
# econ_line(ax, Y, 100 - Y)             # AD (남색). 이동 전 곡선은 tone="old"(회색)
# econ_line(ax, [50, 50], [5, 95])      # LRAS
# econ_text(ax, 88, 14, "$AD$"); econ_text(ax, 51, 92, "$LRAS$")
# econ_point(ax, 50, 50, "A")
# econ_guide(ax, [0, 50], [50, 50])     # 점 A에서 P축까지 파선
# econ_axes(ax, xlim=(0, 100), ylim=(0, 100), xticks={50: r"$\bar{Y}$"}, yticks={50: r"$P_1$"})
# plot_save()
# ```
#
# ## 출처
# - `nber_recession`: FRED `USREC`(NBER 경기침체 지표)를 `fetch_fred_series`로 받음
# - `korea_recession`: 통계청 기준순환일(정점·저점)을 코드에 직접 적어 둠
#
# ## 사용 예
# ```python
# # defs 경로 블록을 넣은 스크립트에서
# from plot_def import *
#
# set_fonts()                                   # 한글 폰트 (macOS: Apple SD Gothic Neo)
#
# fig, ax = plt.subplots(figsize=(8, 4.5))
# ax.plot(df["observation_date"], df["UNRATE"])
#
# for peak, trough in nber_recession(start=start, end=end):   # 미국 경기침체 음영
#     ax.axvspan(peak, trough, color="gray", alpha=0.3)
# # 한국: korea_recession(start, end)
#
# set_yaxis_comma(ax, 1)                        # y축 콤마, 소수 1자리 (생략하면 plot_save가 자동 적용)
# plot_save()                                   # 그림 1개
# # plot_save(i=i)                              # 한 스크립트에서 여러 그림
# ```
#
# ## 함수
# | Function | Returns | Description |
# |----------|---------|-------------|
# | `set_fonts()` | 없음 | 한글을 쓸 수 있는 폰트를 고른다 |
# | `nber_recession(start, end)` | `[(peak, trough), …]` | 미국 경기침체 구간. start, end는 그래프 기간과 같게 |
# | `korea_recession(start=None, end=None)` | `[(peak, trough), …]` | 한국 경기수축 구간 |
# | `set_yaxis_comma(ax=None, i=None)` | 없음 | y축 천 단위 콤마. `i`=소수 자리 (None이면 눈금에 맞춰 자동). `ax=None`이면 아직 안 정한 모든 축 |
# | `set_bis_style(medium="book")` | 없음 | (선택) BIS 보고서풍. set_fonts() 다음에 부르면 plot_save()가 저장 직전에 축선·grid·색·출처 글씨를 다듬는다. medium="book"(책 인쇄 크기)/"ppt"(강의 슬라이드, 파일 이름 끝 `_ppt`) |
# | `set_bok_style(tone1=None, tone2=None, medium="book", **tones)` | 없음 | (선택) 한국은행 통화정책보고서풍. set_bis_style() 대신 부름. medium="book"(책, 기본 black·blue)/"ppt"(강의 슬라이드, 기본 보고서 원래 색). tone1, tone2, tone3…으로 톤 개수·색 지정 |
# | `set_econ_chart_style(medium="ppt")` | 없음 | (선택) 이론 도식(AD-AS 등)용. 거시경제학 슬라이드의 객체 그림(11장 LRAS)과 같은 글꼴·색·비율. medium="ppt"/"book"(스타일 같고 크기·글자·선 굵기만 다름). book이면 plot_save가 파일 이름 끝에 `_book`을 붙임 |
# | `econ_figure(left_pad=0)` | `fig, ax` | econ_chart 크기의 그림과 축 (축 비율 고정). left_pad = 긴 y축 라벨용 왼쪽 여백(인치) |
# | `econ_axes(ax, xlim, ylim, xticks=None, yticks=None, xlabel="Y", ylabel="P")` | 없음 | 왼쪽·아래 축선, 축 끝의 *Y*·*P*, 눈금 없이 라벨만 (`{값: "수식"}`) |
# | `econ_line(ax, x, y, tone="curve", **kw)` / `econ_guide(ax, xs, ys)` | Line2D | 곡선(tone: curve=남색, old=이동 전 회색) / 가는 검정 파선 보조선 |
# | `econ_text(ax, x, y, s, kind="curve", **kw)` / `econ_note(ax, x, y, s, **kw)` | Text | 곡선 이름(Times 이탤릭) / 분홍 설명 상자 |
# | `econ_dot(ax, x, y)` / `econ_point(ax, x, y, name, dx=2, dy=2)` / `econ_arrow(ax, start, end)` / `econ_path_arrow(ax, xs, ys)` | | 점 / 점 + 이름(A, B, C) / 이동 방향 화살표 / 선을 따라 찍는 화살촉 |
# | `econ_ramp(frame, start, end)` | 0~1 | 애니메이션 진행률 (start 전 0, end 뒤 1) |
# | `econ_animate(fig, update, frames, fps=15)` | 없음 | ppt: `update(frame)` 장면들을 `pic_gif/<스크립트이름>.gif`로(반복 없이 한 번 재생), book: 마지막 장면을 `plot_save`처럼 저장 |
# | `plot_save(i=None, name=None)` | 없음 | `pic_tif/<스크립트이름>[_i].tif`(LZW 무손실), `pic_jpg/<스크립트이름>[_i].jpg`를 300 dpi로 저장하고 `plt.show()` |
#
# - 저장 폴더는 현재 폴더 기준이므로 스크립트를 그 폴더에서 실행해야 한다.
#
# ## 사용하는 곳
# - 거의 모든 그래프 스크립트 (380여 개)
# %%

import inspect
import math
import os
import platform
from datetime import date, timedelta

import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import Formatter, FuncFormatter, NullLocator, StrMethodFormatter
from PIL import Image

pd.set_option("display.width", None)
pd.set_option("display.expand_frame_repr", False)


def set_fonts():

    # 후보 폰트 리스트 (운영체제별로 다르게 설치되어 있을 수 있음)
    font_candidates = [
        "Apple SD Gothic Neo",  # macOS (굵은 글꼴 포함)
        "AppleGothic",  # macOS (굵은 글꼴 없음)
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


from fred_api import fetch_fred_series


# USREC 기준으로 recession 음영 처리 (확장기: 0, 침체기: 1)
def nber_recession(start, end):

    # USREC 데이터 불러오기
    df_usrec = fetch_fred_series("USREC", start_date=start, end_date=end)

    recession_periods = []
    in_recession = False

    for i in range(len(df_usrec)):
        rec = df_usrec["USREC"].iloc[i]
        date = df_usrec["observation_date"].iloc[i]

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
        rec = df_usrec["USREC"].iloc[i]
        date = df_usrec["observation_date"].iloc[i]

        if rec == 1 and not in_recession:
            start = date
            in_recession = True
        elif rec == 0 and in_recession:
            end = date
            recession_periods.append((start, end))
            in_recession = False

    # 만약 마지막 달까지 recession이면
    if in_recession:
        recession_periods.append((start, df_usrec["observation_date"].iloc[-1]))

    return recession_periods


class _CommaFormatter(Formatter):
    """천 단위 콤마(,) 서식.
    decimals=None이면 눈금 값을 정확히 나타내는 최소 소수점 자리수를 자동으로 고른다.
    (예: 눈금이 2, 3, 4 → 0자리 / 2.5, 3.0 → 1자리 / 2.25, 2.50 → 2자리)"""

    def __init__(self, decimals=None):
        self.decimals = decimals
        self._auto = 0

    @staticmethod
    def _auto_decimals(values):
        vals = [v for v in values if math.isfinite(v)]
        for d in range(7):
            if all(abs(v - round(v, d)) <= 1e-9 * max(1.0, abs(v)) for v in vals):
                return d
        return 6

    def format_ticks(self, values):
        if self.decimals is None:
            self._auto = self._auto_decimals(values)
        return [self(v) for v in values]

    def __call__(self, x, pos=None):
        d = self._auto if self.decimals is None else self.decimals
        return f"{x:,.{d}f}"


def set_yaxis_comma(ax=None, i=None):
    """
    y축 숫자에 천 단위 콤마(,)를 추가하는 함수.
    - ax: 적용할 축 (None이면 현재 Figure의 미적용된 모든 축, 리스트/튜플로 여러 축 입력 가능)
    - i: 소수점 이하 자리수 (None이면 눈금 간격에 맞춰 자동, 1이면 1자리, 2이면 2자리 등)
    """
    formatter = _CommaFormatter(i)

    # 사용자가 직접 ax를 지정해서 호출했는지 여부
    is_manual_call = ax is not None

    # 적용할 축 수집
    if ax is None:
        target_axes = plt.gcf().axes  # 자동 호출: 모든 축
    elif isinstance(ax, (list, tuple)):
        target_axes = ax  # 리스트 형태
    else:
        target_axes = [ax]  # 단일 축

    for a in target_axes:
        # ★ 핵심 포인트: 자동 호출(plot_save 안에서 실행)일 때,
        # 이미 수동으로 포맷을 지정한 축이면 덮어쓰지 않고 건너뜀(Continue)
        if not is_manual_call and getattr(a, "_custom_comma_formatted", False):
            continue

        a.yaxis.set_major_formatter(formatter)

        # 수동으로 지정한 경우, 꼬리표를 달아서 나중에 덮어써지지 않게 보호함
        if is_manual_call:
            a._custom_comma_formatted = True


# BIS 보고서풍 스타일 (opt-in)
# set_fonts() 다음에 set_bis_style()을 부르면 plot_save()가 저장 직전에 그림을 BIS풍으로 다듬는다:
# 위·왼쪽·오른쪽 축선 제거, 옅은 회색 바탕에 흰 가로 grid만, 눈금 표시 없음, 범례 테두리 없음,
# 출처(축 아래 텍스트)는 작은 회색, 그림 크기는 인쇄 크기(BIS_FIGSIZE)로 바꾸고 글자는 8pt(출처 7pt), 색은 출판사 요청에 따라 파랑·검정 두 톤만 씀:
# black→먹색, blue→파랑, darkblue→남색, gray→회색(먹색의 옅은 톤)
BIS_COLORS = {
    "navy": "#1b3a5c",
    "blue": "#1f5fbf",
    "sky": "#8fb8de",
    "gray": "#8c8c8c",
    "ink": "#222222",
    "muted": "#6b6b6b",
    "grid": "#ffffff",
    "panel": "#efefef",
    "axis": "#888888",
}
_BIS_COLOR_MAP = {
    "black": BIS_COLORS["ink"],
    "blue": BIS_COLORS["blue"],
    "darkblue": BIS_COLORS["navy"],
    "gray": BIS_COLORS["gray"],
}
_bis_on = False
_bis_medium = "book"


def set_bis_style(medium="book"):
    # medium: "book"(책 인쇄 크기, 기본) 또는 "ppt"(4:3 강의 슬라이드). 스타일은 같고 크기·글자·선 굵기만 다름 (BIS_MEDIA)
    # ppt 판은 책 그림(TIFF)을 덮어쓰지 않도록 plot_save가 파일 이름 끝에 _ppt를 붙임
    global _bis_on, _bok_on, _econ_on, _bis_medium
    if medium not in BIS_MEDIA:
        raise ValueError(f"set_bis_style(): medium은 {list(BIS_MEDIA)} 중 하나")
    _bis_on, _bok_on, _econ_on, _bis_medium = True, False, False, medium
    from cycler import cycler

    c = BIS_COLORS
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.edgecolor": c["axis"],
            "axes.prop_cycle": cycler(
                color=[c["ink"], c["blue"], c["navy"], c["sky"], c["gray"]]
            ),
            "text.color": c["ink"],
            "xtick.color": c["ink"],
            "ytick.color": c["ink"],
            "xtick.major.size": 0,
            "ytick.major.size": 0,
            "legend.frameon": False,
        }
    )


def _bis_color(color):
    from matplotlib.colors import to_hex

    try:
        h = to_hex(color)
    except ValueError:
        return color
    for name, new in _BIS_COLOR_MAP.items():
        if h == to_hex(name):
            return new
    return color


def _bis_text_color(color):
    from matplotlib.colors import to_hex

    try:
        if to_hex(color) == "#000000":
            return BIS_COLORS["ink"]
    except ValueError:
        pass
    return _bis_color(color)


# 인쇄 크기(인치)로 바로 그려서 Word에 100%로 넣음: 축소되지 않으므로 글자가 그대로 7~8pt로 찍힘
# book: 패널 1개 = 본문 절반 폭, 2개 이상 = 본문의 약 90% 폭
# ppt: 4:3 강의 슬라이드의 내용 개체 틀(8.0×5.33in)에 100%로 넣는 크기와 화면용 글자 (BOK ppt와 같은 크기)
# lw_scale = 스크립트 선 굵기에 곱하는 배수, axis = 아래 축선 굵기(pt), grid = 흰 grid 굵기(pt),
# scale = 출처 간격(pt)에 곱하는 배수
BIS_MEDIA = {
    "book": {
        "figsize": {1: (3.6, 2.6), 2: (5.6, 2.4)},
        "fontsize": {"tick": 8, "text": 8, "legend": 8, "source": 7},
        "lw_scale": 0.8, "axis": 0.8, "grid": 1.0, "scale": 1,
    },
    "ppt": {
        "figsize": {1: (8.0, 5.33), 2: (8.0, 5.33)},
        "fontsize": {"tick": 14, "text": 14, "legend": 14, "source": 12},
        "lw_scale": 1.6, "axis": 1.2, "grid": 1.6, "scale": 1.75,
    },
}
# 예전 이름 (book 값)
BIS_FIGSIZE = BIS_MEDIA["book"]["figsize"]
BIS_FONTSIZE = BIS_MEDIA["book"]["fontsize"]
BIS_LW_SCALE = BIS_MEDIA["book"]["lw_scale"]


def _bis_resize(fig):
    from matplotlib.transforms import offset_copy

    m = BIS_MEDIA[_bis_medium]
    f, k = m["fontsize"], m["scale"]
    panels = [ax for ax in fig.axes if ax.patch.get_visible()]
    fig.set_size_inches(*m["figsize"][min(len(panels), 2)])

    for ax in fig.axes:
        ax.tick_params(labelsize=f["tick"])
        ax.xaxis.label.set_fontsize(f["text"])
        ax.yaxis.label.set_fontsize(f["text"])

        for line in ax.get_lines():
            line.set_linewidth(line.get_linewidth() * m["lw_scale"])

        for t in ax.texts:
            x, y = t.get_position()
            if not t.get_transform().contains_branch(ax.transData) and y < 0:
                # 출처: 축 아래 고정 간격(pt)에 둠 (y=-0.09 → 첫 줄, 더 아래면 다음 줄)
                t.set_fontsize(f["source"])
                t.set_position((x, 0))
                t.set_transform(
                    offset_copy(ax.transAxes, fig=fig, y=(-14 + (y + 0.09) * 180) * k, units="points")
                )
            else:
                t.set_fontsize(f["text"])

        # 범례는 글자 크기에 맞춰 다시 만듦 (기호 길이·간격이 처음 글자 크기로 고정되므로)
        leg = ax.get_legend()
        if leg:
            # 범례 복사본 대신 원래 그린 선을 라벨로 찾아 씀 (twinx 축의 선 포함)
            artists = {}
            for a in fig.axes:
                for h, lab in zip(*a.get_legend_handles_labels()):
                    artists.setdefault(lab, h)
            labels = [t.get_text() for t in leg.get_texts()]
            ax.legend(
                [artists[lab] for lab in labels],
                labels,
                loc=leg._loc,
                # 기준점은 축 좌표로 다시 지정 (이전 범례의 변환을 넘기면 위치가 엉뚱해짐)
                bbox_to_anchor=(
                    leg._bbox_to_anchor._bbox.bounds
                    if leg._bbox_to_anchor is not None
                    else None
                ),
                bbox_transform=ax.transAxes,
                ncols=leg._ncols,
                fontsize=f["legend"],
            )

    for t in fig.texts:
        t.set_fontsize(f["text"])


def _bis_restyle(fig):
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    c = BIS_COLORS
    m = BIS_MEDIA[_bis_medium]
    _bis_resize(fig)

    for ax in fig.axes:
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(c["axis"])
        ax.spines["bottom"].set_linewidth(m["axis"])
        ax.tick_params(length=0, colors=c["ink"])

        # 옅은 회색 바탕 + 흰 grid는 바탕 축에만 (twinx 축은 patch가 안 보임)
        ax.grid(False)
        if ax.patch.get_visible():
            ax.set_facecolor(c["panel"])
            ax.yaxis.grid(True, color=c["grid"], lw=m["grid"], ls="-")
            ax.set_axisbelow(True)

        for line in ax.get_lines():
            # axhline 같은 기준선(x가 축 좌표 0~1)은 가는 회색 실선
            if not line.get_transform().contains_branch(ax.transData) and list(
                line.get_xdata()
            ) == [
                0,
                1,
            ]:
                line.set(color=c["axis"], ls="-", lw=m["axis"])
            else:
                line.set_color(_bis_color(line.get_color()))
        for patch in ax.patches:
            patch.set_facecolor(_bis_color(patch.get_facecolor()))
        for coll in ax.collections:
            fc = coll.get_facecolor()
            if len(fc):
                coll.set_facecolor([_bis_color(f) for f in fc])

        # 출처처럼 축 아래(y<0)에 놓인 텍스트는 작은 회색
        for t in ax.texts:
            if (
                not t.get_transform().contains_branch(ax.transData)
                and t.get_position()[1] < 0
            ):
                t.set(color=c["muted"])
            else:
                t.set_color(_bis_text_color(t.get_color()))

        leg = ax.get_legend()
        if leg:
            leg.set_frame_on(False)
            for h in leg.legend_handles:
                if isinstance(h, Line2D):
                    h.set_color(_bis_color(h.get_color()))
                elif isinstance(h, Patch):
                    h.set_facecolor(_bis_color(h.get_facecolor()))
            for t in leg.get_texts():
                t.set_color(c["ink"])

    for t in fig.texts:
        t.set_color(_bis_color(t.get_color()))


# 한국은행 통화정책보고서풍 스타일 (opt-in, 통화신용정책보고서 2026.9 PDF에서 색·선·글자 크기를 실측)
# set_fonts() 다음에 set_bok_style()을 부르면 plot_save()가 저장 직전에 그림을 다듬는다:
# 흰 바탕, grid 없음, 왼쪽·오른쪽·아래 축선(검정 가는 선)과 안쪽 눈금, 오른쪽에도 같은 눈금 숫자와 단위,
# 범례는 플롯 위 가로 한 줄, 0선은 검정 실선, 날짜축은 1월마다 점선 + "24.1  7  25.1" 라벨, 출처는 "자료:".
# 색: tone 인자로 정함. 기본은 book = 출판사 두 톤 black·blue, ppt = 보고서 원래 색 blue·orange·gray·sky.
# 크기는 책 판형(BIS와 같은 폭)에 맞추고
# 글자·선 굵기는 보고서(그림 박스 폭 190pt)의 비율을 그 폭으로 키운 값
BOK_COLORS = {
    "blue": "#145faa",
    "orange": "#d2915a",
    "navy": "#1e5199",
    "sky": "#6182d6",
    "gray": "#8c8c8c",
    "shade": "#c8c8c8",
    "ink": "#000000",
}
_BOK_COLOR_MAP = {}  # set_bok_style()이 tone에 맞춰 채움
# medium별 크기: book = 책 판형(패널 1개는 BIS와 같은 크기), ppt = 4:3 강의 슬라이드의 내용 개체 틀(8.0×5.33in)에
# 100%로 넣는 크기와 화면용 글자. scale은 눈금 길이·점선 무늬·범례/출처 간격(pt)에 곱하는 배수
BOK_MEDIA = {
    "book": {
        "figsize": {1: (3.6, 2.6), 2: (5.6, 2.8)},
        "fontsize": {"tick": 7, "unit": 7, "legend": 7.5, "source": 7.5},
        "lw": {"data": 1.4, "axis": 0.5},
        "scale": 1,
        "tones": ("black", "blue"),  # 출판사 두 톤
    },
    "ppt": {
        "figsize": {1: (8.0, 5.33), 2: (8.0, 5.33)},
        "fontsize": {"tick": 14, "unit": 14, "legend": 14, "source": 12},
        "lw": {"data": 2.5, "axis": 1.0},
        "scale": 2,
        # 보고서 원래 색 (두 톤 제한 없음). 실측은 blue·orange, 3번째부터는 같은 계열에서 고름
        "tones": ("blue", "orange", "gray", "sky"),
    },
}
_bok_on = False
_bok_medium = "book"


def _bok_tone(t):
    # tone 이름 → 보고서 색 (black은 먹색, 그 밖의 이름·hex는 그대로)
    return BOK_COLORS.get(t, BOK_COLORS["ink"] if t == "black" else t)


def _same_color(a, b):
    from matplotlib.colors import to_hex

    try:
        return a == b or to_hex(a) == to_hex(b)
    except ValueError:
        return False


def set_bok_style(tone1=None, tone2=None, medium="book", **more_tones):
    # tone1, tone2, tone3, … : 쓸 색(톤)의 개수와 색. 이름은 BOK_COLORS 키(blue, orange, navy, sky, gray)·
    # black·matplotlib 색 이름·hex. tone1만 주면 한 톤. 하나도 안 주면 medium의 기본 톤(BOK_MEDIA):
    # book = black·blue (출판사 두 톤), ppt = blue·orange·gray·sky (보고서 원래 색)
    # 스크립트의 색 이름(blue, black, darkblue, gray)이 tone에 있으면 그 톤으로, 없으면 남은 톤을 차례로 씀
    # 예) 기본(black, blue): blue→파랑, black→먹색 / (blue, orange): blue→파랑, black→황갈색
    # medium: "book"(책 판형) 또는 "ppt"(강의 슬라이드). 스타일은 같고 크기·글자·선 굵기만 다름 (BOK_MEDIA)
    global _bis_on, _bok_on, _econ_on, _bok_medium
    if medium not in BOK_MEDIA:
        raise ValueError(f"set_bok_style(): medium은 {list(BOK_MEDIA)} 중 하나")
    _bis_on, _bok_on, _econ_on, _bok_medium = False, True, False, medium
    from cycler import cycler

    bad = [k for k in more_tones if not (k.startswith("tone") and k[4:].isdigit())]
    if bad:
        raise TypeError(f"set_bok_style(): tone3, tone4, … 만 받음: {bad}")
    extra = [more_tones[k] for k in sorted(more_tones, key=lambda k: int(k[4:]))]
    tones = [t for t in (tone1, tone2, *extra) if t is not None] or list(
        BOK_MEDIA[medium]["tones"]
    )

    slots = ["blue", "black", "darkblue", "gray"]
    _BOK_COLOR_MAP.clear()
    rest = list(tones)
    for slot in slots:
        hit = next((t for t in rest if _same_color(t, slot)), None)
        if hit is not None:
            _BOK_COLOR_MAP[slot] = _bok_tone(hit)
            rest.remove(hit)
    for slot in slots:
        if slot not in _BOK_COLOR_MAP and rest:
            _BOK_COLOR_MAP[slot] = _bok_tone(rest.pop(0))
    # 남은 darkblue·gray는 다른 색상(hue)을 들이지 않도록 진파랑·회색으로
    _BOK_COLOR_MAP.setdefault("darkblue", BOK_COLORS["navy"])
    _BOK_COLOR_MAP.setdefault("gray", BOK_COLORS["gray"])

    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.prop_cycle": cycler(color=[_bok_tone(t) for t in tones]),
            "xtick.direction": "in",
            "ytick.direction": "in",
            "legend.frameon": False,
        }
    )


def _bok_color(color):
    from matplotlib.colors import to_hex

    try:
        h = to_hex(color)
    except ValueError:
        return color
    for name, new in _BOK_COLOR_MAP.items():
        if h == to_hex(name):
            return new
    return color


def _bok_date_label(x, pos=None):
    # 1월(또는 첫 눈금)만 "24.1", 나머지는 월만 "7"
    d = mdates.num2date(x)
    return f"{d.year % 100}.{d.month}" if d.month == 1 or pos == 0 else f"{d.month}"


def _bok_restyle(fig):
    from matplotlib.layout_engine import ConstrainedLayoutEngine
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import FixedFormatter
    from matplotlib.transforms import offset_copy

    m = BOK_MEDIA[_bok_medium]
    c, f, lw, k = BOK_COLORS, m["fontsize"], m["lw"], m["scale"]
    panels = [ax for ax in fig.axes if ax.patch.get_visible()]
    fig.set_size_inches(*m["figsize"][min(len(panels), 2)])
    has_twin = len(panels) < len(fig.axes)
    # 크기를 바꾼 뒤 범례·제목·출처 자리를 다시 잡도록 constrained layout (스크립트의 tight_layout은 크기 변경 전 값)
    if not isinstance(fig.get_layout_engine(), ConstrainedLayoutEngine):
        fig.set_layout_engine("constrained")
    # 점선 무늬(pt): 보고서 실측 1.47/1.10 (matplotlib은 선 굵기를 곱하므로 나눠 줌)
    dotted = (0, (1.5 * k / lw["axis"], 1.1 * k / lw["axis"]))
    has_unit = set()  # 단위 텍스트가 있는 축 (범례를 그 위로 띄움)
    sources = []  # (축, 텍스트, x, y): 축 아래 출처

    for ax in fig.axes:
        ax.grid(False)
        ax.spines["top"].set_visible(False)
        for side in ("left", "right", "bottom"):
            ax.spines[side].set(color=c["ink"], linewidth=lw["axis"])
        # 오른쪽에도 같은 눈금 숫자: twinx가 없고, 패널 2개 이하(3개 이상은 이웃 패널과 부딪힘), 숫자 눈금일 때만
        # (이론 도식의 P₁ 같은 고정 라벨은 반복하지 않음)
        mirror = (
            not has_twin
            and len(panels) <= 2
            and not isinstance(ax.yaxis.get_major_formatter(), FixedFormatter)
        )
        # 오른쪽 눈금: 복사본이면 켬, twinx 축(배경 투명)은 그대로, 그 밖은 끔
        # (tick_params에 None을 주면 "그대로"가 아니라 꺼지므로 키 자체를 뺌)
        side = (
            dict(right=True, labelright=True) if mirror
            else {} if not ax.patch.get_visible()
            else dict(right=False, labelright=False)
        )
        ax.tick_params(
            which="both", direction="in", colors=c["ink"], width=lw["axis"],
            labelsize=f["tick"], top=False, **side,
        )
        ax.tick_params(which="major", length=3 * k)
        ax.tick_params(which="minor", length=1.5 * k)

        for line in ax.get_lines():
            labeled = not line.get_label().startswith("_")
            # axhline·axvline 같은 기준선(한쪽이 축 좌표)은 검정 가는 선, 선 모양은 그대로
            # (범례 라벨이 있으면 LRAS처럼 axvline으로 그린 곡선이므로 데이터 선으로 봄)
            if not line.get_transform().contains_branch(ax.transData) and not labeled:
                line.set(color=c["ink"], lw=lw["axis"])
            # 라벨 없는 점선·파선은 보조선: 가늘게
            elif not labeled and line.get_linestyle() not in ("-", "solid"):
                line.set(color=_bok_color(line.get_color()), lw=lw["axis"] * 1.5)
            else:
                line.set(color=_bok_color(line.get_color()), lw=lw["data"])
        for patch in ax.patches:
            patch.set_facecolor(_bok_color(patch.get_facecolor()))
        for coll in ax.collections:
            fc = coll.get_facecolor()
            if len(fc):
                coll.set_facecolor([_bok_color(x) for x in fc])
            ec = coll.get_edgecolor()
            if len(ec):
                coll.set_edgecolor([_bok_color(x) for x in ec])

        if not ax.patch.get_visible():
            # twinx 축: 오른쪽 위 단위만 왼쪽 단위와 같은 글자로 (나머지 처리는 바탕 축에서)
            for t in ax.texts:
                if t.get_transform() is ax.transAxes and t.get_position()[1] >= 1:
                    t.set(fontsize=f["unit"], color=c["ink"])
            continue

        # 0선: 0이 축 범위 안에 있으면 검정 가는 실선
        lo, hi = ax.get_ylim()
        if lo < 0 < hi:
            ax.axhline(0, color=c["ink"], lw=lw["axis"], zorder=1.5)

        # 날짜축: 눈금은 1·7월(2년 이하는 분기 초), "24.1  7" 라벨, 1월마다 세로 점선
        # 5년 넘으면 연도 눈금 "%y"(라벨이 12개 이하가 되게 1·2·5·10년 간격), 점선은 매년 눈금일 때만
        if isinstance(ax.xaxis.get_major_formatter(), (mdates.DateFormatter, mdates.AutoDateFormatter)):
            x0, x1 = ax.get_xlim()
            months = (x1 - x0) / 30.44
            step = next(b for b in (1, 2, 5, 10, 20) if months / 12 / b <= 12)
            # 스크립트가 연 눈금(YearLocator)을 골랐으면 연간 자료: 짧은 기간도 연도 눈금
            yearly = isinstance(ax.xaxis.get_major_locator(), mdates.YearLocator)
            if months <= 60 or step == 1:
                for y in range(mdates.num2date(x0).year + 1, mdates.num2date(x1).year + 1):
                    xv = mdates.date2num(pd.Timestamp(y, 1, 1))
                    if x0 < xv < x1:
                        ax.axvline(xv, color=c["ink"], lw=lw["axis"], ls=dotted, zorder=1.5)
            if months > 60 or yearly:
                ax.xaxis.set_major_locator(mdates.YearLocator(step))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%y"))
                ax.xaxis.set_minor_locator(
                    mdates.YearLocator() if step > 1 else NullLocator()
                )
            else:
                ax.xaxis.set_major_locator(
                    mdates.MonthLocator(bymonth=(1, 4, 7, 10) if months <= 24 else (1, 7))
                )
                ax.xaxis.set_major_formatter(FuncFormatter(_bok_date_label))
                ax.xaxis.set_minor_locator(mdates.MonthLocator())
            ax.set_xlim(x0, x1)

        for t in list(ax.texts):
            x, y = t.get_position()
            # 축 좌표(transAxes)로 놓인 텍스트만 단위·출처로 봄 (annotate 라벨 등 데이터 위치 텍스트는 그대로)
            if t.get_transform() is not ax.transAxes:
                continue
            if y < 0:
                # 출처 → "자료:". 자리는 레이아웃을 잡은 뒤 축 아래 장식(눈금 숫자·x축 라벨) 바로 밑에 둠
                # 긴 출처가 패널 폭으로 잡혀 이웃 패널을 밀어내지 않도록 레이아웃 계산에서 뺌
                t.set_text(t.get_text().replace("출처:", "자료:"))
                t.set(fontsize=f["source"], color=c["ink"], va="top")
                t.set_in_layout(False)
                sources.append((ax, t, x, y))
            elif y >= 1:
                # 단위: 왼쪽 위, 오른쪽 눈금이 있으면 오른쪽 위에도
                t.set(fontsize=f["unit"], color=c["ink"])
                has_unit.add(ax)
                if mirror and x == 0:
                    ax.text(1, y, t.get_text(), ha="right", va="bottom",
                            fontsize=f["unit"], color=c["ink"], transform=ax.transAxes)

    # 범례: 원래 그린 선을 라벨로 찾아 플롯 위(단위 줄 위)에 가로 한 줄로 다시 만듦
    artists = {}
    for a in fig.axes:
        for h, lab in zip(*a.get_legend_handles_labels()):
            artists.setdefault(lab, h)
    # twinx 축의 범례는 바탕 축 범례에 합침 (둘 다 플롯 위 가운데로 가면 겹침), 라벨에 좌축·우축 표시
    for tw in [a for a in fig.axes if not a.patch.get_visible() and a.get_legend()]:
        base_ax = next((p for p in panels if p.get_shared_x_axes().joined(p, tw)), None)
        if base_ax is None:
            continue
        left = [t.get_text() for t in base_ax.get_legend().get_texts()] if base_ax.get_legend() else []
        right = [t.get_text() for t in tw.get_legend().get_texts()]
        tw.get_legend().remove()
        shown = [f"{lab} (좌축)" for lab in left] + [f"{lab} (우축)" for lab in right]
        for lab, s in zip(left + right, shown):
            artists[s] = artists[lab]
        base_ax.legend([artists[s] for s in shown], shown)
    renderer = fig.canvas.get_renderer()
    legend_h = {}  # 축별 범례 높이(pt)
    # 범례 밑단: 어느 패널이든 단위 줄이 있으면 모든 패널을 그 위로 (패널끼리 범례 높이를 맞춤)
    base = (f["unit"] + 3 * k) if has_unit else 3 * k
    for ax in fig.axes:
        leg = ax.get_legend()
        if not leg:
            continue
        labels = [t.get_text() for t in leg.get_texts()]
        for ncols in (len(labels), 1):
            leg = ax.legend(
                [artists[lab] for lab in labels], labels,
                loc="lower center", bbox_to_anchor=(0.5, 1),
                bbox_transform=offset_copy(ax.transAxes, fig=fig, y=base, units="points"),
                ncols=ncols, fontsize=f["legend"], borderaxespad=0,
                handlelength=1.6, columnspacing=1.2, frameon=False,
            )
            # 한 줄이 패널보다 넓으면 세로로
            if leg.get_window_extent(renderer).width <= ax.get_window_extent(renderer).width:
                break
        for h in leg.legend_handles:
            if isinstance(h, Line2D):
                h.set_color(_bok_color(h.get_color()))
            elif isinstance(h, Patch):
                h.set_facecolor(_bok_color(h.get_facecolor()))
        for t in leg.get_texts():
            t.set_color(c["ink"])
        legend_h[ax] = leg.get_window_extent(renderer).height * 72 / fig.dpi

    # 줄 수가 달라도 범례 윗단이 같도록 가장 높은 범례의 위쪽 끝에 맞춰 위에서 매달음
    top = base + max(legend_h.values(), default=0)
    for ax in legend_h:
        leg = ax.get_legend()
        leg.set_loc("upper center")
        leg.set_bbox_to_anchor(
            (0.5, 1), transform=offset_copy(ax.transAxes, fig=fig, y=top, units="points")
        )

    # 제목이 있으면 범례 위로 올림 (위에서부터 제목, 범례, 단위, 플롯)
    # 패널마다 범례 높이가 달라도 제목 높이가 같도록 가장 큰 간격을 모든 제목에 씀
    titled = [ax for ax in fig.axes if ax.get_title()]
    if titled:
        pad = top + 4 * k if legend_h else (f["unit"] if has_unit else 0) + 6
        for ax in titled:
            title = ax.title
            ax.set_title(
                title.get_text(), pad=pad,
                fontsize=title.get_fontsize(), fontweight=title.get_fontweight(),
            )

    for t in fig.texts:
        t.set(fontsize=f["unit"], color=c["ink"])

    # 출처: 그림 아래쪽에 출처 줄 수만큼 자리를 비우고, 레이아웃을 한 번 돌린 뒤
    # 각 축의 아래 장식 끝(눈금 숫자·x축 라벨) 바로 밑에 그림 좌표로 고정 (축 하나에 여러 줄이면 y 순서대로 쌓음)
    if sources:
        H = fig.get_figheight() * 72  # pt
        line = f["source"] * 1.35
        gap = 3 * k
        per_ax = {}
        for ax, t, x, y in sources:
            per_ax.setdefault(ax, []).append((y, x, t))
        # 텍스트 안의 줄바꿈(\n)까지 세어 출처 전체 높이를 잡음
        nlines = lambda t: t.get_text().count("\n") + 1
        n = max(sum(nlines(t) for _, _, t in v) for v in per_ax.values())
        bottom = (n * line + gap + 2 * k) / H
        fig.get_layout_engine().set(rect=(0, bottom, 1, 1 - bottom))
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        for ax, items in per_ax.items():
            y0 = ax.get_tightbbox(r, for_layout_only=True).y0 / fig.bbox.height
            pos = ax.get_position()
            used = 0  # 위에 놓인 출처들이 차지한 줄 수
            for y, x, t in sorted(items, key=lambda v: -v[0]):
                t.set_transform(fig.transFigure)
                t.set_position((pos.x0 + x * pos.width, y0 - (gap + used * line) / H))
                used += nlines(t)


# 이론 도식 스타일 (opt-in): 거시경제학 11장 31쪽(LRAS) 슬라이드의 객체 그림을 실측
# 축선 검정 1pt(왼쪽·아래만), 눈금 표시 없음, 축 끝에 굵은 이탤릭 P·Y, 곡선은 남색 #000082 2.25pt,
# 곡선 이름은 곡선 끝에 이탤릭, Ȳ·P₁ 같은 라벨은 수식 편집기처럼 Times 굵은 이탤릭, 설명 상자는 분홍 #FFCCCC
# 제목·범례·grid는 쓰지 않음 (슬라이드 제목과 곡선 이름이 대신함)
# Tahoma 이탤릭 파일이 macOS에 없어 라틴 글자는 Times New Roman 이탤릭으로 씀
ECON_COLORS = {"curve": "#000082", "old": "#8c8c8c", "ink": "#000000", "note": "#FFCCCC"}
# ppt = 슬라이드 내용 개체 틀(높이 5.34in)에 100%로 넣는 크기, book = 책 판형(BOK book과 같은 폭·글자·선 굵기)
# 축 상자 비율은 슬라이드 객체 그림의 축(4.91×4.31in)과 같게 ECON_AXES_RECT로 고정
ECON_MEDIA = {
    "ppt": {
        "figsize": (6.4, 5.34),
        "fontsize": {"axis": 24, "curve": 23, "tick": 22, "note": 14},
        "lw": {"curve": 2.25, "axis": 1.0, "guide": 1.0},
        "marker": 60,
    },
    "book": {
        "figsize": (3.6, 3.0),
        "fontsize": {"axis": 8, "curve": 7.5, "tick": 7.5, "note": 7},
        "lw": {"curve": 1.4, "axis": 0.5, "guide": 0.5},
        "marker": 12,
    },
}
ECON_AXES_RECT = (0.12, 0.16, 0.767, 0.74)  # (left, bottom, width, height), 그림 대비 비율
_econ_on = False
_econ_medium = "ppt"


def set_econ_chart_style(medium="ppt"):
    global _bis_on, _bok_on, _econ_on, _econ_medium
    if medium not in ECON_MEDIA:
        raise ValueError(f"set_econ_chart_style(): medium은 {list(ECON_MEDIA)} 중 하나")
    _bis_on, _bok_on, _econ_on, _econ_medium = False, False, True, medium
    plt.rcParams.update(
        {
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "mathtext.fontset": "custom",
            "mathtext.rm": "Times New Roman",
            "mathtext.it": "Times New Roman:italic",
            "mathtext.bf": "Times New Roman:italic:bold",
            "mathtext.cal": "Times New Roman:italic",
        }
    )


def econ_figure(left_pad=0):
    # left_pad: "P_B = P_A"처럼 긴 y축 라벨을 위해 왼쪽에 더 둘 여백(인치, ppt 기준).
    # 축 상자 크기(인치)는 그대로 두고 그림만 넓힘. book은 글자 크기 비율만큼 줄임
    m = ECON_MEDIA[_econ_medium]
    pad = left_pad * m["fontsize"]["tick"] / ECON_MEDIA["ppt"]["fontsize"]["tick"]
    w, h = m["figsize"]
    l, b, aw, ah = ECON_AXES_RECT
    fig = plt.figure(figsize=(w + pad, h))
    ax = fig.add_axes(((l * w + pad) / (w + pad), b, aw * w / (w + pad), ah))
    return fig, ax


def econ_axes(ax, xlim, ylim, xticks=None, yticks=None, xlabel="Y", ylabel="P"):
    # xticks·yticks: {값: "라벨"}. 라벨은 mathtext로 쓰면 Times 굵은 이탤릭 (예: r"$\bar{Y}$")
    m = ECON_MEDIA[_econ_medium]
    f, lw = m["fontsize"], m["lw"]
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.grid(False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set(color=ECON_COLORS["ink"], linewidth=lw["axis"])

    def bold(s):
        # 줄마다 $…$ 안을 \mathbf로 감싸 수식 편집기 같은 굵은 이탤릭으로
        return "\n".join(
            "$\\mathbf{" + t[1:-1] + "}$" if len(t) > 1 and t[0] == t[-1] == "$" else t
            for t in s.split("\n")
        )

    xticks, yticks = xticks or {}, yticks or {}
    ax.set_xticks(list(xticks), [bold(s) for s in xticks.values()])
    ax.set_yticks(list(yticks), [bold(s) for s in yticks.values()])
    ax.tick_params(length=0, labelsize=f["tick"], colors=ECON_COLORS["ink"], pad=4 * lw["axis"] + 2)
    # plot_save()의 set_yaxis_comma()가 라벨을 숫자로 덮어쓰지 않게
    ax._custom_comma_formatted = True

    # 축 이름: 축 끝 (P는 y축 위 왼쪽, Y는 x축 오른쪽 끝 아래)
    style = dict(fontsize=f["axis"], fontweight="bold", fontstyle="italic",
                 fontfamily="Times New Roman", color=ECON_COLORS["ink"], clip_on=False)
    ax.text(-0.02, 1.0, ylabel, transform=ax.transAxes, ha="right", va="center", **style)
    ax.text(1.02, 0.0, xlabel, transform=ax.transAxes, ha="left", va="center", **style)


def econ_line(ax, x, y, tone="curve", **kw):
    # tone: "curve"(남색) / "old"(이동 전 곡선, 회색) / 그 밖의 색 이름·hex
    m = ECON_MEDIA[_econ_medium]
    kw.setdefault("lw", m["lw"]["curve"])
    return ax.plot(x, y, color=ECON_COLORS.get(tone, tone), **kw)[0]


def econ_guide(ax, xs, ys):
    # 균형점에서 축으로 내리는 보조선: 가는 검정 파선
    m = ECON_MEDIA[_econ_medium]
    return ax.plot(xs, ys, color=ECON_COLORS["ink"], lw=m["lw"]["guide"], ls=(0, (4, 3)), zorder=1.5)[0]


def econ_dot(ax, x, y):
    m = ECON_MEDIA[_econ_medium]
    return ax.scatter([x], [y], s=m["marker"], color=ECON_COLORS["ink"], zorder=5)


def econ_text(ax, x, y, s, kind="curve", **kw):
    # 곡선 이름 등 라틴 글자: Times 이탤릭 (첨자는 mathtext, 예: r"$AD_1$")
    m = ECON_MEDIA[_econ_medium]
    kw.setdefault("fontsize", m["fontsize"][kind])
    kw.setdefault("fontstyle", "italic")
    kw.setdefault("fontfamily", "Times New Roman")
    kw.setdefault("color", ECON_COLORS["ink"])
    return ax.text(x, y, s, **kw)


def econ_note(ax, x, y, s, **kw):
    # 분홍 설명 상자 (한글은 set_fonts()의 글꼴)
    m = ECON_MEDIA[_econ_medium]
    kw.setdefault("fontsize", m["fontsize"]["note"])
    kw.setdefault("linespacing", 1.4)
    pad = 6 if _econ_medium == "ppt" else 3
    return ax.text(
        x, y, s, color=ECON_COLORS["ink"],
        bbox=dict(facecolor=ECON_COLORS["note"], edgecolor="none", pad=pad), **kw,
    )


def econ_point(ax, x, y, name, dx=2, dy=2, **kw):
    # 균형점: 검은 점 + 이름(A, B, C). dx·dy는 이름을 점에서 띄우는 거리(데이터 단위)
    econ_dot(ax, x, y)
    kw.setdefault("ha", "left" if dx >= 0 else "right")
    kw.setdefault("va", "bottom" if dy >= 0 else "top")
    return econ_text(ax, x + dx, y + dy, name, **kw)


def econ_arrow(ax, start, end):
    # 이동 방향 화살표: 곡선과 같은 굵기의 검정
    m = ECON_MEDIA[_econ_medium]
    return ax.annotate(
        "", xy=end, xytext=start,
        arrowprops=dict(arrowstyle="->", lw=m["lw"]["curve"], color=ECON_COLORS["ink"],
                        shrinkA=0, shrinkB=0),
        annotation_clip=False,
    )


def econ_path_arrow(ax, xs, ys, step=8):
    # 선 위를 따라가는 화살촉들 (A→B, B→C처럼 균형점이 SRAS·AD 위를 움직일 때)
    # 경로 xs, ys를 따라 step(데이터 단위)마다 검은 삼각형을 진행 방향으로 찍음
    import numpy as np

    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    if len(xs) == 2:  # 직선 경로는 촘촘히 나눔
        xs, ys = np.linspace(xs[0], xs[1], 50), np.linspace(ys[0], ys[1], 50)
    dist = np.concatenate([[0], np.cumsum(np.hypot(np.diff(xs), np.diff(ys)))])
    size = 24 if _econ_medium == "ppt" else 9
    for d in np.arange(step, dist[-1] + 1e-9, step):
        i = int(np.searchsorted(dist, d))
        ax.annotate(
            "", xy=(xs[i], ys[i]), xytext=(xs[i - 1], ys[i - 1]),
            arrowprops=dict(arrowstyle="-|>", mutation_scale=size, lw=0,
                            color=ECON_COLORS["ink"], shrinkA=0, shrinkB=0),
            zorder=6,
        )


def econ_ramp(frame, start, end):
    # 애니메이션 진행률: start 장면 전 0, end 장면 뒤 1, 그 사이 직선으로
    return min(max((frame - start) / (end - start), 0.0), 1.0)


def econ_animate(fig, update, frames, fps=15):
    # ppt: update(frame)로 그린 장면들을 pic_gif/<스크립트이름>.gif로 (한 번만 재생, 반복 없음)
    # book: 책은 움직일 수 없으므로 마지막 장면을 plot_save()처럼 pic_tif·pic_jpg/<스크립트이름>_book으로
    import matplotlib.animation as animation

    name = os.path.splitext(os.path.basename(inspect.stack()[1].filename))[0]
    if _econ_medium == "book":
        update(frames - 1)
        plot_save(name=name)
        return

    class NoLoopPillowWriter(animation.PillowWriter):
        # 기본 Writer는 loop=0(무한 반복)을 강제하므로 loop 인자 없이 저장
        def finish(self):
            self._frames[0].save(
                self.outfile, save_all=True, append_images=self._frames[1:],
                duration=int(1000 / self.fps),
            )

    os.makedirs("pic_gif", exist_ok=True)
    path = f"pic_gif/{name}.gif"
    ani = animation.FuncAnimation(fig, update, frames=frames)
    ani.save(path, writer=NoLoopPillowWriter(fps=fps), dpi=200)
    plt.close(fig)
    print(f"{path} 저장 ({frames}장면)")


def plot_save(i=None, name=None):

    # 저장 및 출력
    # python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

    """
    이 함수를 호출한 .py 파일 이름을 기반으로 그래프를 tif, jpg로 저장합니다.
    name을 주면 스크립트 이름 대신 그 이름으로 저장합니다 (econ_animate가 씀).
    """
    # 호출한 파일 경로 추출
    if name is None:
        caller_frame = inspect.stack()[1]
        caller_filepath = caller_frame.filename
        base_filename = os.path.splitext(os.path.basename(caller_filepath))[0]
    else:
        base_filename = name

    # i가 있으면 _i 형식으로 suffix 추가
    suffix = f"_{i}" if i is not None else ""
    # 기본 매체가 아닌 판은 이름을 달리 해 기본 판을 덮어쓰지 않음
    # econ_chart: 기본 ppt, book 판은 _book / BIS: 기본 book(책 TIFF), ppt 판은 _ppt
    if _econ_on and _econ_medium == "book":
        suffix += "_book"
    elif _bis_on and _bis_medium == "ppt":
        suffix += "_ppt"

    # 저장 경로 설정
    image_path_tif = f"pic_tif/{base_filename}{suffix}.tif"
    image_path_jpg = f"pic_jpg/{base_filename}{suffix}.jpg"

    # 디렉토리 없으면 자동 생성
    os.makedirs("pic_tif", exist_ok=True)
    os.makedirs("pic_jpg", exist_ok=True)

    # comma at every 3 digits on y-axis
    set_yaxis_comma()

    # set_bis_style() / set_bok_style()을 불렀으면 그 스타일로 다듬기
    if _bis_on:
        _bis_restyle(plt.gcf())
    elif _bok_on:
        _bok_restyle(plt.gcf())

    # 그래프 저장
    # TIF는 무손실 LZW 압축으로 저장 (화질 동일, 용량 약 1/10)
    plt.savefig(image_path_tif, dpi=300, pil_kwargs={"compression": "tiff_lzw"})
    plt.savefig(image_path_jpg, dpi=300)

    # JPEG → CMYK 변환 후 덮어쓰기
    # img = Image.open(image_path_jpg).convert("CMYK")
    img = Image.open(image_path_jpg).convert("RGB")

    img.save(image_path_jpg, "JPEG")

    plt.show()


def korea_recession(start=None, end=None):

    # 한국 기준순환일: 정점(peak) → 다음 저점(trough)
    recession_periods = [
        ("1974-02-01", "1975-06-01"),
        ("1979-02-01", "1980-09-01"),
        ("1984-02-01", "1985-09-01"),
        ("1988-01-01", "1989-07-01"),
        ("1992-01-01", "1993-01-01"),
        ("1996-03-01", "1998-08-01"),
        ("2000-08-01", "2001-07-01"),
        ("2002-12-01", "2005-04-01"),
        ("2008-01-01", "2009-02-01"),
        ("2011-08-01", "2013-03-01"),
        ("2017-09-01", "2020-05-01"),
    ]

    recession_periods = [
        (pd.to_datetime(peak), pd.to_datetime(trough))
        for peak, trough in recession_periods
    ]

    if start is not None:
        start = pd.to_datetime(start)
        recession_periods = [
            (peak, trough) for peak, trough in recession_periods if trough >= start
        ]

    if end is not None:
        end = pd.to_datetime(end)
        recession_periods = [
            (peak, trough) for peak, trough in recession_periods if peak <= end
        ]

    return recession_periods
