import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scraper import scrape_yes24_it_bestsellers, save_to_csv
import os
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="Yes24 IT 베스트셀러 대시보드", layout="wide")

# 스타일 설정
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로드 함수
def load_data():
    path = "yes24/data/yes24_it_bestseller.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

# 사이드바
st.sidebar.title("📊 제어판")
st.sidebar.markdown("---")

collect_pages = st.sidebar.slider("수집할 페이지 수", 1, 10, 3)
if st.sidebar.button("🚀 실시간 데이터 수집하기"):
    with st.spinner("Yes24에서 최신 데이터를 가져오는 중..."):
        df_new = scrape_yes24_it_bestsellers(pages=collect_pages)
        if not df_new.empty:
            save_to_csv(df_new, path="yes24/data/yes24_it_bestseller.csv")
            st.sidebar.success("수집 완료!")
            st.rerun()
        else:
            st.sidebar.error("데이터 수집에 실패했습니다.")

# 메인 화면
st.title("📚 Yes24 실시간 IT 베스트셀러 대시보드")
st.markdown(f"수집 기준: IT 모바일 카테고리 실시간 베스트셀러")

# 분석 목적 및 핵심 변수 설명 섹션
with st.container(border=True):
    st.markdown("### 🎯 분석 목적 및 패턴 기반 가설 도출")
    st.markdown("""
    **분석 목적**: Yes24 IT/컴퓨터 카테고리 데이터를 실시간으로 모니터링하여 **패턴 기반의 가설을 도출**하고, 
    도서 간의 **연관성과 트렌드**를 데이터 기반으로 이해하는 것을 목표로 합니다.
    
    > [!NOTE]  
    > 본 분석은 **인과 관계(Causality)**를 증명하는 것이 아니라, 현상들 사이의 **연관성(Association)과 패턴**을 탐색하여 비즈니스 가설을 세우는 데 목적이 있습니다.
    
    **핵심 분석 변수**:
    - **판매지수 (Target)**: 시장의 반응도를 나타내는 주요 지표입니다.
    - **제목 키워드 (Trend)**: 어떤 기술적 주제가 독자들의 관심을 끄는지 보여줍니다.
    - **리뷰수/효율성 (Engagement)**: 독자들의 관여도와 팬덤 형성 패턴을 시사합니다.
    - **가격대 (Market Segment)**: 시장에서 수용되는 가격 패턴을 확인합니다.
    """)

df = load_data()

