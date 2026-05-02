import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
import koreanize_matplotlib
import os

# 설정
BASE_DIR = r"c:\Users\View\wiset-inflearn\yes24"
DATA_PATH = os.path.join(BASE_DIR, "data", "yes24_it_bestseller.csv")
SAVE_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(SAVE_DIR, exist_ok=True)

# 1. 데이터 로드 및 전처리
df = pd.read_csv(DATA_PATH)

# 지표 재정의 (리뷰 효율성)
df['review_efficiency'] = df.apply(lambda x: x['리뷰수'] / x['판매지수'] if x['판매지수'] > 0 else 0, axis=1)

# 상위 2개 이상치 식별
outliers = df.nlargest(2, 'review_efficiency')
df_cleaned = df.drop(outliers.index)

print(f"--- Data Preprocessing ---")
print(f"식별된 이상치:\n{outliers[['도서명', '리뷰수', '판매지수', 'review_efficiency']].to_markdown(index=False)}")
print(f"\n이상치의 의미: 판매지수 대비 리뷰수가 비정상적으로 높아, 일반적인 구매 패턴에서 벗어난 '초기 마케팅' 또는 '강력한 니치 팬덤' 도서로 해석됨.")

# 2. 분석 1: 이상치 제거 전후 비교 시각화
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Before
sns.regplot(data=df, x='리뷰수', y='판매지수', ax=axes[0], scatter_kws={'alpha':0.5}, line_kws={'color':'red'})
axes[0].set_title(f'Before: 이상치 포함 (Corr: {df["리뷰수"].corr(df["판매지수"]):.4f})', fontsize=13)
axes[0].grid(True, linestyle='--', alpha=0.7)

# After
sns.regplot(data=df_cleaned, x='리뷰수', y='판매지수', ax=axes[1], scatter_kws={'alpha':0.5}, line_kws={'color':'blue'})
axes[1].set_title(f'After: 이상치 제거 후 (Corr: {df_cleaned["리뷰수"].corr(df_cleaned["판매지수"]):.4f})', fontsize=13)
axes[1].grid(True, linestyle='--', alpha=0.7)

plt.suptitle('데이터 클렌징 전후 상관관계 비교', fontsize=16, fontweight='bold')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(os.path.join(SAVE_DIR, "before_after_comparison.png"))
plt.close()

# 3. 분석 2: Ridge Regression (다중 변수 분석)
corr_raw = df_cleaned['리뷰수'].corr(df_cleaned['판매지수']) # 변수 정의 복구

features = ['리뷰수', '평점', '정가']
X = df_cleaned[features]
y = df_cleaned['판매지수']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

ridge = Ridge(alpha=1.0)
ridge.fit(X_scaled, y)

coef_df = pd.DataFrame({
    'Feature': features,
    'Coefficient': ridge.coef_
})

print(f"\n--- Ridge Regression Coefficients ---")
print(coef_df.to_markdown(index=False))

plt.figure(figsize=(10, 6))
sns.barplot(data=coef_df, x='Feature', y='Coefficient', palette='viridis', hue='Feature', legend=False)
plt.title('판매지수 영향력 분석 (Ridge Regression)', fontsize=15)
plt.axhline(0, color='black', linewidth=1)
plt.savefig(os.path.join(SAVE_DIR, "ridge_coefficients.png"))
plt.close()

print(f"\n--- 최종 분석 인사이트 ---")
print(f"1. 직접 상관관계: 리뷰수와 판매지수의 상관계수는 {corr_raw:.4f}입니다.")
print(f"2. 영향력 분석: 판매지수에 가장 큰 영향을 주는 변수는 '{coef_df.iloc[coef_df['Coefficient'].abs().idxmax()]['Feature']}'입니다.")
