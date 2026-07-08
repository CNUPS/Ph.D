import streamlit as st
from fpdf import FPDF
import datetime

# --- PDF 레이아웃 및 생성 클래스 ---
class CorporatePDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        # 여백 설정 (좌, 상, 우) - A4 너비 210mm 기준 좌우 여백 15mm씩 (사용 가능 너비 180mm)
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

        # 1. 상단 헤더 영역 (로고 중앙 배치)
        try:
            # A4 너비(210)에서 이미지 너비(70)를 빼고 반으로 나누면 정중앙 X좌표는 70
            self.image("logo.png", x=70, y=15, w=70)
            self.ln(25) # 로고 크기만큼 아래 공간 띄우기
        except:
            self.ln(15) # 로고가 없을 경우 대비한 여백
            
        # 2. 메인 결재 정보 테이블 
        self.set_font("Nanum", "", 10.5)
        
        # [핵심 수정] first_row_as_headings=False 를 추가하여 Bold 폰트 에러 방지
        # col_widths 총합 = 25 + 65 + 25 + 65 = 180 (A4 가용 너비)
        with self.table(borders_layout="ALL", text_align="CENTER", line_height=8, col_widths=(25, 65, 25, 65), first_row_as_headings=False) as table:
            # 첫 번째 줄: 수신자 & 경유
            row = table.row()
            row.cell("수신자")
            row.cell(f" {data['receiver']}", align="L")
            row.cell("(경  유)")
            row.cell("")
            
            # 두 번째 줄: 제목 (colspan을 사용하여 뒤의 3칸을 1칸으로 합침)
            row = table.row()
            row.cell("제    목")
            row.cell(f" {data['title']}", colspan=3, align="L")
            
            # 세 번째 줄: 회계단위 & 프로젝트
            row = table.row()
            row.cell("회계단위")
            row.cell(f" {data['accounting_unit']}", align="L")
            row.cell("프로젝트")
            row.cell(f" {data['project_name']}", align="L")
            
            # 네 번째 줄: 발의일 & 품의번호
            row = table.row()
            row.cell("발의일")
            row.cell(f" {data['initiation_date']}", align="L")
            row.cell("품의번호")
            row.cell(f" {data['report_number']}", align="L")
            
            # 다섯 번째 줄: 적요
            row = table.row()
            row.cell("적    요")
            row.cell(f" {data['summary_desc']}", colspan=3, align="L")
            
        self.ln(7)
        
        # 3. 세부 항목 출력
        self.set_font("Nanum", "", 11)
        self.cell(0, 8, "- 다    음 -", ln=True, align="L")
        self.ln(2)
        
        line_h = 7.5
        self.set_font("Nanum", "", 10.5)
        self.multi_cell(0, line_h, f"1. 내    용: {data['content_detail']}")
        self.multi_cell(0, line_h, f"2. 일    시: {data['datetime_str']}")
        self.multi_cell(0, line_h, f"3. 장    소: {data['location']}")
        self.multi_cell(0, line_h, f"4. 참 여 자: {data['participants']}")
        self.multi_cell(0, line_h, f"5. 소요예산: {data['total_budget']:,} 원")
        
        # 소요예산 상세 내역 들여쓰기
        self.set_font("Nanum", "", 10)
        detail_budget_str = f"  - {data['expense_type']}: {data['people_count']}인 x {data['cost_per_person']:,}원/인 = {data['total_budget']:,}원"
        self.multi_cell(0, line_h, detail_budget_str)
        
        self.ln(10)
        
        # 4. 채주명세 타이틀 및 테이블
        self.set_font("Nanum", "", 11)
        self.cell(0, 8, "[채주명세]", ln=True)
        self.ln(2)
        
        # [핵심 수정] first_row_as_headings=False 추가
        # col_widths 총합 = 40 + 25 + 25 + 25 + 25 + 40 = 180
        self.set_font("Nanum", "", 9.5)
        with self.table(borders_layout="ALL", text_align="CENTER", line_height=8, col_widths=(40, 25, 25, 25, 25, 40), first_row_as_headings=False) as table:
            # 헤더
            row = table.row()
            for header in ["채주명", "금액", "공급가액", "부가세", "금융기관", "계좌번호"]:
                row.cell(header)
                
            # 데이터
            row = table.row()
            row.cell(str(data['payee_name']))
            row.cell(f"{data['payee_total']:,}")
            row.cell(f"{data['supply_value']:,}")
            row.cell(f"{data['vat']:,}")
            row.cell(str(data['bank_name']))
            row.cell(str(data['account_number']))


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
        
    title = st.text_input("문서 제목 (제 목)", value="20260226-스마트인프라연구실-이도근 몽골 중온 개질 아스팔트 온실가스 감축 타당성 조사 회의비 (260226)")
    project_name = st.text_input("프로젝트 명", value="몽골 중온 개질 아스팔트 온실가스 감축 타당성 조사")
    
    col_header3, col_header4 = st.columns(2)
    with col_header3:
        initiation_date = st.date_input("발의 일", datetime.date(2026, 2, 26))
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
    
    col_dt1, col_dt2, col_dt3 = st.columns(3)
    with col_dt1:
        date_input = st.date_input("회의 날짜", datetime.date(2026, 2, 26))
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
    user_file_name = st.text_input("💾 파일 다운로드 지정 이름 (.pdf 자동 할당)", value="회의비_결재문서_20260226")
    
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
    
    with st.spinner("문서 인코딩 및 레이아웃을 빌드 중입니다..."):
        try:
            pdf = CorporatePDF()
            pdf.draw_form(payload)
            pdf_bytes = bytes(pdf.output())
            
            st.success("🎉 에러 없이 완벽한 규격의 PDF 빌드가 완료되었습니다! 아래 버튼을 눌러 확인해 보세요.")
            st.download_button(
                label="💾 완성된 원본 규격 PDF 다운로드",
                data=pdf_bytes,
                file_name=f"{user_file_name}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF 생성 중 오류가 발생했습니다: {e}")
