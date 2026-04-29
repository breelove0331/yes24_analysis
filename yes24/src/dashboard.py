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
with st.expander("🎯 분석 목적 및 핵심 변수 안내", expanded=True):
    st.markdown("""
    **분석 목적**: Yes24 IT/컴퓨터 카테고리 데이터를 실시간으로 모니터링하여 **시장 트렌드를 즉각 파악**하고, 
    도서의 성공 요인(인기 비결)을 데이터 기반으로 이해하는 것을 목표로 합니다.
    
    **핵심 분석 변수**:
    1. **판매지수 (Target)**: 도서의 흥행 성적을 나타내는 가장 중요한 지표입니다.
    2. **리뷰수 (Driver)**: 독자의 반응과 입소문을 대변하며, 판매지수와 높은 상관관계를 보입니다.
    3. **정가 (Constraint)**: 구매 결정 시 독자들이 느끼는 가격 저항선을 확인하는 핵심 수치입니다.
    4. **출판사 (Brand)**: IT 도서 시장 내의 브랜드 파워와 마케팅 능력을 나타내는 범주형 변수입니다.
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
        st.info(f"💡 **인사이트**: IT 도서의 평균 가격은 **{int(avg_price):,}원**이며, 가장 많이 분포된 가격대는 **{int(price_mode):,}원** 전후로 형성되어 있습니다.")

    st.markdown("---")
    
    # 3. 리뷰 효율성 분석 섹션 (신규)
    st.subheader("🎯 리뷰 효율성 분석 (Review Efficiency)")
    st.info("""**리뷰 효율성 = 리뷰수 / 판매지수**  
    판매량 대비 독자들의 피드백 활동이 얼마나 활발한지를 나타냅니다.""")
    
    # 파생 변수 계산
    df['리뷰 효율성'] = df.apply(lambda x: x['리뷰수'] / x['판매지수'] if x['판매지수'] > 0 else 0, axis=1)
    
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
