# [그림 26] 월별 미국 국채 경매규모
# [그림 28] 미국 국채 낙찰기관별 비중
# 두 개의 그래프를 모두 그림
# 첫 번째 그림 화면출력 후 그림창을 닫아야 다음 그림이 출력됨

# 필요한 file

# treasury_auctions_api.py : Treasury Fiscal Data, Treasury Auctions Data에서 data fetch
# plot_def.py : 한글폰트 추가, 그래프 저장

# 한글 폰트 추가

from plot_def import *
set_fonts()

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

from matplotlib_colors import color_names

from plot_def import *


#=================================
# 필요시 자료를 fetch 해서 csv로 저장하는 def


from treasury_auctions_api import *

start = "2023-01-01"
end = "2025-12-31"

output_path = fetch_securities_auction(start_date=start, end_date=end)
#=================================

output_file = "data/treasury_auctions_2024.csv"


df=pd.read_csv(output_file)


# --- 3. 데이터 전처리 ---
# 날짜, 숫자 변환
df['auction_date'] = pd.to_datetime(df['auction_date'])
df['issue_date'] = pd.to_datetime(df['issue_date'])
# 숫자 컬럼 변환 및 단위 조정 (단위: 십억 달러)
cols_to_convert = [
    'total_accepted', 'direct_bidder_accepted', 'indirect_bidder_accepted',
    'primary_dealer_accepted', 'soma_accepted', 'fima_noncomp_accepted', 'treas_retail_accepted'
]
for col in cols_to_convert:
    df[col] = pd.to_numeric(df[col], errors='coerce') /1e9


# 날짜 변환 실패(NaT) 행 제거
df.dropna(subset=['auction_date', 'issue_date'], inplace=True)

# issue_date 기준으로 2024년 데이터 필터링
df = df[df['auction_date'].dt.year >= 2023]
df = df[df['auction_date']<"2025-09-01"]

# 월(month) 컬럼 생성
df['month'] = df['auction_date'].dt.month
df['day'] = df['auction_date'].dt.day
df['year_month'] = df['auction_date'].dt.to_period('M')


# 필요한 증권 종류만 필터링
security_types_to_plot = ['Bill', 'Note', 'Bond']
print(df[df['security_type']=='Bill']['security_term'].unique())

for i in [1, 2]:

    if i == 1:
        fig, ax = plt.subplots(1, 2, figsize=(8, 4.5), constrained_layout=True)

        for idx, security_term_to_plot in enumerate([
            ['4-Week', '6-Week', '8-Week', '12-Week'],   # 첫 번째 subplot (단기 Bill)
            ['10-Year', '20-Year', '30-Year']            # 두 번째 subplot (장기 Note/Bond)
        ]):

            df_filtered = df[df['security_term'].isin(security_term_to_plot)]

            monthly_counts = (
                df_filtered.groupby(['year_month', 'security_term'])['total_accepted']
                .sum()
                .unstack(fill_value=0)
            )
            print(monthly_counts)
            monthly_counts.index = monthly_counts.index.to_timestamp()
            colors = sns.color_palette("viridis", n_colors=len(monthly_counts.columns))

            bottom = None
            for col, color in zip(monthly_counts.columns, colors):
                ax[idx].bar(
                    monthly_counts.index,
                    monthly_counts[col],
                    label=col,
                    bottom=bottom,
                    width=20,
                    color=color
                )
                bottom = monthly_counts[col].values if bottom is None else bottom + monthly_counts[col].values

            # 축 및 서식
            ax[idx].yaxis.set_major_locator(plt.MaxNLocator(integer=True))
            ax[idx].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
            ax[idx].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

            ax[idx].text(0, 1.02, '(10억 달러)', ha='left', va='bottom',
                         transform=ax[idx].transAxes, fontsize=12)
            ax[idx].legend(loc='upper left')

        ax[0].text(0, -0.15, '출처: Treasury Fiscal Data, Treasury Securities Auctions Data', transform=ax[0].transAxes, fontsize=10)
    elif i == 2:


        import matplotlib.pyplot as plt
        import seaborn as sns


        # 필요한 security_type 필터링
        df = df[df['security_type'].isin(security_types_to_plot)]


        acceptance_cols = [
            'direct_bidder_accepted', 'indirect_bidder_accepted',
            'primary_dealer_accepted', 'soma_accepted'
        ]


        # 월별 평균 비율 계산
        ratio_cols = [col + '_ratio' for col in acceptance_cols]

        for col in acceptance_cols:
            df[col + '_ratio'] = (df[col] / df['total_accepted']) *100


        monthly_avg = (df.groupby(['year_month', 'security_type'])[ratio_cols].mean().reset_index())

        monthly_avg['year_month'] = monthly_avg['year_month'].dt.to_timestamp()

        label_map={'direct_bidder_accepted_ratio': "Direct",
                   'indirect_bidder_accepted_ratio': "Indirect",
                   'primary_dealer_accepted_ratio': "Primary Dealer",
                   'soma_accepted_ratio': "SOMA"


        }

        colors = sns.color_palette("viridis", n_colors=len(acceptance_cols))
        # 시각화
        fig, ax = plt.subplots(1, 2, figsize=(9,4.5 ), constrained_layout=True)


        for idx, sec_type in enumerate(['Bill', 'Bond']):
            if sec_type == 'Bill':
                data = monthly_avg[(monthly_avg['security_type'] == 'Bill')]
            elif sec_type == 'Note':
                data = monthly_avg[(monthly_avg['security_type'] == 'Note')]
            else:
                data = monthly_avg[monthly_avg['security_type'] == 'Bond']

            grouped = data.groupby('year_month')[ratio_cols].mean()

            bottom = None

            for col, color in zip(ratio_cols, colors):
                ax[idx].bar(
                    grouped.index,
                    grouped[col].fillna(0),
                    bottom=bottom,
                    label=label_map.get(col,col),
                    width=20,
                    color=color
                )
                bottom =grouped[col].values if bottom is None else bottom + grouped[col].values

            # 축 및 서식
            ax[idx].yaxis.set_major_locator(plt.MaxNLocator(integer=True))
            ax[idx].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
            ax[idx].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))


            ax[idx].text(0, 1.02, '(%)', ha='left', va='bottom',
                           transform=ax[idx].transAxes, fontsize=12)
            ax[idx].text(0.45, 1.02, f'{sec_type}s', ha='left', va='bottom', fontsize=12, transform=ax[idx].transAxes)

        ax[0].text(0, -0.15, "출처: Treasury Auctions Data", fontsize=12, transform=ax[0].transAxes)
        ax[0].legend(loc="upper left", bbox_to_anchor=(0.02, 0.5))


    # 저장 및 출력
    # python py 파일 이름과 동일한 이름으로 그림 파일을 tif, jpg로 저장하는 루틴

    plot_save(i=i)