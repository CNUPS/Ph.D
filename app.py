import streamlit as st
from fpdf import FPDF
import datetime

# --- PDF 레이아웃 및 생성 클래스 ---
class CorporatePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        # 여백 설정 (좌, 상, 우)
        self.set_margins(15, 15, 15)
        self.auto_page_break = True
        self.b_margin = 15

    def draw_form(self, data):
        self.add_page()
        
        # 한글 폰트 등록
        try:
            self.add_font("Nanum", "", "NanumGothicEco.ttf", uni=True)
            self.set_font("Nanum", "", 10)
        except Exception as e:
            st.error("NanumGothicEco.ttf 폰트 파일을 로드할 수 없습니다.")
            return

        # 1. 상단 헤더 영역 (로고 및 문서 타이틀 느낌)
        try:
            # 로고 이미지 좌측 상단 배치 (w=45)
            self.image("logo.png", x=15, y=12, w=45)
        except:
            pass
            
        self.ln(12)
        
        # 수신자 정보
        self.set_font("Nanum", "", 11)
        self.cell(20, 8, "수신자", border=1, align="C")
        self.cell(40, 8, f" {data['receiver']}", border=1, align="L")
        self.cell(0, 8, "", ln=True) # 우측 빈공간 (결재란 공간 확보용)
        
        self.cell(20, 8, "(경  유)", border=1, align="C")
        self.cell(40, 8, "", border=1)
        self.cell(0, 8, "", ln=True)
        
        self.ln(3)
        
        # 제목 영역
        self.set_font("Nanum", "", 12)
        self.cell(20, 10, "제    목", border=1, align="C")
        self.set_font("Nanum", "", 12)
        self.cell(0, 10, f" {data['title']}", border=1, ln=True, align="L")
        
        self.ln(4)
        
        # 2. 메인 정보 테이블 (회계단위, 프로젝트, 발의일, 품의번호)
        self.set_font("Nanum", "", 10)
        
        info_data = [
            ["회계단위", str(data['accounting_unit']), "프로젝트", str(data['project_name'])],
            ["발의일", str(data['initiation_date']), "품의번호", str(data['report_number'])]
        ]
        
        # 에러를 유발했던 색상 옵션을 제거하고 가장 안정적인 형태로 표 생성
        with self.table(borders_layout="ALL", line_height=7) as table:
            for row in info_data:
                row_cells = table.row()
                row_cells.cell(row[0], align="C")
                row_cells.cell(row[1], align="L")
                row_cells.cell(row[2], align="C")
                row_cells.cell(row[3], align="L")
                
        self.ln(4)
        
        # 적요 서술 칸
        self.set_font("Nanum", "", 10)
        self.cell(20, 8, "적요", border=1, align="C")
        self.multi_cell(0, 8, f" {data['summary_desc']}", border=1, align="L")
        
        self.ln(6)
        
        # 중간 구분선 대신 내역 시작 안내
        self.set_font("Nanum", "", 11)
        self.cell(0, 8, "- 다    음 -", ln=True, align="L")
        self.ln(2)
        
        # 3. 세부 항목 출력 (1~5번)
        line_h = 7.5
        self.set_font("Nanum", "", 10.5)
        
        # 1. 내용
        self.cell(25, line_h, "1. 내    용 : ", ln=0)
        self.multi_cell(0, line_h, data['content_detail'])
        
        # 2. 일시
        self.cell(25, line_h, "2. 일    시 : ", ln=0)
        self.cell(0, line_h, data['datetime_str'], ln=True)
        
        # 3. 장소
        self.cell(25, line_h, "3. 장    소 : ", ln=0)
        self.cell(0, line_h, data['location'], ln=True)
        
        # 4. 참여자
        self.cell(25, line_h, "4. 참 여 자 : ", ln=0)
        self.multi_cell(0, line_h, data['participants'])
        
        # 5. 소요예산
        self.cell(25, line_h, "5. 소요예산 : ", ln=0)
        self.set_font("Nanum", "", 11)
        self.cell(0, line_h, f"{data['total_budget']:,} 원", ln=True)
        
        # 소요예산 상세 내역 (회의경비 항목)
        self.set_font("Nanum", "", 10)
        detail_budget_str = f"  - {data['expense_type']}: {data['people_count']}인 x {data['cost_per_person']:,}원/인 = {data['total_budget']:,}원"
        self.cell(0, line_h, detail_budget_str, ln=True)
        
        self.ln(6)
        
        # 4. 채주명세 타이틀 및 테이블 구조화
        self.set_font("Nanum", "", 11)
        self.cell(0, 8, "[채주명세]", ln=True)
        self.ln(2)
        
        # 채주명세 테이블 헤더 및 데이터 생성
        account_headers = ["채주명", "금액", "공급가액", "부가세", "금융기관", "계좌번호"]
        account_rows = [
            [
                str(data['payee_name']), 
                f"{data['payee_total']:,}", 
                f"{data['supply_value']:,}", 
                f"{data['vat']:,}", 
                str(data['bank_name']), 
                str(data['account_number'])
            ]
        ]
        
        self.set_font("Nanum", "", 9.5)
        with self.table(borders_layout="ALL", line_height=8) as table:
            # 헤더 그리기
            header_row = table.row()
            for header in account_headers:
                header_row.cell(header, align="C")
            # 데이터 행 그리기
            for row in account_rows:
                data_row = table.row()
                for item in row:
                    data_row.cell(item, align="C")


