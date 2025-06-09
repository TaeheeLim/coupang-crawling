from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime

with sync_playwright() as p:
    # headless true로 되어있으면 봇으로 감지 될 수 있음
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()

    # url = "https://www.coupang.com/np/search?rocketAll=false&searchId=980e547e2549180&q=%ED%82%A4%ED%81%AC%EB%A1%A0&brand=&offerCondition=&filter=&availableDeliveryFilter=&filterType=&isPriceRange=false&priceRange=&minPrice=&maxPrice=&page=1&trcid=&traid=&filterSetByUser=true&channel=user&backgroundColor=&searchProductCount=9270&component=&rating=0&sorter=scoreDesc&listSize=72"

    # 추후 페이징 변수 처리 필요
    url = "https://www.coupang.com/np/search?component=&q=%ED%82%A4%ED%81%AC%EB%A1%A0&channel=user&listSize=72"

    print("페이지 이동중...")
    page.goto(url)

    page.wait_for_selector('ul#product-list li', timeout=20000)

    # li 태그 중 한정 시간 특가 상품은, 같이 보면 좋은 상품, 핫딜 로켓직구 글로벌특가, 함께 본 상품, 오늘의 판매자 특가는 제외 처리 해야함
    items = page.locator('ul#product-list li')

    product_list = []

    # 추후 페이지 별로 for 문 추가 필요. 페이지 개수 x li 태그 개수
    for i in range(items.count()):
        item = items.nth(i)

        try:
            name = item.locator('div[class^="ProductUnit_productName__"]').inner_text().strip()
        except:
            name = "N/A"

        # 크롤링 방지 때문에 html 태그 storng, del 동적으로 생성하고 class명 뒤에 난수 값 있음
        try:
            price = item.locator('strong[class^="Price_priceValue__"]').inner_text().strip()
        except:
            try:
                price = item.locator('del[class^="Price_priceValue__"]').inner_text().strip()
            except:
                price = "N/A"

        product_list.append({"상품명": name, "가격": price})

    print("상품명 : 가격 리스트")

    num = 0
    for p in product_list:
        num += 1
        print(num, p)

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