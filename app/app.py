import io
import pandas as pd
from playwright.sync_api import sync_playwright
import streamlit as st

st.title("🕷️ 웹 크롤링 자동화 데모")
st.write("원하는 키워드를 입력하고 버튼을 누르면 실시간으로 데이터를 수집하여 엑셀로 드립니다.")

# 사용자 입력 받기
search_keyword = st.text_input("검색어 또는 타겟 정보 입력", "베스트셀러")

if st.button("데이터 수집 시작"):
  with st.spinner("데이터를 열심히 긁어오는 중입니다... 잠시만 기다려주세요!"):
    try:
      # 크롤링 로직 실행 (예시)
      with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.kyobobook.co.kr/bestseller/online/daily")
        page.wait_for_load_state("networkidle")

        items = []
        products = page.locator(".prod_item").all()

        for prod in products[:20]:  # 테스트로 20개만
          title = prod.locator(".prod_name").inner_text()
          price = (
              prod.locator(".price").inner_text()
              if prod.locator(".price").count() > 0
              else "가격 정보 없음"
          )
          items.append({"상품명": title, "가격": price})

        browser.close()

      # 데이터프레임 변환
      df = pd.DataFrame(items)

      st.success(f"수집 완료! 총 {len(df)}개의 데이터를 가져왔습니다.")
      st.dataframe(df)

      # 엑셀 파일 다운로드 버튼 생성
      output = io.BytesIO()
      with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
      excel_data = output.getvalue()

      st.download_button(
          label="📥 엑셀 파일 다운로드",
          data=excel_data,
          file_name="crawled_data.xlsx",
          mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      )

    except Exception as e:
      st.error(f"오류가 발생했습니다: {e}")