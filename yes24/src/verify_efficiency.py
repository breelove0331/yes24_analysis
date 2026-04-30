import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import os

# 설정
DATA_PATH = "yes24/data/yes24_it_bestseller.csv"
SAVE_DIR = "yes24/images"
os.makedirs(SAVE_DIR, exist_ok=True)

# 데이터 로드
df = pd.read_csv(DATA_PATH)

# 1. 파생 변수 생성 (안전하게 처리)
df['review_efficiency'] = df.apply(lambda x: x['리뷰수'] / x['판매지수'] if x['판매지수'] > 0 else 0, axis=1)

# 2. 상관계수 분석
correlation = df['review_efficiency'].corr(df['판매지수'])

# 3. 시각화 (산점도 + 추세선)
plt.figure(figsize=(10, 6))
sns.regplot(data=df, x='review_efficiency', y='판매지수', scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
plt.title('리뷰 효율성 vs 판매지수 상관관계 검증', fontsize=15)
plt.xlabel('리뷰 효율성 (리뷰수 / 판매지수)')
plt.ylabel('판매지수')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/efficiency_verification_scatter.png")
plt.close()

# 4. 그룹 비교 분석
# 효율성을 기준으로 3개 그룹으로 분할 (qcut 사용)
df['efficiency_group'] = pd.qcut(df['review_efficiency'], q=3, labels=['Low', 'Mid', 'High'])
group_stats = df.groupby('efficiency_group')['판매지수'].mean().reset_index()

# 결과 출력용 텍스트 생성
print(f"--- Analysis Results ---")
print(f"Pearson Correlation: {correlation:.4f}")
print(f"\n--- Group Comparison (Mean Sales Index) ---")
print(group_stats.to_markdown(index=False))

# 해석을 위한 관찰 포인트
if abs(correlation) < 0.1:
    strength = "관계 없음 (매우 약함)"
elif abs(correlation) < 0.3:
    strength = "약한 연관성"
else:
    strength = "상당한 연관성"
    
print(f"\nCorrelation Strength: {strength}")
