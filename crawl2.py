import re
import time
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
# import mariadb  # mariadb 미설치로 주석 처리

# =========================================================
# DB 접속 정보 (본인 환경에 맞게 수정하세요)
# =========================================================
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",          # 본인 계정으로 변경
    "password": "1234",      # 본인 비밀번호로 변경
}
DB_NAME = "job_crawler_db"   # 새로 만들 DB 이름

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# =========================================================
# 1. 크롤링 함수 (requests + BeautifulSoup, 브라우저 불필요)
# =========================================================
def crawl_jobkorea(keyword, start_page=1, end_page=1):
    job_list = []
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"https://www.jobkorea.co.kr/Search?stext={encoded_keyword}"

    for current_page in range(start_page, end_page + 1):
        print(f"[진행 중] {current_page} 페이지 수집 중...")

        try:
            resp = requests.get(f"{url}&Page_No={current_page}", headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[에러] {current_page} 페이지 요청 실패: {e}")
            continue

        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')

        # 2026년 리뉴얼된 잡코리아 구조 (data-sentry-component 속성 기반)
        post_list = soup.select('div[data-sentry-component="CardJob"]')

        print(f"[디버그] {current_page} 페이지에서 찾은 공고 수: {len(post_list)}")

        if not post_list:
            debug_path = f"debug_page_{current_page}.html"
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[디버그] 선택자가 안 맞는 것 같아 원본 HTML을 '{debug_path}'로 저장했습니다.")

        for post in post_list:
            try:
                title_element = post.select_one('a[data-sentry-component="Title"]')
                if not title_element:
                    continue

                post_title = title_element.get_text(strip=True)
                job_url = title_element['href']  # 이미 절대경로 URL

                match = re.search(r"/GI_Read/(\d+)", job_url)
                platform_post_id = match.group(1) if match else ""

                company_span = post.select_one("span.mb-5 a span")
                company_name = company_span.get_text(strip=True) if company_span else ""

                # 지역 / 직무 / 급여가 순서대로 GrayChip으로 표시됨
                chips = [c.get_text(strip=True) for c in post.select('div[data-sentry-component="GrayChip"] span.truncate')]
                region = chips[0] if len(chips) > 0 else ""
                pay = chips[2] if len(chips) > 2 else "면접 후 결정"

                # 목록 화면엔 학력/고용형태 정보가 더 이상 표시되지 않음
                edu_require = ""
                emp_type = ""

                career_element = post.select_one("span.flex-shrink-0.text-gray700.text-typo-c1-13")
                personal_history = career_element.get_text(strip=True) if career_element else ""

                end_at = "상시채용"
                for span in post.find_all("span"):
                    if "마감" in span.get_text():
                        end_at = span.get_text(strip=True)
                        break

                crawled_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                job_list.append({
                    "source": "잡코리아",
                    "platform_post_id": platform_post_id,
                    "job_part": keyword,
                    "company_name": company_name,
                    "post_title": post_title,
                    "region": region,
                    "personal_history": personal_history,
                    "edu_require": edu_require,
                    "emp_type": emp_type,
                    "pay": pay,
                    "end_at": end_at,
                    "crawled_at": crawled_at,
                    "job_url": job_url
                })
            except Exception as e:
                print(f"데이터 파싱 에러: {e}")
                continue

        # 사이트에 부담을 덜 주기 위한 딜레이
        time.sleep(1.5)

    return job_list


# =========================================================
# 2. DB / 테이블 생성 함수 (DB가 아예 없을 때 최초 1회 실행)
# =========================================================
# def setup_database():
#     """DB_NAME 데이터베이스와 job_posts 테이블이 없으면 생성"""
#     try:
#         # database 인자 없이 서버에만 접속
#         conn = mariadb.connect(**DB_CONFIG)
#     except mariadb.Error as e:
#         print(f"MariaDB 서버 연결 에러: {e}")
#         raise
#
#     cursor = conn.cursor()
#
#     cursor.execute(
#         f"CREATE DATABASE IF NOT EXISTS {DB_NAME} "
#         f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
#     )
#     conn.commit()
#     cursor.close()
#     conn.close()
#     print(f"데이터베이스 '{DB_NAME}' 준비 완료.")
#
#     # 이제 해당 DB로 다시 접속해서 테이블 생성
#     conn = mariadb.connect(**DB_CONFIG, database=DB_NAME)
#     cursor = conn.cursor()
#
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS job_posts (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             source VARCHAR(50),
#             platform_post_id VARCHAR(50) UNIQUE,
#             job_part VARCHAR(100),
#             company_name VARCHAR(255),
#             post_title VARCHAR(500),
#             region VARCHAR(100),
#             personal_history VARCHAR(100),
#             edu_require VARCHAR(100),
#             emp_type VARCHAR(100),
#             pay VARCHAR(100),
#             end_at VARCHAR(100),
#             crawled_at DATETIME,
#             job_url VARCHAR(500)
#         ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
#     """)
#     conn.commit()
#     cursor.close()
#     conn.close()
#     print("테이블 'job_posts' 준비 완료.")


# =========================================================
# 3. 데이터 저장 함수
# =========================================================
# def save_to_mariadb(job_list):
#     if not job_list:
#         print("저장할 데이터가 없습니다.")
#         return
#
#     try:
#         conn = mariadb.connect(**DB_CONFIG, database=DB_NAME)
#     except mariadb.Error as e:
#         print(f"DB 연결 에러: {e}")
#         return
#
#     cursor = conn.cursor()
#
#     insert_query = """
#         INSERT INTO job_posts
#         (source, platform_post_id, job_part, company_name, post_title,
#          region, personal_history, edu_require, emp_type, pay, end_at, crawled_at, job_url)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         ON DUPLICATE KEY UPDATE
#             post_title = VALUES(post_title),
#             crawled_at = VALUES(crawled_at)
#     """
#
#     inserted, skipped = 0, 0
#     for job in job_list:
#         try:
#             cursor.execute(insert_query, (
#                 job["source"],
#                 job["platform_post_id"],
#                 job["job_part"],
#                 job["company_name"],
#                 job["post_title"],
#                 job["region"],
#                 job["personal_history"],
#                 job["edu_require"],
#                 job["emp_type"],
#                 job["pay"],
#                 job["end_at"],
#                 job["crawled_at"],
#                 job["job_url"]
#             ))
#             inserted += 1
#         except mariadb.Error as e:
#             print(f"INSERT 실패 (post_id={job.get('platform_post_id')}): {e}")
#             skipped += 1
#             continue
#
#     conn.commit()
#     cursor.close()
#     conn.close()
#
#     print(f"DB 저장 완료: 성공 {inserted}건 / 실패 {skipped}건")


# =========================================================
# 4. 실행부
# =========================================================
def main():
    keyword = "파이썬 개발자"
    start_page = 1   # 크롤링 시작 페이지
    end_page = 5     # 크롤링 종료 페이지 (예: 1~5페이지)

    # 1) DB / 테이블 최초 준비 (mariadb 미설치로 주석 처리)
    # setup_database()

    # 2) 크롤링 실행
    result = crawl_jobkorea(keyword, start_page=start_page, end_page=end_page)

    if not result:
        print("⚠️ 수집된 데이터가 없습니다. 사이트 구조가 바뀌었거나 크롤링이 차단됐을 수 있습니다.")
        return

    # 3) 엑셀로 확인용 저장
    df = pd.DataFrame(result)
    columns_order = [
        "source", "platform_post_id", "job_part", "company_name", "post_title",
        "region", "personal_history", "edu_require", "emp_type", "pay", "end_at", "crawled_at", "job_url"
    ]
    df = df[columns_order]
    df.to_excel("잡코리아_DB적재용_리스트.xlsx", index=False)
    print(f"성공적으로 {len(df)}건의 데이터를 정제하여 '잡코리아_DB적재용_리스트.xlsx' 파일로 저장했습니다.")

    # 4) DB에 저장 (mariadb 미설치로 주석 처리)
    # save_to_mariadb(result)


if __name__ == "__main__":
    main()
