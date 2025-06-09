from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import time

with sync_playwright() as p:
    # headless true로 되어있으면 봇으로 감지 될 수 있음
    # ✅ Edge 브라우저 사용
    browser = p.chromium.launch(channel="msedge", headless=False)
    context = browser.new_context()

    page = context.new_page()

    page_num = 1
    product_list = []

    while True:
        # 추후 페이징 변수 처리 필요
        url = f"https://www.coupang.com/np/search?q=%ED%82%A4%ED%81%AC%EB%A1%A0&channel=user&listSize=72&page={page_num}"

        print(f"\n[Page {page_num}] 페이지 이동중...")
        if page_num == 1:
            page.goto(url)
            time.sleep(2)

        # 페이지 이동 후 약간 대기 (쿠팡 HTTP/2 에러 방지)
        time.sleep(2)

        # li 태그 중 한정 시간 특가 상품은, 같이 보면 좋은 상품, 핫딜 로켓직구 글로벌특가, 함께 본 상품, 오늘의 판매자 특가는 제외 처리 해야함
        page.wait_for_selector('ul#product-list li', timeout=20000)

        items = page.locator('ul#product-list li')

        # 추후 페이지 별로 for 문 추가 필요. 페이지 개수 x li 태그 개수
        for i in range(items.count()):
            item = items.nth(i)

            try:
                name = item.locator('div[class^="ProductUnit_productName__"]').inner_text().strip()
            except:
                name = "N/A"

            # 크롤링 방지 때문에 html 태그 strong, del 동적으로 생성하고 class명 뒤에 난수 값 있음
            try:
                price = item.locator('strong[class^="Price_priceValue__"]').inner_text().strip()
            except:
                try:
                    price = item.locator('del[class^="Price_priceValue__"]').inner_text().strip()
                except:
                    price = "N/A"

            product_list.append({"상품명": name, "가격": price})

        try:
            next_btn_a = page.locator('a[class^="Pagination_nextBtn__"]')
            if next_btn_a.count() > 0:
                print("➡️ 다음 페이지 존재 → 클릭으로 이동")

                # ✅ 클릭 후 약간 대기
                next_btn_a.first.click()
                time.sleep(2)

                page_num += 1
            else:
                print("✅ 마지막 페이지 (Pagination_nextBtn__ → span 태그)")
                break
        except:
            print("✅ 마지막 페이지 (Pagination_nextBtn__ → span 태그)")
            break

    print("\n상품명 : 가격 리스트")

    product_cnt = 0
    for p in product_list:
        product_cnt += 1
        print(product_cnt, p)

    # DataFrame 생성 (columns 생략 → 자동으로 딕셔너리 키 사용)
    df = pd.DataFrame(product_list)

    # 그냥 확인용 출력
    print(df.head())

    # 현재 시간 문자열 생성
    timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")

    # 엑셀 파일명
    excel_filename = f"coupang_products{timestamp}.xlsx"

    # 엑셀 저장
    df.to_excel(excel_filename, index=False, engine='openpyxl')

    print(f"\n엑셀로 저장 완료: {excel_filename}")

    browser.close()
