import streamlit as st
from fpdf import FPDF
import datetime

# --- PDF 레이아웃 및 생성 클래스 ---
class CorporatePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        # 여백 설정 (좌 15, 상 15, 우 15) -> 가용 너비 = 210 - 30 = 180mm
        self.set_margins(15, 15, 15)
        self.auto_page_break = True
        self.b_margin = 15

    def draw_form(self, data):
        self.add_page()
        
        # 폰트 등록 (유저가 업로드한 정규/Bold 폰트 완벽 연동)
        try:
            self.add_font("Nanum", "", "NanumBarunGothic.ttf", uni=True)
            self.add_font("Nanum", "B", "NanumBarunGothicBold.ttf", uni=True)
            self.set_font("Nanum", "", 10)
        except Exception as e:
            st.error("NanumBarunGothic.ttf 또는 Bold 폰트 파일을 로드할 수 없습니다. 서버 저장소 위치를 확인해주세요.")
            return

        # --- 1. 상단 기관 로고 및 내부결재선 영역 ---
        # 로고 배치 (좌측 상단 y=15, w=50)
        try:
            self.image("logo.png", x=15, y=15, w=50)
        except:
            pass
        
        # 결재선 그리기 (우측 상단 정렬)
        # 테이블 에러를 피하기 위해 절대 좌표 기반 패딩 셀 방식으로 처리
        self.set_font("Nanum", "B", 9)
        self.set_xy(145, 15)
        self.cell(15, 6, "수신자", border=1, align="C")
        self.cell(35, 6, data["receiver"], border=1, align="C")
        
        self.set_xy(145, 21)
        self.cell(15, 12, "(경유)", border=1, align="C")
        self.cell(35, 12, "내부결재", border=1, align="C")
        
        self.ln(10) # 결재선 하단 여백 추가
        
        # --- 2. 문서 제목 (공식 몽골 PDF 스타일 라인 포인트) ---
        self.set_y(40)
        self.set_font("Nanum", "B", 15)
        # 제목 글자 크기에 맞춰 자동 줄바꿈 지원하면서 에러 방지
        self.multi_cell(180, 8, data["title"], border=0, align="L")
        self.ln(3)
        
        # 상단 굵은 수평선
        self.set_line_width(0.6)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(4)
        
        # --- 3. 메타 정보 테이블 (회계단위, 프로젝트, 발의일, 품의번호) ---
        self.set_font("Nanum", "", 10)
        self.set_line_width(0.2)
        
        # 1행: 회계단위 / 프로젝트
        # 명확한 너비 지정으로 'Not enough space' 에러 근본적 차단 (총합 180mm)
        self.set_fill_color(245, 245, 245)
        self.cell(25, 8, "회계단위", border=1, align="C", fill=True)
        self.cell(50, 8, data["accounting_unit"], border=1, align="L")
        self.cell(25, 8, "프로젝트", border=1, align="C", fill=True)
        
        # 프로젝트명 길어질 때 셀 깨짐 방지용 multi_cell 유동적 처리 예방을 위한 가용 너비 배정
        current_x = self.get_x()
        current_y = self.get_y()
        self.multi_cell(80, 8, data["project_name"], border=1, align="L")
        self.set_xy(current_x + 80, current_y)
        self.ln(8)
        
        # 2행: 발의일 / 품의번호
        self.cell(25, 8, "발의 일", border=1, align="C", fill=True)
        self.cell(50, 8, data["initiation_date"], border=1, align="L")
        self.cell(25, 8, "품의번호", border=1, align="C", fill=True)
        self.cell(80, 8, str(data["report_number"]), border=1, align="L")
        self.ln(12)
        
        # --- 4. 적요 요약문 영역 ---
        self.set_font("Nanum", "B", 11)
        self.cell(180, 6, "적요", ln=True)
        self.set_font("Nanum", "", 10)
        self.ln(2)
        self.multi_cell(180, 6, data["summary_desc"], border=0, align="L")
        
        # 구분선
        self.ln(4)
        self.set_font("Nanum", "B", 11)
        self.cell(180, 6, "- 다음 -", ln=True)
        self.ln(2)
        
        # --- 5. 다음 세부 항목 리스트 (1~5번 규격화) ---
        self.set_font("Nanum", "", 10)
        line_h = 6
        
        # 1. 내용
        self.set_font("Nanum", "B", 10)
        self.cell(20, line_h, "1. 내용 : ", border=0)
        self.set_font("Nanum", "", 10)
        self.multi_cell(160, line_h, data["content_detail"])
        
        # 2. 일시
        self.set_font("Nanum", "B", 10)
        self.cell(20, line_h, "2. 일시 : ", border=0)
        self.set_font("Nanum", "", 10)
        self.cell(160, line_h, data["datetime_str"], ln=True)
        
        # 3. 장소
        self.set_font("Nanum", "B", 10)
        self.cell(20, line_h, "3. 장소 : ", border=0)
        self.set_font("Nanum", "", 10)
        self.cell(160, line_h, data["location"], ln=True)
        
        # 4. 참여자
        self.set_font("Nanum", "B", 10)
        self.cell(20, line_h, "4. 참여자 : ", border=0)
        self.set_font("Nanum", "", 10)
        self.multi_cell(160, line_h, data["participants"])
        
        # 5. 소요예산 및 산출내역
        self.set_font("Nanum", "B", 10)
        self.cell(20, line_h, "5. 예산 : ", border=0)
        self.set_font("Nanum", "", 10)
        
        # 금액 포맷팅 추가 (ex: 400,000 원)
        formatted_total = f"{data['total_budget']:,} 원"
        self.cell(160, line_h, formatted_total, ln=True)
        
        # 하단 디테일 산출 내역 서술형 추가
        self.set_font("Nanum", "", 9.5)
        calc_text = f"  - {data['expense_type']}: {data['people_count']}인 x {data['cost_per_person']:,}원/인 = {data['total_budget']:,}원"
        self.cell(180, line_h, calc_text, ln=True)
        self.ln(8)
        
        # --- 6. 채주명세서 테이블 (에러 빈발 구간 완벽 패딩화) ---
        self.set_font("Nanum", "B", 11)
        self.cell(180, 6, "[채주명세]", ln=True)
        self.ln(2)
        
        self.set_font("Nanum", "", 9)
        # 테이블 컬럼 너비 분배 공식 수치 적용 (총합 180mm 정확히 일치)
        col_widths = {
            "payee": 35,
            "total": 25,
            "supply": 25,
            "vat": 20,
            "bank": 25,
            "account": 50
        }
        
        # 채주명세 헤더
        self.set_fill_color(240, 240, 240)
        self.cell(col_widths["payee"], 8, "채주명", border=1, align="C", fill=True)
        self.cell(col_widths["total"], 8, "금액", border=1, align="C", fill=True)
        self.cell(col_widths["supply"], 8, "공급가액", border=1, align="C", fill=True)
        self.cell(col_widths["vat"], 8, "부가세", border=1, align="C", fill=True)
        self.cell(col_widths["bank"], 8, "금융기관", border=1, align="C", fill=True)
        self.cell(col_widths["account"], 8, "계좌번호", border=1, align="C", fill=True)
        self.ln()
        
        # 채주명세 데이터 행
        self.cell(col_widths["payee"], 8, data["payee_name"], border=1, align="C")
        self.cell(col_widths["total"], 8, f"{data['payee_total']:,}", border=1, align="R")
        self.cell(col_widths["supply"], 8, f"{data['supply_value']:,}", border=1, align="R")
        self.cell(col_widths["vat"], 8, f"{data['vat']:,}", border=1, align="R")
        self.cell(col_widths["bank"], 8, data["bank_name"], border=1, align="C")
        self.cell(col_widths["account"], 8, data["account_number"], border=1, align="L")
        self.ln(15)
        
        # 하단 종료 마감 처리
        self.set_line_width(0.4)
        self.line(15, self.get_y(), 195, self.get_y())


