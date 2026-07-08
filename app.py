import streamlit as st
from fpdf import FPDF
import datetime

# --- PDF 생성 함수 ---
def generate_pdf(data):
    # FPDF 객체 생성 (A4, 세로)
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    
    # 폰트 등록 (NanumGothicEco.ttf 파일이 같은 폴더에 있어야 합니다)
    try:
        pdf.add_font("Nanum", "", "NanumGothicEco.ttf", uni=True)
        pdf.set_font("Nanum", "", 12)
    except Exception as e:
        st.error("폰트 파일을 찾을 수 없습니다. 'NanumGothicEco.ttf'가 같은 폴더에 있는지 확인해주세요.")
        return None

    # 제목 추가
    pdf.set_font("Nanum", "", 18)
    pdf.cell(0, 15, "회의비 집행 품의서", ln=True, align="C")
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    # 본문 텍스트 설정
    pdf.set_font("Nanum", "", 11)
    line_height = 8
    
    # 1. 내용
    pdf.cell(40, line_height, "1. 내    용:", border=0)
    pdf.multi_cell(0, line_height, data['content'])
    
    # 2. 일시
    pdf.cell(40, line_height, "2. 일    시:", border=0)
    pdf.cell(0, line_height, data['datetime_str'], ln=True)
    
    # 3. 장소
    pdf.cell(40, line_height, "3. 장    소:", border=0)
    pdf.cell(0, line_height, data['location'], ln=True)
    
    # 4. 참여자
    pdf.cell(40, line_height, "4. 참 여 자:", border=0)
    pdf.multi_cell(0, line_height, data['participants'])
    
    # 5. 소요예산
    pdf.cell(40, line_height, "5. 소요예산:", border=0)
    budget_text = f"{data['total_budget']:,} 원 ({data['people_count']}인 x {data['cost_per_person']:,} 원/인)"
    pdf.cell(0, line_height, budget_text, ln=True)
    
    pdf.ln(5)
    
    # 6. 예산 정보
    pdf.set_font("Nanum", "", 12)
    pdf.cell(0, line_height, "[예산 정보]", ln=True)
    pdf.set_font("Nanum", "", 11)
    pdf.cell(40, line_height, "- 예산 과목:", border=0)
    pdf.cell(0, line_height, data['budget_subject'], ln=True)
    pdf.cell(40, line_height, "- 금회 집행액:", border=0)
    pdf.cell(0, line_height, f"{data['execution_amount']:,} 원", ln=True)
    pdf.cell(40, line_height, "- 예산 잔액:", border=0)
    pdf.cell(0, line_height, f"{data['balance_amount']:,} 원", ln=True)
    
    pdf.ln(5)
    
    # 7. 채주명세
    pdf.set_font("Nanum", "", 12)
    pdf.cell(0, line_height, "[채주명세]", ln=True)
    pdf.set_font("Nanum", "", 11)
    pdf.cell(40, line_height, "- 채 주 명:", border=0)
    pdf.cell(0, line_height, data['payee_name'], ln=True)
    pdf.cell(40, line_height, "- 총 금 액:", border=0)
    pdf.cell(0, line_height, f"{data['payee_total']:,} 원", ln=True)
    pdf.cell(40, line_height, "- 공 급 가 액:", border=0)
    pdf.cell(0, line_height, f"{data['supply_value']:,} 원", ln=True)
    pdf.cell(40, line_height, "- 부  가  세:", border=0)
    pdf.cell(0, line_height, f"{data['vat']:,} 원", ln=True)
    
    # 바이트 데이터로 변환하여 반환
    # 바이트 데이터로 변환하여 반환
    return bytes(pdf.output())


# --- Streamlit UI 구성 ---
st.set_page_config(page_title="회의비 품의서 생성기", layout="centered")

st.title("📄 회의비 품의서 자동 생성기")
st.write("아래 항목을 입력하고 PDF를 생성해 보세요.")

