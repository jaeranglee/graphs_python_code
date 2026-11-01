# %% [markdown]
# # [그림 10] MMF의 RRP와 TGCR 거래 규모
#
# ## 이 코드가 하는 일
# 뉴욕 연준에서 TGCR 거래량과 RRP 거래액을 받아 한 그림에 그린다(y축 두 개).
#
# ## 그림이 다루는 내용
# [그림 8]에서 본 것처럼 MMF는 연준 RRP에서 돈을 뺐다. 그 돈의 일부는 민간 레포 시장(국채담보 단기거래)으로 갔다.
# 연준 RRP 거래액은 줄고 TGCR 거래량은 늘어나는 모습을 한 그림에서 비교한다.
#
# ## 결과물
# pic_jpg/f10_tgcr_vol.jpg, pic_tif/f10_tgcr_vol.tif
#
# ## 필요한 파일 (defs 폴더)
# - fred_api.py: FRED 자료 받기
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - nyfed_api_rate_volume.py: 뉴욕 연준 기준금리와 거래량 받기(fetch_all_secured_rates_vol)
# - nyfed_rrp_vol.py: 뉴욕 연준 RRP 거래 자료 받기(fetch_rrp_vol)
# %%
import matplotlib.dates as mdates

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

# %% [markdown]
# ## 자료 받기 (뉴욕 연준 Markets Data)
# - fetch_all_secured_rates_vol(): TGCR, BGCR, SOFR, EFFR의 금리와 거래량. 그림에는 TGCR 거래량만 쓴다.
# - fetch_rrp_vol(): 첫 번째 자료는 RRP 전체 거래액, 두 번째 자료 중 거래상대방이 mmf인 줄은 MMF의 RRP 거래액이다.
# ## 자료 받기 (FRED)
# - 연준 RRP 잔액 주평균 (WLRRAA): 불러오기만 하고 그림에는 쓰지 않는다.
# ## 그리기
# - 왼쪽 y축: TGCR 거래량, 오른쪽 y축: RRP 전체 거래액과 MMF의 RRP 거래액
# %%
from nyfed_api_rate_volume import fetch_all_secured_rates_vol
from nyfed_rrp_vol import fetch_rrp_vol
from fred_api import fetch_fred_series

# 사용자 정의 기간

start = "2020-01-01"
end = "2025-10-01"

# Fetch Volume data from NY FED Markets Data
df_all = fetch_all_secured_rates_vol(start_date=start, end_date=end)

tgcr = df_all[df_all["Type"] == "TGCR"].copy()
bgcr = df_all[df_all["Type"] == "BGCR"].copy()
sofr = df_all[df_all["Type"] == "SOFR"].copy()
effr = df_all[df_all["Type"] == "EFFR"].copy()

df_rrp = fetch_fred_series("WLRRAA", start_date=start, end_date=end)

# Fetch Total RRP data from NY FED Markets Data,
ny_rrp = fetch_rrp_vol(start_date=start, end_date=end)[0]

# Fetch MMF's RRP data from NY FED Markets Data,
mmf_rrp = fetch_rrp_vol(start_date=start, end_date=end)[1]
mmf_rrp = mmf_rrp[mmf_rrp["Counterparty Type"] == "mmf"].copy()


# 시각화
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)


ax_left = ax
ax_right = ax_left.twinx()  # Create right-side y-axis

# 왼쪽 TGCR volume
ax_left.plot(
    tgcr["Date"], tgcr["Volume"] / 1e3, label="TGCR trading volume", lw=2, color="black"
)

# 오른쪽: FED RRP total volume, FED RRP with mmf volume
ax_right.plot(
    ny_rrp["Date"],
    ny_rrp["Total Volume"] / 1e12,
    label="RRP Total",
    linestyle=":",
    lw=2,
    color="black",
)
ax_right.plot(
    mmf_rrp["Date"],
    mmf_rrp["Amount Accepted"] / 1e12,
    label="MMF RRP",
    linestyle="-",
    lw=2,
    color="blue",
)

ax_right.set_ylim(-0.1, 3)
ax_left.set_ylim(-0.1, 3)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

ax_left.text(
    0,
    1.00,
    "(조 달러)",
    ha="left",
    va="bottom",
    transform=ax.transAxes,
    fontsize=12,
    color="black",
)
ax_right.text(
    1,
    1,
    "(조 달러)",
    ha="right",
    va="bottom",
    transform=ax.transAxes,
    fontsize=12,
    color="black",
)
ax_left.legend(loc="upper left", bbox_to_anchor=(0.0, 0.85))
ax_right.legend(loc="upper left", bbox_to_anchor=(0.0, 0.99))

ax.text(0, -0.15, "출처: NY FED", transform=ax.transAxes, fontsize=10)
ax.grid(True, linestyle="--", color="gray", alpha=0.3)

mmf_rrp.to_csv("data/mmf_rrp.csv")
ny_rrp.to_csv("data/ny_rrp.csv")

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
plot_save()