# --- Streamlit 인터페이스 대시보드 ---
st.set_page_config(page_title="한국도로협회 양식 결재문서 빌더", layout="centered")
st.title("📋 한국도로협회 품의서 빌더 (찐최종 에러 프리 버전)")
st.caption("몽골 중온 개질 아스팔트 온실가스 감축 타당성 조사 양식 원형 매칭 모델")

with st.form("corporate_form"):
    st.subheader("1. 문서 정보 및 결재선 설정")
    c1, c2 = st.columns(2)
    with c1:
        receiver = st.text_input("수신자 입력", value="내부결재")
        accounting_unit = st.text_input("회계단위", value="사단법인 한국도로협회")
    with c2:
        report_number = st.number_input("품의번호", min_value=1, value=4, step=1)
        initiation_date_str = st.date_input("발의 일자 선택", datetime.date(2026, 2, 26)).strftime("%Y-%m-%d")

    title = st.text_input("문서 제목", value="20260226-스마트인프라연구실-이도근 몽골 중온 개질 아스팔트 온실가스 감축 타당성 조사 회의비(260226)")
    project_name = st.text_input("프로젝트명", value="몽골 중온 개질 아스팔트 온실가스 감축 타당성 조사")
    
    st.markdown("---")
    st.subheader("2. 적요 및 세부 내용")
    summary_desc = st.text_area("적요 기재란", value="윤성산업개발이 발주한 몽골 중온 개질 아스팔트 온실가스 감축 타당성 조사 용역과 관련하여 다음과 같이 연구회의를 개최하고자 합니다.")
    
    content_detail = st.text_input("1. 내용 항목 세부", value="몽골 중온 아스팔트 온실가스 감축 현지조사 및 경제성분석")
    datetime_str = st.text_input("2. 일시 항목 세부", value="2026.02.26 (목) 14:30~18:30")
    location = st.text_input("3. 장소 항목 세부", value="서초르호봇")
    participants = st.text_area("4. 참여자 항목 세부", value="윤성산업개발 임희섭 연구소장, 그리너스 김낙현 대표, 한국도로협회 최지선 실장 등 8명")
    
    st.markdown("---")
    st.subheader("3. 산출금액 및 채주명세 설정")
    expense_type = st.text_input("비용 비목 구분", value="회의경비(식대 및 다과)")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        people_count = st.number_input("인원수 (명)", min_value=1, value=8)
    with col_p2:
        cost_per_person = st.number_input("1인당 단가 (원)", min_value=0, value=50000, step=1000)
    with col_p3:
        total_budget = people_count * cost_per_person
        st.metric(label="자동 계산 총 예산", value=f"{total_budget:,} 원")

    st.markdown("**[채주 지급 계좌 명세정보]**")
    cc1, cc2 = st.columns(2)
    with cc1:
        payee_name = st.text_input("채주명", value="윤성산업개발(주)")
        bank_name = st.text_input("지급 은행", value="우리은행")
    with cc2:
        payee_total = st.number_input("지급 총액 (원)", min_value=0, value=total_budget)
        account_number = st.text_input("계좌번호", value="1005-xxx-xxxxxx")
    
    # 공급가액과 부가세 공식 규격 1.1 분할 계산 자동화
    calc_supply = int(round(payee_total / 1.1))
    calc_vat = payee_total - calc_supply
    
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        supply_value = st.number_input("공급가액 (원)", min_value=0, value=calc_supply)
    with v_col2:
        vat = st.number_input("부가세 (원)", min_value=0, value=calc_vat)

    user_file_name = st.text_input("💾 저장 파일명 지정 (.pdf 자동 부여)", value="20260226-스마트인프라연구실-이도근_몽골_회의비")
    
    submitted = st.form_submit_button("원형 규격 반영 PDF 빌드하기")

