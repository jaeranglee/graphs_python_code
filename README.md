# Open API를 이용한 그래프 작성

책 「이야기로 풀어가는 현실 국제금융론」의 [그림]을 그리는 Python 코드입니다.
세인트루이스 연준 FRED, 뉴욕 연준 Markets Data, 미국 재무부 Fiscal Data, Yahoo Finance, IMF, 한국은행 ECOS의
자료를 Open API로 받아 그래프를 그립니다. 자료를 받는 함수는 다른 분석에도 그대로 쓸 수 있습니다.

코드는 MIT 라이선스로 공개합니다(`LICENSE`). 출처를 밝히면 자유롭게 고쳐 쓰고 다시 배포할 수 있습니다.
`data/`의 자료는 각 기관(CME, FRB, 미국 재무부, Google 등)의 것이므로 그 기관의 이용 조건을 따릅니다.

## 폴더 구성

```
graphs_python_code/        이 저장소
├── README.md
├── LICENSE                MIT 라이선스
├── .gitignore             올리지 않는 파일 목록(.env, 캐시, 그림 파일)
├── requirements.txt       필요한 패키지 목록
├── f1_bank_deposits.py    [그림 1]을 그리는 코드
├── ...
├── data/                  직접 내려받은 자료 (CME, FRB, Google Trends, 재무부 파일 등)
├── defs/                  자료를 받는 함수, 그림 저장 함수 (이 책의 코드가 쓰는 파일만)
│   ├── fred_api.py
│   ├── plot_def.py
│   ├── .env.example       API 키 견본 (복사해서 .env를 만듦)
│   ├── .env               API 키 (직접 만듦, 공개하지 않음)
│   └── ...
├── cache/                 API 응답 캐시 (실행하면 생김)
├── pic_jpg/               그린 그림 (jpg, 실행하면 생김)
└── pic_tif/               그린 그림 (tif, 인쇄용)
```

- 파일 이름은 책의 그림 번호와 내용입니다. 예: `[그림 1] 은행예금 잔액과 은행업 ETF가격` → `f1_bank_deposits.py`.
- 자료를 받는 함수 파일은 `defs/`에 있습니다. 각 코드의 첫 부분에 있는 아래 블록이 `defs/`를 찾아 import 경로에 넣습니다.
  코드 폴더 안의 `defs/`를 먼저 찾고, 없으면 위쪽 폴더에서 찾습니다. 그래서 코드 파일을 다른 폴더로 옮겨도 `defs/`가 같은 폴더나 위쪽 폴더에 있으면 됩니다.

```python
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
```

## 준비

