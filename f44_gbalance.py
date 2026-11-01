# %% [markdown]
# # [그림 44] 미국 재정수지 흑자기
#
# ## 이 코드가 하는 일
# FRED에서 미국 연방정부의 연간 재정수지를 받아, 흑자를 낸 두 시기를 그림 두 개로 나눠 그린다.
#
# ## 그림이 다루는 내용
# 재정수지 = 정부 수입 - 정부 지출. 0보다 크면 흑자, 작으면 적자이다.
# 미국 연방정부는 대부분의 해에 적자를 냈고, 흑자는 드물었다.
# - 왼쪽: 1913~1933년. 제1차 세계대전 뒤 1920년대에 흑자가 이어졌다.
# - 오른쪽: 1997년 이후. 1998~2001년에 흑자를 낸 뒤 다시 적자로 돌아섰다.
# 두 그림 모두 경기침체 기간을 회색으로 칠한다.
#
# ## 결과물
# pic_jpg/f44_gbalance.jpg, pic_tif/f44_gbalance.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 경기침체 기간(nber_recession), 그림 저장, FRED 자료 받기
# - fred_api.py: fetch_fred_series가 실제로 들어 있는 파일(plot_def.py가 대신 불러온다)
#
# ## 자료 받기 (FRED)
# - 연방정부 재정수지 (FYFSD), 회계연도 기준 연간 자료
# %%
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


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

start = "1913-01-01"
end = "2099-12-31"

# Fetch FRED series

# Federal Balance
bal = fetch_fred_series("FYFSD", start_date=start, end_date=end)


# 2021년 이후로 필터링
bal1 = bal[
    (bal["observation_date"] >= "1913-01-01")
    & (bal["observation_date"] <= "1933-01-01")
].copy()
bal2 = bal[bal["observation_date"] >= "1997-01-01"].copy()


# NBER Recession from plot_def.py
recession_periods = nber_recession(start=start, end=end)


# 시각화
fig, ax = plt.subplots(1, 2, figsize=(9, 4.5), constrained_layout=True)

# 왼쪽: 1917부터  1930
ax[0].plot(
    bal1["observation_date"], bal1["FYFSD"] / 1e2, label="재정수지", lw=2, color="blue"
)
ax[0].axhline(y=0, color="gray", linestyle="--")

ax[0].legend()
ax[0].xaxis.set_major_locator(mdates.YearLocator(3))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


# 침체기 음영
for peak, trough in recession_periods:
    if (
        peak >= bal1["observation_date"].min()
        and trough <= bal1["observation_date"].max()
    ):
        ax[0].axvspan(peak, trough, color="gray", alpha=0.3)


# 단위 표시 및 출처
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
    "출처: FRED, 음영은 경기침체기",
    transform=ax[0].transAxes,
    fontsize=10,
    ha="left",
)
ax[0].grid(False)

# 오른쪽: 1997 이후

ax[1].plot(
    bal2["observation_date"], bal2["FYFSD"] / 1e6, label="재정수지", lw=2, color="black"
)

ax[1].axhline(y=0, color="gray", linestyle="--")

# 침체기 음영

for peak, trough in recession_periods:
    if (
        peak >= bal2["observation_date"].min()
        and trough <= bal2["observation_date"].max()
    ):
        ax[1].axvspan(peak, trough, color="gray", alpha=0.3)


ax[1].legend()
ax[1].xaxis.set_major_locator(mdates.YearLocator(3))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


# 단위 표시 및 출처
ax[1].text(
    0,
    1.00,
    "(조 달러)",
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
    "출처: FRED, 음영은 경기침체기",
    transform=ax[1].transAxes,
    fontsize=10,
    ha="left",
)
ax[1].grid(False)


# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
