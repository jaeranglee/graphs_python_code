# %% [markdown]
# # [그림 53] 전세계 금 보유량, 국가별 보유량
#
# ## 이 코드가 하는 일
# IMF에서 세계와 주요국 중앙은행의 금 보유량, 외환보유액을 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# 중앙은행은 외환보유액의 일부를 금으로 가지고 있다. 최근 몇 년 동안 여러 나라 중앙은행이 금을 많이 사들였다.
# - 왼쪽: 세계 중앙은행의 금 보유량(왼쪽 y축)과 외환보유액 중 금이 차지하는 비중(오른쪽 y축)
# - 오른쪽: 금을 가장 많이 가진 나라 중 하나인 독일(왼쪽 y축)과 중국·인도·일본·터키(오른쪽 y축)의 금 보유량
#
# ## 결과물
# pic_jpg/f53_gold_reserve.jpg, pic_tif/f53_gold_reserve.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - imf_api.py: IMF 자료 받기(fetch_gold_data, fetch_imf_data, API key 필요 없음)
#
# ## 자료 가공
# - 금 보유 비중(%) = 세계 금 보유액(달러) / 세계 외환보유액 x 100
# %%
import matplotlib.dates as mdates

import matplotlib.pyplot as plt


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


start = "1999-01-01"
end = "2025-06-01"


# imf_api 가져오기
from imf_api import *

indicator_id = [
    "RGV_REVS",  # Gold Reserve Volume
    "RGOLDMV_REVS",  # Gold Reserve in market value (SDR), 시계열 사라짐
    "TRGMV_REVS",  # Total Reserve in USD (market value)
    "RXF11_REVS",  # Reserve Excluding Gold, only in USD
    "RGOLDNV_REVS",  # Gold Reserve in national value (USD)
]


country_id = ["G001", "USA", "DEU", "ITA", "FRA", "CHN", "CHE", "IND", "JPN", "TUR"]
unit_id = ["FTO", "XDR", "USD"]


# world total gold volume
df_world_gold = fetch_gold_data(
    country_id[0],  # World
    indicator_id[0],  # Gold Reserve Volume
    unit_id[0],  # Troy ounce
    start_period=start,
    end_period=end,
)
df_world_gold = df_world_gold.rename(columns={"OBS_VALUE": "World Holdings"}).copy()

# world total gold value in USD
df_world_gold_value = fetch_imf_data(
    "IMF.STA,IL",
    country_id[0],  # World
    indicator_id[4],  # Gold Reserve in national value (USD),
    start_period=start,
    end_period=end,
    cycle="M",
    use_cache=True,
    unit_id=unit_id[2],
)  # USD,

df_world_gold_value = df_world_gold_value.rename(
    columns={"OBS_VALUE": "World Gold Values"}
).copy()


# world total reserves in USD
df_world_reserves = (
    fetch_imf_data(
        "IMF.STA,IL",
        country_id[0],  # World
        indicator_id[2],  # Total Reserve in USD (market value)
        start_period=start,
        end_period=end,
        cycle="M",
        use_cache=False,
        unit_id=unit_id[2],  # USD, (SDR 단위 사라짐)
    )
    .rename(columns={"OBS_VALUE": "World Reserves"})
    .copy()
)

print(df_world_reserves.head())

df_merged = pd.merge(df_world_gold_value, df_world_reserves, on="Date", how="inner")
df_merged["share"] = df_merged["World Gold Values"] / df_merged["World Reserves"] * 100

# List of country codes and labels
countries = ["DEU", "CHN", "IND", "JPN", "TUR"]
labels = ["독일", "중국", "인도", "일본", "터키"]
colors = ["blue", "black", "gray", "black", "blue"]
lws = [2, 2, 2, 1.5, 1.5]
lss = ["-", "--", ":", "-.", "--"]


# countries' gold holdings volume data fetch

all_data = {}
for country in countries:
    df = fetch_gold_data(
        country,  # country in countries list
        indicator_id[0],  # Gold Reserve Volume
        unit_id[0],  # Troy ounce
        start_period=start,
        end_period=end,
    )

    df = df.rename(columns={df.columns[-1]: "value"})
    all_data[country] = df.set_index("Date")["value"].to_dict()
df_pivot = pd.DataFrame(all_data)


# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# Gold volume, and Reserve share

ax_left = ax[0]
ax_right = ax_left.twinx()  # Create right-side y-axis

ax_left.plot(
    df_world_gold["Date"],
    df_world_gold["World Holdings"] / 1e6,
    label="전세계 금 보유량(좌축)",
    lw=2,
    color="black",
)
ax_right.plot(
    df_merged["Date"],
    df_merged["share"],
    label="금 보유액/외환보유액(우축)",
    lw=2,
    color="blue",
)

# 과학적 표기 (1e6 등) 방지
# ax[0].ticklabel_format(style='plain', axis='y')

ax_left.legend(loc="upper left", bbox_to_anchor=(0, 1.0))
ax_right.legend(loc="upper left", bbox_to_anchor=(0, 0.92))
ax_left.yaxis.label.set_visible(True)
ax_left.text(
    0,
    1.00,
    "(백만 troy oz)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)
ax_right.text(
    1,
    1.00,
    "(%)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[0].transAxes,
)

ax[0].xaxis.set_major_locator(mdates.YearLocator(4))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
ax[0].text(
    0.0, -0.15, "출처: IFS, IMF", transform=ax[0].transAxes, fontsize=10, ha="left"
)
ax[0].grid(True, linestyle="--", which="major", alpha=0.5, axis="y")


ax_left1 = ax[1]
ax_right1 = ax_left1.twinx()  # Create right-side y-axis


# 독일(최축)

ax_left1.plot(
    df_pivot.index, df_pivot["DEU"] / 1e6, label="독일(좌축)", lw=2, color="blue"
)

# 다른 나라(우축)
# Plot each country with its corresponding color

for country, label, lw, color, ls in zip(
    countries[1:], labels[1:], lws[1:], colors[1:], lss[1:]
):
    ax_right1.plot(
        df_pivot.index,
        df_pivot[country] / 1e6,
        label=label + "(우측)",
        lw=lw,
        color=color,
        ls=ls,
    )


# 과학적 표기 (1e6 등) 방지
# ax_left1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:,.0f}'))

ax[1].xaxis.set_major_locator(mdates.YearLocator(4))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

# 단위 표시 및 출처
ax_left1.legend(loc="upper left", bbox_to_anchor=(0.2, 0.99))
ax_right1.legend(loc="upper left", bbox_to_anchor=(0.63, 0.7))


ax[1].text(
    0,
    1.00,
    "(백만 troy oz)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)
ax[1].text(
    1,
    1.0,
    "(백만 troy oz)",
    ha="right",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax[1].transAxes,
)

ax[1].text(
    0.0, -0.15, "출처: IFS, IMF", transform=ax[1].transAxes, fontsize=10, ha="left"
)

ax[1].grid(True, linestyle="--", which="major", alpha=0.5, axis="y")


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

set_yaxis_comma(ax[0])
plot_save()