1. Python 3.13을 설치합니다.
2. 이 저장소를 내려받고(`git clone https://github.com/jaeranglee/graphs_python_code.git` 또는 Code → Download ZIP),
   그 폴더에서 가상환경을 만들고 패키지를 설치합니다.
   ```
   cd graphs_python_code
   python3.13 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
   Windows에서는 `.venv/bin/pip` 대신 `.venv\Scripts\pip`를 씁니다.
3. API 키를 받아 `defs/.env` 파일에 적습니다. 키는 영문과 숫자로 된 긴 문자열이며, 남에게 보이지 않게 합니다.
   견본 파일 `defs/.env.example`을 같은 폴더에 `.env`라는 이름으로 복사한 뒤 `=` 뒤에 키를 적으면 됩니다.
   ```
   cp defs/.env.example defs/.env
   ```
   ```
   FRED_API_KEY=발급받은_키
   ECOS_API_KEY=발급받은_키
   ```
   `.env`는 `.gitignore`에 들어 있어 git에 올라가지 않습니다. 이 저장소를 고쳐서 다시 올릴 때도 `.env`는 올리지 마세요.
   - FRED: https://fred.stlouisfed.org/docs/api/api_key.html 에서 회원가입 후 발급 (대부분의 그림에 필요)
   - ECOS: https://ecos.bok.or.kr/api/ 에서 발급 (그림 51)
   - 뉴욕 연준, 재무부, IMF, Yahoo Finance는 키가 필요 없습니다.

[그림 2] `f2_btfp.py`는 책 본문에서 단계별로 설명한 예제라서, 함수 파일을 쓰지 않고 FRED 요청 함수를 코드 안에 직접 적었습니다.
따옴표 안에 키를 넣으면 그 키를 쓰고, `"your api key"` 그대로 두면 `defs/.env`의 `FRED_API_KEY`를 읽습니다.

## 실행

저장소 폴더(`graphs_python_code/`)에서 실행합니다. 그림은 `pic_jpg/`, `pic_tif/`에 코드 이름으로 저장되고 화면에도 나타납니다.

```
.venv/bin/python f1_bank_deposits.py
```

- PyCharm에서는 파일을 열고 실행 버튼(Windows는 Shift+Ctrl+F10)을 누릅니다.
- 받은 자료는 `cache/`에 저장되어, 같은 날 다시 실행하면 API를 다시 부르지 않습니다.
- 캐시는 공개하지 않습니다. 처음 실행하면 `defs/` 옆에 `cache/` 폴더와 자료 출처별 하위 폴더(`fred_cache`, `ecos_cache`, `imf_cache`, `nyfed_cache`, `treasury_cache` 등 실제로 쓰는 것)가 자동으로 생기고, 받은 자료가 쌓입니다.
- 캐시 파일 이름에는 자료 이름과 기간이 들어갑니다(예: FRED는 `<시리즈ID>.<시작일>.<종료일>.parquet`). 모든 코드가 같은 폴더를 함께 쓰므로, 한 코드가 받은 자료를 다른 코드도 그대로 씁니다. `f2_btfp.py`의 직접 만든 함수도 같은 규칙을 따릅니다.
- 자료를 새로 받고 싶으면 해당 캐시 파일을 지우거나 함수에 `use_cache=False`를 넣습니다.

## 그림별 파일

| 그림 | 제목                                                      | 파일                              | 자료 출처           | data/ 파일                              |
|------|-----------------------------------------------------------|-----------------------------------|---------------------|-----------------------------------------|
| 1    | 은행예금 잔액과 은행업 ETF가격                            | `f1_bank_deposits.py`             | FRED, Yahoo Finance |                                         |
| 2    | BTFP 잔액과 정책금리                                      | `f2_btfp.py`                      | FRED                |                                         |
| 3    | CRE 대출, 주택대출, CRE가격과 공동주택가격 상승률         | `f3_cre.py`                       | FRED                |                                         |
| 4    | NYCB 주가와 은행업주가                                    | `f4_nycb.py`                      | FRED, Yahoo Finance |                                         |
| 6    | MMF와 은행예금 잔액                                       | `f6_mmf.py`                       | FRED                |                                         |
| 8    | MMF의 단기국채 투자잔액, 연준과 MMF의 RRP                 | `f8_mmf_rrp.py`                   | FRED, NY Fed        |                                         |
| 9    | 1일만기 국채담보 단기금융거래 이자율                      | `f9_tgcr_rate_percentile.py`      | FRED, NY Fed        |                                         |
| 10   | MMF의 RRP와 TGCR 거래 규모                                | `f10_tgcr_vol.py`                 | FRED, NY Fed        | mmf_rrp.csv, ny_rrp.csv                 |
| 11   | 1일물 금리                                                | `f11_on_rates.py`                 | FRED, NY Fed        |                                         |
| 12   | 연방기금금리와 정책금리                                   | `f12_ffr.py`                      | FRED                |                                         |
| 13   | 정책금리 기대확률(2025년 9월 17일 FOMC)                   | `f13_cme_rate_probability.py`     | CME FedWatch        | FedMeeting_20250917.csv                 |
| 14   | 월별 구인건수와 고용 증감                                 | `f14_nfp_adp.py`                  | FRED                |                                         |
| 15   | 베버리지커브: 구인율과 실업률                             | `f15_beveridge.py`                | FRED                |                                         |
| 15   | NFP 고용 수정 전후비교                                    | `f15_nfp_revision_1st_final.py`   | FRED                | nfp_revisions.csv                       |
| 16   | 직전 2개월 NFP 수정치                                     | `f16_nfp_2month_revisions.py`     | FRED                | nfp_revisions.csv                       |
| 17   | 베버리지커브: 구인율과 실업률                             | `f17_beveridge.py`                | FRED                |                                         |
| 18   | 소비자물가와 근원물가                                     | `f18_cpi_inflation.py`            | FRED                |                                         |
| 19   | 수입물가와 생산자물가                                     | `f19_imp_and_ppi.py`              | FRED                |                                         |
| 20   | Dot Plot (2024.9.18)                                      | `f20_dot_plot.py`                 | FRB                 | f_Dot_plot.xlsx                         |
| 21   | 제2차 세계대전 전후 국채 수익률, 소비자물가 상승률        | `f21_3mbills_cpi.py`              | FRED                |                                         |
| 22   | M2 증가율, 연방기금금리, 소비자물가 상승률                | `f22_m2_ffr_cpi.py`               | FRED                |                                         |
| 23   | 미국 예외주의에 대한 구글 트렌드와 S&P500                 | `f23_google_trend_sp500.py`       | FRED, Google Trends | f_google_trend.csv                      |
| 24   | 10년물 미국채 수익률과 S&P500                             | `f24_GB10.py`                     | FRED                |                                         |
| 25   | 미국 수익률 곡선                                          | `f25_yield.py`                    | FRED                |                                         |
| 26   | 월별 미국 국채 경매규모                                   | `f26_treasury_auctions.py`        | Treasury            | treasury_auctions_2024.csv              |
| 27   | Bid to cover ratio                                        | `f27_treasury_bid_to_cover.py`    | Treasury            | treasury_auctions_2024.csv              |
| 29   | 연준의 국채보유액과 연방정부의 연준예금(TGA)잔액          | `f29_soma_holdings.py`            | FRED                |                                         |
| 30   | 미국 연방정부 국채 잔액                                   | `f30_treasury_outstanding.py`     | Treasury            | MSPD_SumSecty_20010131_20250731.json    |
| 31   | 주요 국채 보유주체                                        | `f31_treasury_holders.py`         | FRED                |                                         |
| 32   | 프라이머리 딜러 국채 포지션                               | `f32_nyfed_pdposition.py`         | NY Fed              | TimeSeries.csv, nyfed_pdposition.csv    |
| 33   | 미국 재무부 TGA잔고                                       | `f33_tga.py`                      | FRED                |                                         |
| 34   | 연방정부 부채한도와 총부채                                | `f34_public_debt.py`              | Treasury            | DTS_DebtSubjLim_20051003_20250902.json  |
| 35   | 연준의 총자산 규모                                        | `f35_fedasset.py`                 | FRED                |                                         |
| 36   | 단기 자금시장 유동성과 주식시장 변동성                    | `f36_cb_tb_vix.py`                | FRED                |                                         |
| 37   | 은행 지급준비금과 1일물 금리(2024년 이후)                 | `f37_bank_reserves_sofr_iorb.py`  | FRED, NY Fed        |                                         |
| 40   | 연준의 RP 거래                                            | `f40_rp_vol.py`                   | FRED, NY Fed        |                                         |
| 41   | 1일물 단기자금 거래 규모                                  | `f41_effr_iorb.py`                | FRED, NY Fed        |                                         |
| 43   | 재무부 TGA 잔고 장기추이                                  | `f43_tga_2002.py`                 | FRED                |                                         |
| 44   | 미국 재정수지 흑자기                                      | `f44_gbalance.py`                 | FRED                |                                         |
| 45   | 미국채 수익률                                             | `f45_tb_yield_fed_tb_holdings.py` | FRED                |                                         |
| 47   | 월별 미재무부 국채 바이백 낙찰규모                        | `f47_treasury_buybacks.py`        | Treasury            | treasury_buybacks.csv                   |
| 48   | 달러 인덱스와 10년물 미국채 수익률                        | `f48_dollar_index_and_10y.py`     | FRED                |                                         |
| 49   | TPU, 소비자심리지수, 구글트렌드                           | `f49_tpu.py`                      | FRED, Google Trends | f_google_trend_recession.csv            |
| 50   | 국가별 미국채 보유액과 순매입액                           | `f50_foreign_holdings.py`         | Treasury TIC        | TIC_data.xlsx, f_foreign_holdings1.xlsx |
| 51   | 실질 달러인덱스, 금 현물가격, 실질실효 유로인덱스         | `f51_real_dollar_and_gold.py`     | FRED, BOK ECOS      |                                         |
| 52   | 전세계 외환보유액의 주요 통화별 구성                      | `f52_reserve.py`                  | IMF                 |                                         |
| 53   | 전세계 금 보유량, 국가별 보유량                           | `f53_gold_reserve.py`             | IMF                 |                                         |
| 54   | 수입증가율과 재고투자 증가율                              | `f54_import_inv.py`               | FRED                |                                         |
| 55   | 트럼프 대통령 재임기간 소비자물가, WTI, 달러인덱스 상승률 | `f55_cpi_wti_dollar.py`           | FRED                |                                         |
| 56   | 소비자물가지수와 PCE물가지수 상승률                       | `f56_cpi_pce.py`                  | FRED                |                                         |
| 17   | 베버리지커브: 구인율과 실업률 (colorful version)          | `f177_beveridge.py`               | FRED                |                                         |

- 그림 15는 두 판이 있습니다: `f15_beveridge.py`(베버리지커브), `f15_nfp_revision_1st_final.py`(NFP 수정 전후). 그림 17도 `f17_beveridge.py`와 색을 바꾼 `f177_beveridge.py`가 있습니다.
- 그림 15, 16의 `data/nfp_revisions.csv`는 `nfp_revision.py`로 다시 만들 수 있습니다.

## 함수 파일 (`defs/`)

코드 안에서 `from fred_api import fetch_fred_series`처럼 불러 씁니다. 각 파일의 첫머리에 사용법, 파라미터, 돌려주는 열이 적혀 있습니다.

| 파일 (defs/)                   | 주요 함수                                                                                | 내용                                                                                                                                                |
|--------------------------------|------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `plot_def.py`                  | `set_fonts()`, `plot_save(i=None)`, `nber_recession(start, end)`                         | 한글 폰트, 그림 저장(pic_jpg·pic_tif), 미국 경기침체 음영. `from plot_def import *`로 쓰면 `plt`, `pd`, `mdates`, `fetch_fred_series`도 함께 들어옴 |
| `fred_api.py`                  | `fetch_fred_series(series_id, start_date, end_date)`                                     | FRED 시계열. 그 밖에 `fetch_vintage_series`, `fetch_fred_vintage_dates`, `fetch_fred_as_of`(발표 시점별 값)                                         |
| `nyfed_api_all_rates.py`       | `fetch_all_secured_rates(start_date, end_date, rate_type_filter=None)`                   | 뉴욕 연준 1일물 금리(SOFR·TGCR·BGCR·EFFR·OBFR)와 분위수                                                                                             |
| `nyfed_api_rate_volume.py`     | `fetch_all_secured_rates_vol(start_date, end_date, rate_type_filter=None)`               | 1일물 거래 규모                                                                                                                                     |
| `nyfed_api.py`                 | `fetch_secured_rate`, `fetch_secured_series`, `fetch_soma_holdings`, `fetch_pdpositions` | secured rate 금리(·거래량), SOMA 보유 증권, 프라이머리 딜러 포지션                                                                                  |
| `nyfed_api_rp.py`              | `fetch_rp_operation(start_date, end_date, term="overnight")`                             | 연준 RP 운영                                                                                                                                        |
| `nyfed_rrp_vol.py`             | `fetch_rrp_vol(start_date, end_date)`                                                    | 연준 역RP 거래 규모                                                                                                                                 |
| `treasury_api.py`              | `fetch_debt_outstanding_json(...)`                                                       | 재무부 MSPD 국채 잔액 (data/의 json)                                                                                                                |
| `treasury_auctions_api.py`     | `fetch_securities_auction(...)`                                                          | 재무부 국채 경매 결과                                                                                                                               |
| `treasury_buybacks_api.py`     | `fetch_buybacks(start_date, end_date)`                                                   | 재무부 국채 바이백                                                                                                                                  |
| `treasury_debt_limit_api.py`   | `fetch_debt_limit_json(start_date, end_date, base_url)`                                  | 부채한도 대상 부채 (data/의 json)                                                                                                                   |
| `treasury_tic_api.py`          | `download_tic_holdings_soup(...)` 등                                                     | TIC 국가별 미국채 보유·매매                                                                                                                         |
| `imf_api.py`                   | `fetch_cofer_data`, `fetch_gold_data`                                                    | 외환보유액 통화 구성(COFER), 금 보유량                                                                                                              |
| `bok_ecos_api.py`              | `fetch_ecos_series(name, stat_code, item_code, ...)`                                     | 한국은행 ECOS                                                                                                                                       |

자주 쓰는 두 함수의 사용 예입니다.

```python
from plot_def import *          # set_fonts, plot_save, nber_recession, plt, pd, mdates, fetch_fred_series
set_fonts()                     # 운영체제에 맞는 한글 폰트

