# %% [markdown]
# # [그림 12] 연방기금금리와 정책금리
#
# ## 이 코드가 하는 일
# FRED에서 실효연방기금금리와 정책금리 범위를 받아 한 그림에 그린다.
#
# ## 그림이 다루는 내용
# 연방기금금리는 미국 은행들이 서로 하루 동안 돈을 빌려줄 때의 금리이고, 연준은 이 금리의 목표 범위를 정한다.
# 실효연방기금금리(실제 거래된 평균 금리)가 2022년 이후 금리 인상과 인하 과정에서
# 목표 범위 안에 머무는 모습을 본다.
#
# ## 결과물
# pic_jpg/f12_ffr.jpg, pic_tif/f12_ffr.tif
#
# ## 필요한 파일 (defs 폴더)
# - fred_api.py: FRED 자료 받기
# - plot_def.py: 한글 폰트 설정, 그림 저장
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

from plot_def import *

set_fonts()
# %% [markdown]
# ## 자료 받기 (FRED)
# - 실효연방기금금리 (RIFSPFFNB): 선으로 그린다.
# - 정책금리 범위의 위쪽(DFEDTARU)과 아래쪽(DFEDTARL): 두 값 사이를 색칠한다(fill_between).
# %%
start = "2022-01-01"
end = "2025-12-31"

from fred_api import fetch_fred_series

df0 = fetch_fred_series("RIFSPFFNB", start_date=start, end_date=end)
df1 = fetch_fred_series("DFEDTARU", start_date=start, end_date=end)
df2 = fetch_fred_series("DFEDTARL", start_date=start, end_date=end)

merged_df = df0.copy()
# ---------------------

# 그래프 그리기
fig, ax = plt.subplots(figsize=(9, 4.5), constrained_layout=True)

# 보조 y축: Effective Federal Funds Rate
ax.plot(
    merged_df["observation_date"],
    merged_df["RIFSPFFNB"],
    label="실효연방기금금리",
    color="blue",
    lw=2,
)

ax.fill_between(
    df1["observation_date"],
    df1["DFEDTARU"],
    df2["DFEDTARL"],
    label="정책금리 범위",
    alpha=0.2,
)
ax.text(
    0,
    1.00,
    "(%)",
    ha="left",
    va="bottom",
    color="black",
    fontsize=12,
    rotation=0,
    transform=ax.transAxes,
)

ax.tick_params(axis="y", labelcolor="b")

# 제목 및 레이아웃
ax.text(
    0.0,
    -0.15,
    "출처: FRED",
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment="bottom",
    horizontalalignment="left",
    color="black",
)

plt.grid(False)
ax.legend()

# 저장 및 출력
plot_save()