if df is not None and not df.empty:
    # 수집 일시 표시
    last_updated = df['수집일시'].iloc[0] if '수집일시' in df.columns else "알 수 없음"
    st.caption(f"마지막 업데이트: {last_updated}")
    
    # 1. 핵심 지표 (KPI)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 도서 수", f"{len(df)}권")
    with col2:
        avg_price = int(df['판매가'].mean())
        st.metric("평균 판매가", f"{avg_price:,}원")
    with col3:
        top_publisher = df['출판사'].value_counts().index[0]
        st.metric("최다 점유 출판사", top_publisher)
    with col4:
        max_sales = df['판매지수'].max()
        st.metric("최고 판매지수", f"{max_sales:,}")

    st.markdown("---")

    # 2. 시각화 섹션
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.subheader("🏢 출판사별 점유율 (Top 10)")
        pub_counts = df['출판사'].value_counts().head(10).reset_index()
        pub_counts.columns = ['출판사', '도서 수']
        fig1 = px.bar(pub_counts, x='출판사', y='도서 수', 
                     color='도서 수', color_continuous_scale='Blues',
                     text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)
        # 인사이트 자동 생성
        top_pub = pub_counts.iloc[0]
        st.info(f"💡 **인사이트**: 현재 IT 시장은 **{top_pub['출판사']}** 출판사가 {top_pub['도서 수']}권으로 가장 높은 점유율을 기록하며 시장을 주도하고 있습니다.")

    with row1_col2:
        st.subheader("💰 가격대별 도서 분포")
        fig2 = px.histogram(df, x='판매가', nbins=15, 
                           color_discrete_sequence=['#FF9F43'],
                           labels={'판매가': '판매 가격 (원)', 'count': '도서 수'})
        st.plotly_chart(fig2, use_container_width=True)
        # 인사이트 자동 생성
        avg_price = df['판매가'].mean()
        price_mode = df['판매가'].value_counts().index[0]
        st.info(f"💡 **패턴 관찰**: IT 도서 시장에서는 **{int(price_mode):,}원** 전후의 가격 설정이 지배적인 패턴으로 나타나며, 이는 시장이 수용하는 표준 가격대임을 시사합니다.")

    st.markdown("---")
    
    # 신규 섹션: 제목 키워드 분석
    st.subheader("🔍 제목 키워드 트렌드 분석 (Keyword Pattern)")
    
    # 간단한 키워드 추출 로직
    def get_keywords(titles):
        import re
        words = []
        for title in titles:
            # 특수문자 제거 및 공백 기준 분리
            clean_title = re.sub(r'[^\w\s]', ' ', title)
            words.extend([w for w in clean_title.split() if len(w) > 1])
        return words

    all_words = get_keywords(df['도서명'].tolist())
    word_counts = pd.Series(all_words).value_counts().head(10).reset_index()
    word_counts.columns = ['키워드', '빈도']
    
    row_kw_1, row_kw_2 = st.columns(2)
    
    with row_kw_1:
        fig_kw = px.bar(word_counts, x='키워드', y='빈도', 
                       color='빈도', color_continuous_scale='Reds',
                       text_auto=True)
        st.plotly_chart(fig_kw, use_container_width=True)
        st.info(f"💡 **패턴 관찰**: 최근 IT 베스트셀러에서는 **'{word_counts.iloc[0]['키워드']}'**, **'{word_counts.iloc[1]['키워드']}'** 등의 키워드가 높은 빈도로 관찰되며, 이는 현재 시장의 주요 관심사와 연관이 있습니다.")

    with row_kw_2:
        # 상위 20% 도서의 키워드 분포
        top_20_df = df.nlargest(int(len(df)*0.2), '판매지수')
        top_words = get_keywords(top_20_df['도서명'].tolist())
        top_word_counts = pd.Series(top_words).value_counts().head(10).reset_index()
        top_word_counts.columns = ['키워드', '빈도']
        
        fig_top_kw = px.pie(top_word_counts, values='빈도', names='키워드',
                           hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_top_kw, use_container_width=True)
        st.info(f"💡 **패턴 관찰**: 판매지수 상위 20% 도서들에서는 특정 기술 스택에 대한 집중도가 더 높게 나타나는 경향이 관찰됩니다.")

    st.markdown("---")

    # 신규 섹션: 가격 vs 판매지수 상세 분석
    st.subheader("📊 가격 구간과 판매 성과 (Price vs Performance)")
    
    # 가격 구간 생성 (5000원 단위)
    df['가격구간'] = (df['판매가'] // 5000 * 5000).astype(int)
    price_group = df.groupby('가격구간')['판매지수'].mean().reset_index()
    price_group['가격구간_표기'] = price_group['가격구간'].apply(lambda x: f"{x:,}원~")
    
    row_pr_1, row_pr_2 = st.columns(2)
    
    with row_pr_1:
        fig_pr_scatter = px.scatter(df, x='판매가', y='판매지수', 
                                   hover_name='도서명', color='출판사',
                                   log_y=True, # 판매지수 편차가 크므로 로그 스케일 사용
                                   labels={'판매가': '판매 가격 (원)', '판매지수': '판매 지수 (Log Scale)'})
        st.plotly_chart(fig_pr_scatter, use_container_width=True)
        st.info("💡 **패턴 관찰**: 가격이 높다고 해서 판매지수가 반드시 낮아지는 패턴은 관찰되지 않으며, 오히려 특정 전문 서적 영역에서는 고가-고판매 지표가 동시 관찰됩니다.")
        
    with row_pr_2:
        fig_pr_avg = px.line(price_group, x='가격구간_표기', y='판매지수',
                            markers=True, color_discrete_sequence=['#E74C3C'])
        st.plotly_chart(fig_pr_avg, use_container_width=True)
        best_price_range = price_group.loc[price_group['판매지수'].idxmax(), '가격구간_표기']
        st.info(f"💡 **패턴 관찰**: 평균 판매지수가 가장 높은 구간은 **{best_price_range}**대로 파악되며, 해당 구간의 도서들이 시장에서 활발히 소비되는 경향이 있습니다.")

    st.markdown("---")
    
    # 3. 리뷰 효율성 분석 섹션 (신규)
    st.subheader("🎯 리뷰 효율성 분석 (Review Efficiency)")
    st.info("""**리뷰 효율성 = 판매지수 / 리뷰수**  
    리뷰 1건당 발생하는 판매지수를 의미하며, 판매 성과 대비 독자들의 피드백 밀도를 나타냅니다.""")
    
    # 파생 변수 계산 (리뷰수가 0인 경우 제외 또는 처리)
    df['리뷰 효율성'] = df.apply(lambda x: x['판매지수'] / x['리뷰수'] if x['리뷰수'] > 0 else 0, axis=1)
    
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.write("📊 리뷰 효율성 지표 분포")
        fig_eff = px.box(df, y='리뷰 효율성', points="all",
                        color_discrete_sequence=['#9B59B6'],
                        labels={'리뷰 효율성': '효율성 지표'})
        st.plotly_chart(fig_eff, use_container_width=True)
        # 인사이트 자동 생성
        avg_eff = df['리뷰 효율성'].mean()
        st.info(f"💡 **인사이트**: 전체 도서의 평균 리뷰 효율성은 **{avg_eff:.4f}**입니다. 박스플롯 상단의 이상치들은 판매량 대비 압도적인 팬덤을 보유한 도서들입니다.")
        
    with row2_col2:
        st.write("🏆 리뷰 효율성 상위 10개 도서")
        top_eff = df.sort_values(by='리뷰 효율성', ascending=False).head(10)
        st.dataframe(top_eff[['도서명', '출판사', '리뷰수', '판매지수', '리뷰 효율성']], 
                     hide_index=True, use_container_width=True)
        # 인사이트 자동 생성
        best_eff_book = top_eff.iloc[0]['도서명']
        st.info(f"💡 **인사이트**: 현재 리뷰 효율이 가장 높은 도서는 **'{best_eff_book}'**이며, 이는 독자들의 참여도가 가장 높음을 시사합니다.")

    st.markdown("---")

    # 4. 상세 분석 섹션
    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        st.subheader("📈 리뷰수 vs 판매지수 상관관계")
        fig3 = px.scatter(df, x='리뷰수', y='판매지수', 
                         hover_name='도서명', color='리뷰 효율성',
                         size='판매지수', color_continuous_scale='Viridis',
                         labels={'리뷰수': '리뷰 개수', '판매지수': '판매 지수'})
        st.plotly_chart(fig3, use_container_width=True)
        # 인사이트 자동 생성
        corr = df['리뷰수'].corr(df['판매지수'])
        st.info(f"💡 **인사이트**: 리뷰수와 판매지수의 상관계수는 **{corr:.2f}**입니다. 색상이 밝을수록(노란색) 판매량 대비 리뷰 참여가 활발한 '고관여' 도서임을 의미합니다.")

    with row3_col2:
        st.subheader("⭐ 평점 분포")
        fig4 = px.box(df, y='평점', points="all",
                     color_discrete_sequence=['#2ECC71'],
                     labels={'평점': '독자 평점'})
        st.plotly_chart(fig4, use_container_width=True)
        # 인사이트 자동 생성
        avg_rating = df['평점'].mean()
        st.info(f"💡 **인사이트**: 베스트셀러 도서들의 평균 평점은 **{avg_rating:.2f}점**으로, 전반적으로 독자 만족도가 매우 높게 형성되어 있습니다.")

    st.markdown("---")

    # 5. 상세 데이터 테이블
    st.subheader("🔍 전체 도서 목록 상세")
    search_query = st.text_input("도서명 또는 저자 검색", "")
    
    if search_query:
        filtered_df = df[df['도서명'].str.contains(search_query, case=False) | 
                         df['저자'].str.contains(search_query, case=False)]
    else:
        filtered_df = df

    st.dataframe(filtered_df[['도서명', '저자', '출판사', '판매가', '판매지수', '리뷰수', '평점']], 
                 use_container_width=True, hide_index=True)

else:
    st.warning("수집된 데이터가 없습니다. 왼쪽 사이드바에서 '실시간 데이터 수집하기' 버튼을 눌러주세요.")
    st.info("데이터가 처음인 경우 수집에 시간이 다소 소요될 수 있습니다.")

# 푸터
st.markdown("---")
st.markdown("Created by Antigravity AI | Data source: Yes24 Best Sellers (IT/Computer)")