if submitted:
    payload = {
        "receiver": receiver,
        "title": title,
        "accounting_unit": accounting_unit,
        "project_name": project_name,
        "initiation_date": initiation_date_str,
        "report_number": report_number,
        "summary_desc": summary_desc,
        "content_detail": content_detail,
        "datetime_str": datetime_str,
        "location": location,
        "participants": participants,
        "expense_type": expense_type,
        "people_count": people_count,
        "cost_per_person": cost_per_person,
        "total_budget": total_budget,
        "payee_name": payee_name,
        "payee_total": payee_total,
        "supply_value": supply_value,
        "vat": vat,
        "bank_name": bank_name,
        "account_number": account_number
    }
    
    with st.spinner("문서 인코딩 및 몽골 타당성 조사 레이아웃 최적화 매핑 중..."):
        try:
            pdf = CorporatePDF()
            pdf.draw_form(payload)
            pdf_bytes = bytes(pdf.output())
            
            st.success("🎉 에러 없이 깔끔하게 PDF 빌드가 완료되었습니다!")
            st.download_button(
                label="📥 찐최종 결재 품의서 PDF 다운로드",
                data=pdf_bytes,
                file_name=f"{user_file_name}.pdf",
                mime="application/pdf"
            )
        except Exception as ex:
            st.error(f"컴파일 중 예외가 발생했습니다: {ex}")
