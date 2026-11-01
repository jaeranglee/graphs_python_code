# %% [markdown]
# # [그림 29] 연준의 국채보유액과 연방정부의 연준예금(TGA)잔액
#
# ## 이 코드가 하는 일
# FRED에서 연준의 국채 보유액과 재무부의 연준 예금(TGA) 잔액을 받아 그림 두 개를 나란히 그린다.
#
# ## 그림이 다루는 내용
# - 왼쪽: 연준은 코로나 때 국채를 대량으로 사들였고(양적완화), 2022년부터는 만기가 된 국채를 다시 사지 않는 방식으로
#   보유액을 줄였다(양적긴축). 중장기국채(Notes and Bonds)와 단기국채(Bills)로 나눠 본다.
# - 오른쪽: TGA는 미국 재무부가 연준에 둔 예금 계좌이다. 세금이 들어오고 국채를 발행하면 늘고, 돈을 쓰면 준다.
#
# ## 결과물
# pic_jpg/f29_soma_holdings.jpg, pic_tif/f29_soma_holdings.tif
#
# ## 필요한 파일 (defs 폴더)
# - plot_def.py: 한글 폰트 설정, 그림 저장
# - fred_api.py: FRED 자료 받기
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
# ## 자료 받기 (FRED, 모두 매주 수요일 기준, 백만 달러)
# - 연준 보유 중장기국채 (WSHONBNL)
# - 연준 보유 단기국채 (WSHOBL)
# - 연준 보유 물가연동국채 (WSHONBIIL): 불러오지만 그림에는 쓰지 않는다(TIPS 선은 주석 처리).
# - 연준 보유 국채 합계 (WSHOTSL): 불러오지만 그림에는 쓰지 않는다.
# - 재무부 일반계정 TGA (WDTGAL)
# ## 그리기
# - 모두 1e6으로 나눠 조 달러로 그린다. 왼쪽은 중장기국채와 단기국채, 오른쪽은 TGA이다.
# %%
start = "2020-01-01"
end = "2025-12-31"

series_ids = {
    "Notes and Bonds": "WSHONBNL",
    "Bills": "WSHOBL",
    "TIPS": "WSHONBIIL",
    "Treasuries": "WSHOTSL",
    "TGA": "WDTGAL",
}


from fred_api import fetch_fred_series


# 모든 데이터 가져오기
all_data = {}
for term, sid in series_ids.items():
    df = fetch_fred_series(sid, start_date=start, end_date=end)

    df = df.rename(columns={df.columns[-1]: "value"})
    all_data[term] = df.set_index("observation_date")["value"].to_dict()


# 병합
soma = pd.DataFrame(all_data)

# 시각화
fig, ax = plt.subplots(1, 2, figsize=(8, 4.5), constrained_layout=True)

# 왼쪽:
ax[0].plot(
    soma.index,
    soma["Notes and Bonds"] / 1e6,
    label="Notes and Bonds",
    lw=2,
    color="black",
)
ax[0].plot(soma.index, soma["Bills"] / 1e6, label="Bills", lw=2, color="blue")

# 책에는 사용하지 않음
# ax[0].plot(soma.index, soma['TIPS']/1e6, label='TIPS', lw=2, color='orange')

ax[1].plot(soma.index, soma["TGA"] / 1e6, label="TGA", lw=2, color="blue")


for i in [0, 1]:
    ax[i].legend(loc="upper left", bbox_to_anchor=(0.4, 0.7), fontsize=12)

    ax[i].xaxis.set_major_locator(mdates.YearLocator())
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax[i].text(
        0,
        1.00,
        "(조 달러)",
        ha="left",
        va="bottom",
        transform=ax[i].transAxes,
        fontsize=12,
    )
    ax[i].text(0, -0.15, "출처: FRED", transform=ax[i].transAxes, fontsize=12)

    ax[i].grid(True, linestyle="--", color="gray", linewidth=0.7, alpha=0.7)

# 저장 및 출력
# python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

plot_save()
