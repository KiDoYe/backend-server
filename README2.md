# 잡코리아 채용공고 크롤러

잡코리아(jobkorea.co.kr)에서 키워드로 채용공고를 검색해 수집하고, 엑셀 파일로 저장하는 파이썬 스크립트입니다. 브라우저(Playwright/Chromium) 없이 `requests` + `BeautifulSoup`만으로 동작해서 라즈베리파이 2B 같은 저사양 환경에서도 가볍게 실행할 수 있습니다.

## 파일 구성

| 파일 | 설명 |
|---|---|
| `crawl.py` | 크롤링 실행 스크립트 |
| `requirements.txt` | 필요한 파이썬 패키지 목록 |
| `run.sh` | 가상환경 설치부터 실행까지 한 번에 처리하는 셸 스크립트 |

## 요구 사항

Python 3.9 이상. 브라우저 설치가 필요 없습니다 (requests 기반).

## 사용 방법 (라즈베리파이 / 리눅스 서버)

가장 간단한 방법은 `run.sh` 하나로 끝내는 거예요.

```
chmod +x run.sh
./run.sh
```

이 스크립트가 자동으로 처리하는 것:

1. `venv` 가상환경 생성 (없을 때만)
2. 가상환경 활성화
3. `requirements.txt` 기준 패키지 설치
4. `crawl.py` 실행

이미 가상환경/패키지가 설치되어 있으면 관련 단계는 건너뛰기 때문에 반복 실행해도 안전합니다.

## 수동 실행 (직접 하나씩)

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python crawl.py
```

## 검색 조건 변경

`crawl.py` 맨 아래 `main()` 함수에서 수정합니다.

```python
keyword = "파이썬 개발자"   # 검색 키워드
start_page = 1              # 크롤링 시작 페이지
end_page = 5                 # 크롤링 종료 페이지
```

## 출력

실행이 끝나면 실행 위치에 `잡코리아_DB적재용_리스트.xlsx` 파일이 생성됩니다.

| 컬럼명 | 설명 |
|---|---|
| source | 출처 (고정값: 잡코리아) |
| platform_post_id | 공고 고유 ID |
| job_part | 검색 키워드 |
| company_name | 회사명 |
| post_title | 공고 제목 |
| region | 근무 지역 |
| personal_history | 경력 조건 |
| edu_require | 학력 조건 (목록 화면에 더 이상 표시되지 않아 현재 미수집) |
| emp_type | 고용 형태 (목록 화면에 더 이상 표시되지 않아 현재 미수집) |
| pay | 급여 |
| end_at | 마감일 |
| crawled_at | 수집 시각 |
| job_url | 공고 상세 URL |

## 주의 사항

- 결과 엑셀 파일이 이미 다른 프로그램(엑셀 등)에서 열려 있으면 `PermissionError`가 발생합니다. 실행 전 닫아주세요.
- 크롤링 결과가 0건이면 잡코리아의 페이지 구조가 바뀌었거나 요청이 차단됐을 가능성이 있습니다. 이 경우 스크립트가 자동으로 `debug_page_N.html` 파일을 저장하니, 열어서 실제 HTML 구조를 확인하고 `crawl.py`의 선택자(selector)를 다시 맞춰야 합니다.
- 현재 선택자는 2026년 리뉴얼된 잡코리아 구조(`data-sentry-component` 속성 기반)에 맞춰져 있습니다. 사이트가 다시 개편되면 선택자도 함께 업데이트해야 합니다.
- 반복 실행 시 사이트에 부담을 주지 않도록 페이지마다 1.5초 딜레이가 들어가 있습니다. 너무 자주/많이 요청하면 IP가 차단될 수 있습니다.
- MariaDB 저장 기능(`setup_database`, `save_to_mariadb`)은 코드에 남아있지만 주석 처리되어 있습니다. DB를 설치한 뒤 `DB_CONFIG` 값을 채우고, `requirements.txt`에서 `mariadb` 줄 주석을 해제하고, `crawl.py` 상단의 `import mariadb`와 관련 함수 호출부 주석을 해제하면 사용할 수 있습니다.