df = fetch_fred_series("IORB", start_date="2025-09-01", end_date="2025-09-30")
#   observation_date  IORB
# 0       2025-09-01   4.4

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(df["observation_date"], df["IORB"])
for peak, trough in nber_recession(start="2000-01-01", end="2025-09-30"):   # 미국 경기침체 음영
    ax.axvspan(peak, trough, color="gray", alpha=0.3)
plot_save()                     # pic_jpg/<코드 이름>.jpg, pic_tif/<코드 이름>.tif
```

한 코드에서 그림을 여러 장 그리면 `plot_save(i=1)`, `plot_save(i=2)`처럼 번호를 주어 파일 이름을 구분합니다.

## data/ 폴더

API로 받을 수 없어 직접 내려받은 자료입니다. 코드는 `data/파일이름`으로 읽습니다.

| 파일                                                                                | 내용                                                      |
|-------------------------------------------------------------------------------------|-----------------------------------------------------------|
| `FedMeeting_20250917.csv`                                                           | CME FedWatch에서 내려받은 FOMC 정책금리 확률 (그림 13)    |
| `FedMeeting_20261209.csv`                                                           | 같은 형식, 2026년 12월 FOMC                               |
| `f_Dot_plot.xlsx`                                                                   | FOMC 점도표(2024.9.18, 연준 SEP)를 옮겨 적은 것 (그림 20) |
| `f_google_trend.csv`, `f_google_trend_recession.csv`                                | Google Trends 검색량 (그림 23, 49)                        |
| `nfp_revisions.csv`                                                                 | `nfp_revision.py`가 만든 NFP 발표별 수정치 (그림 15, 16)  |
| `mmf_rrp.csv`, `ny_rrp.csv`                                                         | MMF·연준 역RP 자료 (그림 10)                              |
| `treasury_auctions_2024.csv`                                                        | 국채 경매 결과 (그림 26, 27)                              |
| `MSPD_SumSecty_20010131_20250731.json`                                              | 재무부 MSPD 국채 잔액 (그림 30)                           |
| `DTS_DebtSubjLim_20051003_20250902.json`                                            | 재무부 DTS 부채한도 (그림 34)                             |
| `TimeSeries.csv`, `nyfed_pdposition.csv`                                            | 뉴욕 연준 프라이머리 딜러 포지션 (그림 32)                |
| `treasury_buybacks.csv`                                                             | 국채 바이백 (그림 47)                                     |
| `TIC_data.xlsx`, `f_foreign_holdings1.xlsx`                                         | TIC 국가별 미국채 보유 (그림 50)                          |

## 그 밖의 파일

| 파일                              | 내용                                                                                                               |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------------|
| `nfp_revision.py`                 | FRED ALFRED에서 비농업고용(PAYEMS)의 1·2·3차 발표치를 받아 `data/nfp_revisions.csv`로 저장. 요청이 많아 몇 분 걸림 |

## 버전 기록

### 2026-11-01

책에 실린 코드와 거의 같은 첫 공개판(git tag `book-v1`)과 비교해 바뀐 점입니다.
책판 코드가 필요하면 `git checkout book-v1`로 받을 수 있습니다(돌아올 때는 `git checkout main`).
책판에는 `defs/` 함수 파일이 들어 있지 않아 그대로는 실행되지 않습니다. 책 본문과 코드를 대조할 때 쓰고, 실행은 지금 판으로 합니다.

**폴더와 실행 환경**

- 자료를 받는 함수 파일을 `defs/` 폴더에 모았습니다. 각 코드 첫 부분의 경로 블록이 `defs/`를 찾아 줍니다.
- API 키는 `defs/.env` 한 곳에 적습니다. 받은 자료는 `cache/`에 저장되어 같은 날 다시 실행하면 API를 부르지 않습니다.
- 저장소 맨 위에 그림 코드를 두고, 자료를 받는 함수(`defs/`)와 자료(`data/`), `requirements.txt`를 함께 공개합니다.
- `requirements.txt`에 코드를 확인한 패키지 버전을 고정해 적었습니다(Python 3.13). 시간이 지나 패키지가 바뀌어도 같은 결과를 얻을 수 있습니다.
- MIT 라이선스(`LICENSE`), 올리지 않는 파일 목록(`.gitignore`), API 키 견본(`defs/.env.example`)을 추가했습니다.
- jupyter notebook(`.ipynb`) 판을 없애고 `.py`만 씁니다. 노트북을 만들던 `py_to_jupyter.py`도 지웠습니다. `# %%` 셀 구분은 그대로 있어 PyCharm 등에서 셀 단위로 실행할 수 있습니다.
- 한국은행 ECOS 함수의 인자가 늘었습니다: `fetch_ecos_series(이름, 통계표, 항목1, 항목2, 항목3, 주기, start_date, end_date)`. 항목2, 3이 없으면 `""`을 넣습니다.

