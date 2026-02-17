import streamlit as st
import anthropic
import os
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="AI 콘텐츠 생성기",
    page_icon="✍️",
    layout="wide"
)

# CSS 스타일 (개선됨!)
st.markdown("""
<style>
    /* placeholder 글씨 밝게 */
    ::placeholder {
        color: #adb5bd !important;
        opacity: 1 !important;
    }
    
    /* 다크모드 placeholder */
    [data-theme="dark"] ::placeholder {
        color: #ced4da !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .output-box {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        border: 1px solid #e9ecef;
    }
    .style-tag {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    
    /* 라디오 버튼 왼쪽 정렬 */
    .stRadio > div {
        display: flex;
        flex-direction: column;
        align-items: flex-start !important;
    }
    
    .stRadio > div > label {
        width: 100%;
        text-align: left !important;
    }
    
    /* 사이드바 간격 */
    .sidebar .element-container {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# API 클라이언트 초기화
@st.cache_resource
def get_anthropic_client():
    api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
    if not api_key:
        st.error("❌ ANTHROPIC_API_KEY가 설정되지 않았습니다!")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

client = get_anthropic_client()

# 말투 분석 함수
def analyze_writing_style(sample_text):
    """샘플 글에서 말투 특징 추출"""
    features = []
    
    if "~해요" in sample_text or "~이에요" in sample_text:
        features.append("해요체")
    if "~더라구요" in sample_text or "~거든요" in sample_text:
        features.append("구어체")
    if any(emoji in sample_text for emoji in ["💰", "📈", "🎯", "✅", "❌"]):
        features.append("이모지 활용")
    if "안녕하세요" in sample_text or "오늘은" in sample_text:
        features.append("친근한 인사")
    if "[이미지:" in sample_text or "사진 설명" in sample_text:
        features.append("이미지 자리 표시")
    
    return features if features else ["일반적인 블로그 스타일"]

# 글 생성 함수
def generate_content(topic, platform, tone, word_count, style_sample, use_emoji, use_hashtags, use_image_placeholders):
    """Claude API로 콘텐츠 생성"""
    
    # 플랫폼별 설정
    platform_configs = {
        "네이버 블로그": {"max_length": 2500, "format": "긴 형식, 단락 구분 명확"},
        "쓰레드": {"max_length": 800, "format": "짧은 문장, 번호 매기기"},
        "X(트위터)": {"max_length": 280, "format": "280자 이내, 임팩트 있게"},
        "인스타그램": {"max_length": 1500, "format": "줄바꿈 많이, 해시태그 충분히"},
        "유튜브 스크립트": {"max_length": 2500, "format": "말하는 듯한 구어체"},
        "뉴스레터": {"max_length": 2000, "format": "전문적이고 정보 전달 중심"}
    }
    
    config = platform_configs.get(platform, platform_configs["네이버 블로그"])
    
    # 말투 분석
    style_instructions = ""
    if style_sample:
        features = analyze_writing_style(style_sample)
        style_instructions = f"\n\n<말투 학습>\n다음 특징을 반영해주세요: {', '.join(features)}\n\n샘플 글:\n{style_sample[:500]}\n</말투 학습>"
    
    # 프롬프트 구성
    system_prompt = f"""당신은 {platform} 콘텐츠 전문 작가입니다.

<작성 규칙>
- 플랫폼: {platform}
- 형식: {config['format']}
- 목표 글자수: 약 {word_count}자
- 말투: {'친근하고 편안한 말투' if tone < 50 else '전문적이고 신뢰감 있는 말투'}
- 이모지: {'자연스럽게 사용' if use_emoji else '사용하지 않음'}
- 해시태그: {'마지막에 관련 해시태그 5-10개 추가' if use_hashtags else '사용하지 않음'}
- 이미지 자리: {'[이미지: 설명] 형태로 적절한 위치에 표시' if use_image_placeholders else '표시하지 않음'}
</작성 규칙>

{style_instructions}

주제에 대해 검색된 최신 정보를 바탕으로 정확하고 유익한 콘텐츠를 작성하세요."""

    user_prompt = f"주제: {topic}\n\n위 주제에 대해 {platform} 포스팅을 작성해주세요."
    
    # 진행 상황 표시
    with st.spinner("🔍 주제 분석 중..."):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            content = response.content[0].text
            return content
            
        except Exception as e:
            st.error(f"❌ 생성 중 오류 발생: {str(e)}")
            return None

# 메인 UI
st.markdown('<h1 class="main-header">✍️ 콘텐츠 생성</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">내 말투 학습 + 웹 검색 기반 자동 작성</p>', unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown("### 📝 말투 학습")
    
    style_sample = st.text_area(
        "내가 쓴 글을 붙여넣으면 말투를 학습해요",
        height=150,
        placeholder="내가 쓴 글을 여기에 붙여넣으세요...\n\n예: 안녕하세요! 오늘은 미국 주식에 대해 이야기해볼게요. 솔직히 처음엔 어려웠는데 하나씩 배우다 보니 재미있더라구요 😊",
        key="style_sample"
    )
    
    if style_sample:
        features = analyze_writing_style(style_sample)
        st.markdown("**🎯 감지된 스타일:**")
        for feature in features:
            st.markdown(f'<span class="style-tag">{feature}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📱 플랫폼")
    
    # 라디오 버튼으로 변경 (왼쪽 정렬)
    platform = st.radio(
        "플랫폼 선택",
        ["네이버 블로그", "쓰레드", "X(트위터)", "인스타그램", "유튜브 스크립트", "뉴스레터"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 💬 말투")
    tone = st.slider(
        "말투 조절",
        0, 100, 30,
        label_visibility="collapsed"
    )
    col1, col2 = st.columns(2)
    col1.markdown("😊 친근함")
    col2.markdown("👔 전문성")
    
    st.markdown("---")
    st.markdown("### 📏 글자수")
    word_count = st.select_slider(
        "글자수 선택",
        options=[300, 500, 800, 1200, 1500, 2000, 2500],
        value=800,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 🎨 추가 옵션")
    use_emoji = st.checkbox("이모지 사용", value=True)
    use_hashtags = st.checkbox("해시태그 추가", value=True)
    use_image_placeholders = st.checkbox("이미지 자리 표시", value=True)

# 메인 영역
st.markdown("### 🔍 주제 입력")
topic = st.text_input(
    "주제를 입력하세요",
    placeholder="예: 다이소 보조배터리 사용 후기, 배당주 투자 전략, ChatGPT 활용법",
    label_visibility="collapsed"
)

st.markdown("---")

# 생성 버튼
if st.button("✨ 콘텐츠 생성하기", type="primary", use_container_width=True):
    if not topic:
        st.warning("⚠️ 주제를 입력해주세요!")
    else:
        content = generate_content(
            topic, platform, tone, word_count,
            style_sample,
            use_emoji, use_hashtags, use_image_placeholders
        )
        
        if content:
            st.success("✅ 생성 완료!")
            
            # 결과 표시
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 다운로드 버튼
            col1, col2 = st.columns(2)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{platform}_{topic[:10]}_{timestamp}.txt"
            
            col1.download_button(
                "💾 TXT 다운로드",
                content,
                filename,
                mime="text/plain",
                use_container_width=True
            )
