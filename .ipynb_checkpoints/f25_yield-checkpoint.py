# %% [markdown]
# # [그림 25] 미국 수익률 곡선
# ## required file
#   - plot_def.py
#   - fred_api.py
# %%
# 폰트 설정
from plot_def import *
set_fonts()

start = "2021-01-01"
end = "2025-12-31"

# %% [markdown]
# ## FRED 상의 시리즈 ID (Constant Maturity Treasury Rates)
# %%

series_ids = {
    "1day(RRP)": "RRPONTSYAWARD", #ON RRP
    "1day(IORB)": "IORB",
    "1day(EFFR)": "EFFR",
    "1M": "DGS1MO",
    "3M": "DGS3MO",
    "6M": "DGS6MO",
    "1Y": "DGS1",
    "2Y": "DGS2",
    "3Y": "DGS3",
    "5Y": "DGS5",
    "7Y": "DGS7",
    "10Y": "DGS10",
    "20Y": "DGS20",
    "30Y": "DGS30"
}


from fred_api import fetch_fred_series


# 모든 만기 데이터 가져오기
all_data = {}
for term, sid in series_ids.items():
    df = fetch_fred_series(sid,start_date=start, end_date=end)

    df.rename(columns={df.columns[-1]: "value"}, inplace=True)
    all_data[term] = df.set_index("observation_date")['value'].to_dict()
print(all_data)

# 병합
df_all_all = pd.DataFrame(all_data)
all_terms = list(series_ids.keys())
select1 = all_terms[0]
select2 = all_terms[3:]

terms_to_plot = [select1] + select2

# RRP 포함, IORB, EFFR 제외
df_all = df_all_all[terms_to_plot]

# 최신 날짜 데이터 선택
latest_date = df_all.dropna().index.max()
latest_curve = df_all.loc[latest_date]

from dateutil.relativedelta import relativedelta

# Convert string to datetime

latest_dt = latest_date  # already a Timestamp, which behaves like datetime

#1달 전
prev_dt = latest_dt - relativedelta(days=44)
july_dt = "2025-07-15"

#2달 전
two_dt = latest_dt - relativedelta(months=2)
june_dt = "2025-06-02"

# 가장 가까운 이전 날짜 찾기
prev_dt_actual = df_all.dropna().loc[:prev_dt].index.max()
prev_curve = df_all.loc[prev_dt_actual]
july_curve = df_all.loc[july_dt]

# 가장 가까운 2달전 날짜 찾기
two_dt_actual = df_all.dropna().loc[:two_dt].index.max()
two_curve = df_all.loc[two_dt_actual]
june_curve = df_all.loc[june_dt]

old_dt = "2023-09-01"
old_curve = df_all.loc[old_dt]

book_dt = "2025-08-28"
book_curve = df_all.loc[book_dt]

# 그래프1: Yield Curve

for i in [0,1]:
    if i == 0:
        fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

        ax.plot(old_curve.index, old_curve.values, color='black', ls="--", marker='o', lw=1, label=str(old_dt))
        ax.plot( july_curve.index, july_curve.values, color='blue', marker='o', lw=2, label=str(july_dt))

        # 코드를 실행하는 날에 가장 근접한 yield curve
        # ax.plot(latest_curve.index, latest_curve.values, color='black', marker='o', lw=2, label=str(latest_date.date()))

        # 책에 사용된 yield curve
        ax.plot(book_curve.index, book_curve.values, color='black', marker='o', lw=2, label=str(book_dt))

        ax.legend(loc='upper left', fontsize=10, bbox_to_anchor=(0.7, 1))
        ax.text(1, -0.12, '(만기)', ha='right', va='bottom', color='black', transform=ax.transAxes,
                 fontsize=12, rotation=0)
        ax.text(0, -0.15, f'출처: FRED', transform=ax.transAxes, fontsize=11)


    elif i == 1:

        # 그래프 그리기2: 개별 만기 국채 수익률 추이
        # 책 본문에 없음. 참고용으로 그림

        df1 = df_all_all[df_all_all.index >= '2024-01-01']
        selected_terms_to_plot = ['30Y', '1M', '10Y', '1day(IORB)', '1day(RRP)']

        df_filtered = df1.dropna(subset=selected_terms_to_plot)[selected_terms_to_plot]

        color_map = {
            '1day(IORB)': 'black',
            '1day(RRP)': 'orange',
            '1M': 'black',
            '10Y': 'blue',
            '30Y': 'green'
        }

        fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)

        # 모든 컬럼을 line plot (zip 이용)
        for col, series in zip(df_filtered, df_filtered.T.values):
            ax.plot(df_filtered.index, series, label=col, color=color_map.get(col), lw=2)

            ax.legend(loc='upper left', fontsize=10, bbox_to_anchor=(0.75, 1))
        ax.text(0, -0.15, f'출처: FRED, 최종 자료: {latest_dt.strftime("%Y-%m-%d")}', transform=ax.transAxes, fontsize=11)

    ax.text(0, 1.00, '(%)',  ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
    ax.grid(True, linestyle='--', color='gray', linewidth=0.7, alpha=0.3)


    # 저장 및 출력
    # python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴
    plot_save(i=i)