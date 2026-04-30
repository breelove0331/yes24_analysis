import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import os
import re

# 설정
DATA_PATH = "yes24/data/yes24_it_bestseller.csv"
SAVE_DIR = "yes24/images"
os.makedirs(SAVE_DIR, exist_ok=True)

# 데이터 로드
df = pd.read_csv(DATA_PATH)

# 1. 출판사 점유율 (Top 10)
plt.figure(figsize=(10, 6))
df['출판사'].value_counts().head(10).plot(kind='bar', color='skyblue')
plt.title('출판사 점유율 (Top 10)', fontsize=15)
plt.xlabel('출판사')
plt.ylabel('도서 수')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/publisher_share.png")
plt.close()

# 2. 가격대별 분포
plt.figure(figsize=(10, 6))
sns.histplot(df['판매가'], bins=15, kde=True, color='orange')
plt.title('가격대별 도서 분포', fontsize=15)
plt.xlabel('판매 가격 (원)')
plt.ylabel('도서 수')
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/price_dist.png")
plt.close()

# 3. 키워드 분석 (상위 10개)
def get_keywords(titles):
    words = []
    for title in titles:
        clean_title = re.sub(r'[^\w\s]', ' ', str(title))
        words.extend([w for w in clean_title.split() if len(w) > 1])
    return words

all_words = get_keywords(df['도서명'].tolist())
word_counts = pd.Series(all_words).value_counts().head(10)

plt.figure(figsize=(10, 6))
word_counts.plot(kind='bar', color='salmon')
plt.title('제목 키워드 빈도 (Top 10)', fontsize=15)
plt.xlabel('키워드')
plt.ylabel('빈도')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/keyword_trend.png")
plt.close()

# 4. 리뷰수 vs 판매지수 산점도
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='리뷰수', y='판매지수', hue='평점', size='판매지수', sizes=(20, 200), palette='viridis')
plt.title('리뷰수 vs 판매지수 상관관계', fontsize=15)
plt.xlabel('리뷰 수')
plt.ylabel('판매 지수')
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/review_sales_scatter.png")
plt.close()

# 5. 가격 구간별 평균 판매지수
df['가격구간'] = (df['판매가'] // 5000 * 5000)
price_avg = df.groupby('가격구간')['판매지수'].mean().reset_index()
plt.figure(figsize=(10, 6))
plt.plot(price_avg['가격구간'], price_avg['판매지수'], marker='o', color='red', linestyle='-')
plt.title('가격 구간별 평균 판매지수', fontsize=15)
plt.xlabel('가격 구간 (원)')
plt.ylabel('평균 판매지수')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/price_performance.png")
plt.close()

print(f"이미지 생성이 완료되었습니다. 저장 위치: {SAVE_DIR}")