with st.form("expense_form"):
    st.subheader("기본 정보")
    # 1. 내용
    content = st.text_input("1. 내용", placeholder="예: 몽골 중온 아스팔트 온실가스 감축 현지조사 및 경제성분석")
    
    # 2. 일시
    col1, col2, col3 = st.columns(3)
    with col1:
        date_input = st.date_input("날짜", datetime.date.today())
    with col2:
        start_time = st.time_input("시작 시간", datetime.time(14, 30))
    with col3:
        end_time = st.time_input("종료 시간", datetime.time(18, 30))
    
    # 날짜를 요일이 포함된 문자열로 포맷팅
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    weekday_str = weekdays[date_input.weekday()]
    datetime_str = f"{date_input.strftime('%Y.%m.%d')} ({weekday_str}) {start_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')}"
    
    # 3. 장소
    location = st.text_input("3. 장소", placeholder="예: 서초 르호봇")
    
    # 4. 참여자
    participants = st.text_area("4. 참여자", placeholder="예: 임희섭 연구소장, 김낙현 대표 등 총 8명")
    
    st.divider()
    st.subheader("비용 및 예산 정보")
    
    # 5. 소요예산
    st.markdown("**5. 소요예산**")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        people_count = st.number_input("참여 인원 (명)", min_value=1, value=8)
    with p_col2:
        cost_per_person = st.number_input("1인당 단가 (원)", min_value=0, value=50000, step=1000)
    
    total_budget = int(people_count * cost_per_person)
    st.info(f"**총 예산 산출:** {people_count}인 × {cost_per_person:,}원 = **{total_budget:,} 원**")
    
    # 6. 예산 정보
    st.markdown("**6. 예산 정보**")
    budget_subject = st.text_input("예산 과목", placeholder="예: 연구개발비 - 회의비")
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        execution_amount = st.number_input("금회 집행액 (원)", min_value=0, value=total_budget, step=1000)
    with b_col2:
        balance_amount = st.number_input("예산 잔액 (원)", min_value=0, value=0, step=10000)
        
    st.divider()
    st.subheader("채주명세 (영수증 정보)")
    
    # 7. 채주명세
    payee_name = st.text_input("채주명 (상호명)", placeholder="예: (주)식당이름")
    payee_total = st.number_input("결제 총 금액 (원)", min_value=0, value=total_budget, step=1000)
    
    # 공급가액과 부가세 자동 계산 (부가세 10% 가정), 수정 가능하도록 설정
    default_supply = int(round(payee_total / 1.1))
    default_vat = payee_total - default_supply
    
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        supply_value = st.number_input("공급가액 (원)", min_value=0, value=default_supply, step=1000)
    with v_col2:
        vat = st.number_input("부가세 (원)", min_value=0, value=default_vat, step=100)

    # 폼 제출 버튼
    submitted = st.form_submit_button("PDF 생성하기")

# --- 제출 시 PDF 생성 처리 ---
if submitted:
    # 딕셔너리로 데이터 묶기
    data = {
        "content": content,
        "datetime_str": datetime_str,
        "location": location,
        "participants": participants,
        "people_count": people_count,
        "cost_per_person": cost_per_person,
        "total_budget": total_budget,
        "budget_subject": budget_subject,
        "execution_amount": execution_amount,
        "balance_amount": balance_amount,
        "payee_name": payee_name,
        "payee_total": payee_total,
        "supply_value": supply_value,
        "vat": vat
    }
    
    with st.spinner("PDF를 생성하는 중입니다..."):
        pdf_bytes = generate_pdf(data)
        
    if pdf_bytes:
        st.success("PDF가 성공적으로 생성되었습니다! 아래 버튼을 눌러 다운로드하세요.")
        st.download_button(
            label="📄 완성된 PDF 다운로드",
            data=pdf_bytes,
            file_name=f"회의비_품의서_{datetime.date.today().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
