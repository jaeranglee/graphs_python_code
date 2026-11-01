# %% [markdown]
# # [그림 52] 전세계 외환보유액의 주요 통화별 구성
#
# ## 이 코드가 하는 일
# IMF에서 세계 외환보유액을 통화별로 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# 외환보유액은 각 나라 중앙은행이 위기에 대비해 가지고 있는 외화 자산이다.
# IMF의 COFER 통계는 이 외환보유액이 어떤 통화(달러, 유로, 엔, 파운드, 위안 등)로 되어 있는지 보여준다.
# 달러 비중은 1999년 70%를 넘었으나 2025년에는 60% 아래로 내려왔다. 그래도 여전히 가장 큰 비중이다.
# - 왼쪽: 통화별 비중(%)을 쌓은 면적 그래프
# - 오른쪽: 통화별 보유 금액(조 달러)
#
# ## 결과물
# pic_jpg/f52_reserve.jpg, pic_tif/f52_reserve.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - imf_api.py: IMF 자료 받기(API key 필요 없음)
#
# ## 자료 받기 (IMF COFER, 1999년 1분기 ~ 2025년 1분기)
# - 금액: fetch_cofer_data(통화 코드, "NV_USD", ...)
# - 비중: fetch_imf_data(..., unit_id="SHRO_PT", cycle="Q"). 같은 자료를 받지만 두 함수는 인자 이름이 다르다.
# - 기타 = 100 - 다섯 통화 비중의 합
#
# ## 그리기
# - 왼쪽 면적 그래프는 그림을 꽉 채우므로, 범례를 한 가지 색으로 된 아래쪽 USD 영역에 3열로 둔다.
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter


# 한글 폰트 설정

# Set font depending on the platform
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

from plot_def import *

set_fonts()

# fetch data from IMF Data
from imf_api import *

currencies = {
    "USD": "CI_USD",
    "EUR": "CI_EUR",
    "JPY": "CI_JPY",
    "GBP": "CI_GBP",
    "CNY": "CI_CNY",
}

color_map = {
    "USD": "black",
    "EUR": "blue",
    "JPY": "gray",
    "GBP": "blue",
    "CNY": "black",
}

ls_map = {"USD": "-", "EUR": "--", "JPY": ":", "GBP": "-.", "CNY": "-"}

lw_map = {"USD": 2, "EUR": 2, "JPY": 1.5, "GBP": 1.5, "CNY": 1}
# 기준 날짜 설정
start = "1999-Q1"
end = "2025-Q1"


# 통합 DataFrame 생성
dfs_usd = []
dfs_share = []

for name, code in currencies.items():
    df_usd = fetch_cofer_data(code, "NV_USD", start_period=start, end_period=end)
    df_usd = df_usd.rename(columns={"NV_USD": name})
    dfs_usd.append(df_usd.set_index("Date"))

    # df_share = fetch_cofer_data(code, "SHRO_PT", start_period=start, end_period=end)

    # fetch_imf_data() will work too. But params are different from fetch_cofer_data().
    df_share = fetch_imf_data(
        "IMF.STA,COFER",
        "G001.AFXRA",  # country_id is for world(GOO1) and AFXRA data. with fetch_imf_data()
        indicator_id=code,  # currencies code is indicator_id for fetch_imf_data()
        unit_id="SHRO_PT",  # param for fetch_cofer_data() is unit_id for fetch_imf_data()
        start_period=start,
        end_period=end,
        cycle="Q",  # cycle is pre-coded with fetch_cofer_data(), but fetch_imf_data() should come with cycle.
        # No 'M' cycle is available for COFER.
    )

    # df_share.rename(columns={"SHRO_PT": name}, inplace=True)

    # extra data preps with fetch_imf_data()
    # fetch_imf_data() fetches "OBS_VALUE", not "SHRO_PT".
    # fetch_imf_data() has other cols that will not be used.
    # Select only ['Date',name]
    df_share = df_share.rename(columns={"OBS_VALUE": name})
    df_share = df_share[["Date", name]]

    # common lines of commands from here.
    print(df_share)
    dfs_share.append(df_share.set_index("Date"))

# 날짜 기준으로 병합
df_usd_all = pd.concat(dfs_usd, axis=1).sort_index()
df_share_all = pd.concat(dfs_share, axis=1).sort_index()

print(df_share_all)

# 부족 분을 기타로 계산
df_with_other = df_share_all.copy()

df_with_other["기타"] = 100 - df_with_other.sum(axis=1)


### 시각화


# Plot
# 왼쪽: 달러 쉐어 그래프:

df_with_other.index = pd.to_datetime(df_with_other.index)

# --- Visualization ---
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

## (1) Share chart (area)
df_with_other.plot.area(
    ax=ax[0],
    stacked=True,
    alpha=0.65,
    color=["lightblue", "gray", "steelblue", "lightgray", "gainsboro", "whitesmoke"],
)

ax[0].set_xlabel("")
ax[0].ticklabel_format(style="plain", axis="y")
# 선이 없는 아래쪽 USD 영역에 범례를 둔다.
ax[0].legend(loc="lower center", ncol=3)
ax[0].text(
    0,
    1.00,
    "(구성비율, %)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    transform=ax[0].transAxes,
)
ax[0].text(
    0,
    -0.15,
    "출처: COFER, IMF",
    transform=ax[0].transAxes,
    fontsize=11,
    va="bottom",
    ha="left",
    color="black",
)

## (2) USD value chart (lines)
for curr in currencies.keys():
    df_usd_all[curr] = df_usd_all[curr] / 1e12  # 조 달러 단위
    ax[1].plot(
        df_usd_all.index,
        df_usd_all[curr],
        label=curr,
        lw=lw_map[curr],
        ls=ls_map[curr],
        color=color_map[curr],
    )

ax[1].xaxis.set_major_locator(mdates.YearLocator(5))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax[1].ticklabel_format(style="plain", axis="y")
ax[1].yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}"))

ax[1].text(
    0,
    1.00,
    "(금액, 조 달러)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    transform=ax[1].transAxes,
)
ax[1].text(
    0,
    -0.15,
    "출처: COFER, IMF",
    transform=ax[1].transAxes,
    fontsize=11,
    va="bottom",
    ha="left",
    color="black",
)

ax[1].legend(loc="upper left")
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