**오류 수정**

- [그림 2] `f2_btfp.py`: 키를 넣지 않으면 `KeyError: 'observations'`로 멈추던 문제. 키가 없으면 `defs/.env`의 키를 읽고, FRED 요청이 실패하면 FRED의 오류 메시지를 보여줍니다.
- [그림 51] `f51_real_dollar_and_gold.py`: 바뀐 ECOS 함수 인자에 맞게 고쳐 다시 실행됩니다.
- [그림 17] `f15_beveridge.py`, `f17_beveridge.py`, `f177_beveridge.py`: '가장 최근 달'로 표시한 큰 점이 실제로는 2025년 4월에 고정돼 있어 범례의 날짜와 맞지 않던 문제. 이제 자료의 마지막 달을 찍습니다. 범례에 같은 기간이 두 번 나오던 것도 고쳤습니다.
- [그림 49] `f49_tpu.py`: 무역정책 불확실성지수(EPUTRADE)를 그리면서 범례에는 '경제정책 불확실성지수'로 적혀 있던 것을 '무역정책 불확실성지수'로 고쳤습니다.
- [그림 1, 2] `f1_bank_deposits.py`, `f2_btfp.py`: 코드 안에 풀어 쓴 그림 저장 부분을 `plot_save()`와 같게 고쳤습니다. y축 천 단위 쉼표(소수점 자리 자동), tif 무손실 LZW 압축, jpg RGB 저장. 이제 다른 그림과 같은 형식의 파일이 나옵니다.
- [그림 2] `f2_btfp.py`: 코드 안의 FRED 함수가 매번 API를 부르던 것을, 다른 코드와 같은 공용 캐시(`cache/fred_cache`)를 쓰도록 고쳤습니다.
- `defs/bok_ecos_api.py`: 요청 URL을 출력할 때 API 키를 `***`로 가립니다.
- `nfp_revision.py`: FRED에 직접 요청하던 두 곳을 `defs/fred_api.py`의 `fetch_fred_vintage_dates()`, `fetch_fred_as_of()`로 바꿨습니다. 수정 내역을 계산해 `data/nfp_revisions.csv`로 저장하는 부분은 이 파일에 그대로 있고, 실행 방법과 결과도 같습니다.
- 책 그림을 그리지 않는 파일을 뺐습니다: 예제 `nyfed_api_vol_rate.py`(함수는 `defs/nyfed_api.py`의 `fetch_secured_series`), `treasury_receipts_outlays_ex.py`와 이 예제만 쓰던 `defs/treasury_receipts_outlays.py`·`data/MTS_RcptSrcOutlyAgcy_*.csv`, 원고 제출용 도구 `resize_tif_api.py`, 어느 그림도 쓰지 않던 `data/DTS_PubDebtTrans_20051003_20250925.json`(61.7MB).
- 최신 pandas에서 경고가 나지 않도록 `inplace=True` 대신 결과를 다시 변수에 넣습니다.