# --- Streamlit 웹 UI 구성 ---
st.set_page_config(page_title="한국도로협회 회의비 품의서 시스템", layout="centered")

st.title("🏛️ 회의비 집행 품의서 시스템")
st.write("원하는 문서 양식 데이터를 입력하면 오차 없이 양식 규격 PDF를 빌드합니다.")

with st.form("corporate_expense_form"):
    st.subheader("📋 1. 공문서 결재 기본 정보")
    
    col_header1, col_header2 = st.columns(2)
    with col_header1:
        receiver = st.selectbox("수신자 구분", ["내부결재", "기타전결", "직접입력"])
        if receiver == "직접입력":
            receiver = st.text_input("수신자 직접 입력", value="내부결재")
    with col_header2:
        accounting_unit = st.text_input("회계단위", value="사단법인 한국도로협회")
        
    title = st.text_input("문서 제목 (제 목)", value="몽골 중온 개질 아스팔트 온실가스 감축 타당성 조사 회의비(260226)")
    project_name = st.text_input("프로젝트 명", value="몽골 중온 개질 아스팔트 온실가스 감축 타당성 조사")
    
    col_header3, col_header4 = st.columns(2)
    with col_header3:
        initiation_date = st.date_input("발의 일", datetime.date.today())
        initiation_date_str = initiation_date.strftime("%Y-%m-%d")
    with col_header4:
        report_number = st.text_input("품의번호", value="4")
        
    summary_desc = st.text_area(
        "적요 (상세 설명 문구)", 
        value="윤성산업개발이 발주한 몽골 중온 개질 아스팔트 온실가스 감축 타당성 조사 용역과 관련하여 다음과 같이 연구회의를 개최하고자 합니다."
    )
    
    st.divider()
    st.subheader("📅 2. 연구 회의 세부 내역 (다음)")
    
    content_detail = st.text_input("1. 내용 항목", value="몽골 중온 아스팔트 온실가스 감축 현지조사 및 경제성분석")
    
    # 일시 입력 구조화
    col_dt1, col_dt2, col_dt3 = st.columns(3)
    with col_dt1:
        date_input = st.date_input("회의 날짜", datetime.date.today())
    with col_dt2:
        start_time = st.time_input("시작 시간", datetime.time(14, 30))
    with col_dt3:
        end_time = st.time_input("종료 시간", datetime.time(18, 30))
        
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_str = weekdays[date_input.weekday()]
    datetime_str = f"{date_input.strftime('%Y.%m.%d')} ({weekday_str}) {start_time.strftime('%H:%M')}~{end_time.strftime('%H:%M')}"
    
    location = st.text_input("3. 장소 항목", value="서초르호봇")
    participants = st.text_area(
        "4. 참여자 항목", 
        value="윤성산업개발 임희섭 연구소장, 그리너스 김낙현 대표, 한국도로협회 최지선 실장 등 8명"
    )
    
    st.markdown("**5. 소요예산 산출 자동화**")
    expense_type = st.text_input("비용 비목 구분", value="회의경비(식대 및 다과)")
    
    col_calc1, col_calc2 = st.columns(2)
    with col_calc1:
        people_count = st.number_input("참여 인원수 (명)", min_value=1, value=8)
    with col_calc2:
        cost_per_person = st.number_input("1인당 배정 금액 (원)", min_value=0, value=50000, step=1000)
        
    total_budget = int(people_count * cost_per_person)
    st.info(f"💡 계산된 총 예산: **{total_budget:,} 원**")
    
    st.divider()
    st.subheader("💳 3. 채주명세 입금 격자 표 데이터")
    
    payee_name = st.text_input("채주명 (입금주/상호)", value="윤성산업개발(주)")
    payee_total = st.number_input("결제 총 금액 (원)", min_value=0, value=total_budget)
    
    # 부가세 및 공급가액 자동 역산 로직
    default_supply = int(round(payee_total / 1.1))
    default_vat = payee_total - default_supply
    
    col_tax1, col_tax2 = st.columns(2)
    with col_tax1:
        supply_value = st.number_input("공급가액 (원)", min_value=0, value=default_supply)
    with col_tax2:
        vat = st.number_input("부가세 (원)", min_value=0, value=default_vat)
        
    col_bank1, col_bank2 = st.columns(2)
    with col_bank1:
        bank_name = st.text_input("금융기관 (은행명)", value="우리은행")
    with col_bank2:
        account_number = st.text_input("계좌번호", value="1002-123-456789")
        
    st.divider()
    user_file_name = st.text_input("💾 파일 다운로드 지정 이름 (.pdf 자동 할당)", value=f"회의비_결재문서_{datetime.date.today().strftime('%Y%m%d')}")
    
    # 제출 서명
    submitted = st.form_submit_button("원형 규격 반영 PDF 빌드하기")

if submitted:
    # 묶음 딕셔너리 데이터 전달
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
    
    with st.spinner("문서 인코딩 및 레이아웃을 빌드 중입니다..."):
        try:
            pdf = CorporatePDF()
            pdf.draw_form(payload)
            pdf_bytes = bytes(pdf.output())
            
            st.success("🎉 이상 없이 PDF 빌드가 완료되었습니다!")
            st.download_button(
                label="💾 완성된 원본 규격 PDF 다운로드",
                data=pdf_bytes,
                file_name=f"{user_file_name}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF 생성 중 오류가 발생했습니다: {e}")
