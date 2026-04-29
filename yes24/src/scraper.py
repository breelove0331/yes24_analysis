import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from datetime import datetime

def scrape_yes24_it_bestsellers(pages=3):
    """
    Yes24 IT/컴퓨터 카테고리 베스트셀러를 수집합니다.
    pages: 수집할 페이지 수 (기본 3페이지, 약 72권)
    """
    data = []
    category_number = "001001003"  # IT 모바일 카테고리
    
    for page in range(1, pages + 1):
        url = f"https://www.yes24.com/product/category/BestSellerContents?categoryNumber={category_number}&pageNumber={page}&pageSize=24"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            
            items = soup.select(".item_info")
            if not items:
                break
                
            for item in items:
                title = item.select_one(".gd_name").text.strip() if item.select_one(".gd_name") else "N/A"
                subtitle = item.select_one(".gd_nameE").text.strip() if item.select_one(".gd_nameE") else ""
                author = item.select_one(".info_auth a").text.strip() if item.select_one(".info_auth a") else "N/A"
                publisher = item.select_one(".info_pub a").text.strip() if item.select_one(".info_pub a") else "N/A"
                
                # 정가
                price_el = item.select_one(".info_price .yes_m")
                price = int(re.sub(r'[^0-9]', '', price_el.text)) if price_el else 0
                    
                # 판매가
                sale_price_el = item.select_one(".info_price .yes_b")
                sale_price = int(re.sub(r'[^0-9]', '', sale_price_el.text)) if sale_price_el else 0
                    
                # 판매지수
                sales_index_el = item.select_one(".saleNum")
                sales_index = int(re.sub(r'[^0-9]', '', sales_index_el.text)) if sales_index_el else 0
                    
                # 리뷰수
                review_el = item.select_one(".rating_rvCount a")
                review_count = int(re.sub(r'[^0-9]', '', review_el.text)) if review_el else 0
                    
                # 평점
                rating_el = item.select_one(".rating_grade .yes_b")
                rating = float(rating_el.text) if rating_el else 0.0
                        
                data.append({
                    '도서명': title,
                    '부제': subtitle,
                    '저자': author,
                    '출판사': publisher,
                    '정가': price,
                    '판매가': sale_price,
                    '판매지수': sales_index,
                    '리뷰수': review_count,
                    '평점': rating,
                    '수집일시': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            break
            
    if data:
        df = pd.DataFrame(data)
        df = df.drop_duplicates(subset=['도서명'])
        return df
    return pd.DataFrame()

def save_to_csv(df, path="yes24/data/yes24_it_bestseller.csv"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} items to {path}")

if __name__ == "__main__":
    # 독립 실행 시 5페이지 수집
    df = scrape_yes24_it_bestsellers(pages=5)
    if not df.empty:
        save_to_csv(df)