**범례 위치** (그림 내용은 같고 범례만 옮김)

| 그림                                  | 바뀐 점                                                              |
|---------------------------------------|---------------------------------------------------------------------|
| 1, 3, 4, 6, 22, 24, 48, 49, 51       | 좌축·우축 범례 두 개를 하나로 합쳐 선이 없는 자리에 둠                     |
| 2, 6(오른쪽), 22(오른쪽), 41(그림 42)   | 선과 겹치던 범례를 빈 자리로 옮김. 그림 2 오른쪽은 축 밖으로 나가던 것도 고침 |
| 15, 17                                | 범례를 2열로 줄여 선과 겹치지 않게 함                                   |
| 25(참고 그림)                          | 범례를 위쪽 가운데 2열로 둠                                           |
| 4, 49, 26(그림 26)                     | 빈 자리가 없어 y축 범위를 넓혀 범례 자리를 만듦(눈금 범위가 달라짐)         |
| 26(그림 28)                            | 막대가 그림을 채워 범례를 그림 아래에 가로로 둠                          |
| 52                                    | 면적 그래프 아래쪽 USD 영역에 범례를 3열로 둠                            |

**코드 안 설명**

- 모든 코드의 markdown 셀(`# %% [markdown]`)을 파이썬을 처음 배우는 학생도 읽을 수 있게 다시 썼습니다. 각 코드 첫 셀은 같은 순서로 되어 있습니다.
  - 이 코드가 하는 일: 어디서 어떤 자료를 받아 무엇을 그리는지
  - 그림이 다루는 내용: 그림이 보여주는 경제 현상을 쉬운 말로 설명
  - 결과물: 저장되는 그림 파일 이름(`pic_jpg/`, `pic_tif/`)
  - 필요한 파일: `defs/` 함수 파일, `data/` 자료 파일
- 중간 셀에는 실제로 쓰는 FRED 시리즈 ID와 단위, 자료 가공 순서, 그리는 방법을 적었습니다. 불러오지만 그림에 쓰지 않는 자료도 밝혔습니다.
- 책 본문에서 단계별로 설명한 그림 1, 2는 셀 구성을 그대로 두고 내용만 고쳤습니다. 책과 달라진 부분은 그림 2 첫 셀의 '책과 달라진 점'에 적었습니다.

