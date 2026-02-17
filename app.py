import streamlit as st
import anthropic
import os
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="AI 콘텐츠 생성기",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 (다크 네이비 테마)
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: #0f1419;
    }
    
    /* 사이드바 배경 */
    [data-testid="stSidebar"] {
        background: #1a1f2e;
    }
    
    /* 사이드바 버튼 커스텀 */
    [data-testid="stSidebar"] .stButton>button {
        background: #1e2433 !important;
        border: 1px solid #2d3748 !important;
        color: #9ca3af !important;
        font-weight: 500 !important;
        padding: 0.875rem 1rem !important;
        border-radius: 8px !important;
        transition: all 0.3s !important;
        text-align: left !important;
    }
    
    [data-testid="stSidebar"] .stButton>button:hover {
        border-color: #667eea !important;
        background: #252d3d !important;
        color: #e2e8f0 !important;
        transform: translateX(4px) !important;
    }
    
    /* placeholder 글씨 밝게 */
    ::placeholder {
        color: #6b7280 !important;
        opacity: 1 !important;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #1e2433 !important;
        border: 1px solid #2d3748 !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 1px #667eea !important;
    }
    
    /* 메인 헤더 */
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .header-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .sub-header {
        color: #9ca3af;
        margin-bottom: 2rem;
        font-size: 0.9rem;
    }
    
    /* 섹션 타이틀 */
    .section-title {
        color: #667eea;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 메뉴 스타일 */
    .menu-title {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: #6b7280;
        margin-bottom: 1rem;
        padding-left: 0.5rem;
    }
    
    /* 메인 콘텐츠 영역 버튼 (생성하기 등) */
    .stButton>button:not([data-testid="stSidebar"] .stButton>button) {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.875rem 1.5rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.3s !important;
    }
    
    .stButton>button:not([data-testid="stSidebar"] .stButton>button):hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* 결과 박스 */
    .output-box {
        background: #1e2433;
        border: 1px solid #2d3748;
        border-radius: 12px;
        padding: 1.5rem;
        min-height: 500px;
        color: #e2e8f0;
    }
    
    .output-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #6b7280;
        text-align: center;
        padding: 3rem 1rem;
    }
    
    .output-placeholder-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* 스타일 태그 */
    .style-tag {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        margin: 0.25rem;
        font-weight: 500;
    }
    
    /* 체크박스 스타일 */
    .stCheckbox {
        color: #e2e8f0;
    }
    
    /* 슬라이더 */
    .stSlider > div > div > div {
        background: #2d3748;
    }
    
    /* 구분선 */
    hr {
        border-color: #2d3748;
        margin: 1.5rem 0;
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
    features = []
    if "~해요" in sample_text or "~이에요" in sample_text:
        features.append("해요체")
    if "~더라구요" in sample_text or "~거든요" in sample_text:
        features.append("구어체")
    if any(emoji in sample_text for emoji in ["💰", "📈", "🎯", "✅", "❌"]):
        features.append("이모지 활용")
    if "안녕하세요" in sample_text or "오늘은" in sample_text:
        features.append("친근한 인사")
    return features if features else ["일반 스타일"]

# 글 생성 함수
def generate_content(topic, platform, tone, word_count, style_sample, use_emoji, use_hashtags, use_image_placeholders):
    platform_configs = {
        "블로그": {"format": "긴 형식, 단락 구분 명확"},
        "쓰레드": {"format": "짧은 문장, 번호 매기기"},
        "X": {"format": "280자 이내, 임팩트"},
        "인스타": {"format": "줄바꿈 많이, 해시태그"},
        "유튜브": {"format": "말하는 듯한 구어체"},
        "뉴스레터": {"format": "전문적, 정보 전달"}
    }
    
    config = platform_configs.get(platform, platform_configs["블로그"])
    
    style_instructions = ""
    if style_sample:
        features = analyze_writing_style(style_sample)
        style_instructions = f"\n\n말투 특징: {', '.join(features)}\n샘플: {style_sample[:300]}"
    
    system_prompt = f"""당신은 {platform} 콘텐츠 작가입니다.

- 플랫폼: {platform}
- 형식: {config['format']}
- 글자수: {word_count}자
- 말투: {'친근함' if tone < 50 else '전문성'}
- 이모지: {'사용' if use_emoji else '미사용'}
- 해시태그: {'추가' if use_hashtags else '미사용'}
- 이미지: {'[이미지: 설명] 표시' if use_image_placeholders else '미사용'}
{style_instructions}"""

    user_prompt = f"주제: {topic}\n\n위 주제로 {platform} 포스팅 작성해주세요."
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0.7,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"❌ 오류: {str(e)}"

# 세션 스테이트
if "mode" not in st.session_state:
    st.session_state.mode = "글쓰기"
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""
if "platform" not in st.session_state:
    st.session_state.platform = "블로그"
if "word_count" not in st.session_state:
    st.session_state.word_count = 800

# 사이드바 메뉴
with st.sidebar:
    st.markdown('<div class="menu-title">MENU</div>', unsafe_allow_html=True)
    
    # 글쓰기 버튼
    if st.button("✍️ 글쓰기", key="writing_menu", use_container_width=True):
        st.session_state.mode = "글쓰기"
    
    # 그림그리기 버튼
    if st.button("🎨 그림그리기", key="image_menu", use_container_width=True):
        st.session_state.mode = "그림그리기"

# 메인 레이아웃
if st.session_state.mode == "글쓰기":
    # 헤더
    st.markdown('''
    <div class="main-header">
        ✍️ AI 콘텐츠 생성기
        <span class="header-badge">✨ 글 공유 + 말투 학습</span>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">내 말투 학습 + 웹 검색 기반 자동 작성</p>', unsafe_allow_html=True)
    
    # 2단 레이아웃
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        # 주제 입력
        st.markdown('<div class="section-title">🔍 주제 입력</div>', unsafe_allow_html=True)
        topic = st.text_input(
            "주제",
            placeholder="예: 다이소 무선 랜카드, 배당주 투자 전략, ChatGPT 활용법",
            label_visibility="collapsed"
        )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 말투 학습
        st.markdown('<div class="section-title">📝 말투 학습</div>', unsafe_allow_html=True)
        style_sample = st.text_area(
            "샘플",
            height=100,
            placeholder="내가 쓴 글을 붙여넣으세요...\n\n예: 안녕하세요! 오늘은 미국 주식에 대해 이야기해볼게요. 솔직히 처음엔 어려웠는데 하나씩 배우다 보니 재미있더라구요 😊",
            label_visibility="collapsed"
        )
        
        if style_sample:
            features = analyze_writing_style(style_sample)
            for feature in features:
                st.markdown(f'<span class="style-tag">{feature}</span>', unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 플랫폼
        st.markdown('<div class="section-title">📱 플랫폼</div>', unsafe_allow_html=True)
        
        platforms = ["블로그", "쓰레드", "X", "인스타", "유튜브", "뉴스레터"]
        cols = st.columns(3)
        for idx, platform in enumerate(platforms):
            col_idx = idx % 3
            with cols[col_idx]:
                if st.button(platform, key=f"platform_{platform}", use_container_width=True):
                    st.session_state.platform = platform
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 말투 조절
        st.markdown('<div class="section-title">💬 말투 조절</div>', unsafe_allow_html=True)
        tone = st.slider("tone", 0, 100, 30, label_visibility="collapsed")
        col1, col2 = st.columns(2)
        col1.markdown("😊 친근함")
        col2.markdown("👔 전문성")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 글자수
        st.markdown('<div class="section-title">📏 글자수</div>', unsafe_allow_html=True)
        
        word_counts = [300, 800, 1500, 2500]
        cols = st.columns(4)
        for idx, wc in enumerate(word_counts):
            with cols[idx]:
                if st.button(str(wc), key=f"wc_{wc}", use_container_width=True):
                    st.session_state.word_count = wc
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 옵션
        st.markdown('<div class="section-title">🎨 옵션</div>', unsafe_allow_html=True)
        use_emoji = st.checkbox("이모지 사용", value=True)
        use_hashtags = st.checkbox("해시태그 자동 생성", value=True)
        use_image_placeholders = st.checkbox("이미지 자리 표시", value=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 생성 버튼
        if st.button("✨ 콘텐츠 생성하기", type="primary", key="generate_btn"):
            if not topic:
                st.warning("⚠️ 주제를 입력해주세요!")
            else:
                with st.spinner("🔍 생성 중..."):
                    content = generate_content(
                        topic, st.session_state.platform, tone, st.session_state.word_count,
                        style_sample, use_emoji, use_hashtags, use_image_placeholders
                    )
                    st.session_state.generated_content = content
    
    with right_col:
        st.markdown('<div class="section-title">📄 생성된 콘텐츠</div>', unsafe_allow_html=True)
        
        if st.session_state.generated_content:
            st.markdown('<div class="output-box">', unsafe_allow_html=True)
            st.markdown(st.session_state.generated_content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "💾 복사하기",
                st.session_state.generated_content,
                f"content_{timestamp}.txt",
                use_container_width=True,
                key="download_btn"
            )
        else:
            st.markdown('''
            <div class="output-box">
                <div class="output-placeholder">
                    <div class="output-placeholder-icon">✨</div>
                    <div>왼쪽 상단에서 주제를 입력하고</div>
                    <div>콘텐츠 생성하기를 눌러주세요!</div>
                    <div style="margin-top: 1rem; font-size: 0.875rem;">내 스타일로 글이 완성돼요</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

else:  # 그림그리기
    st.markdown('<h1 class="main-header">🎨 AI 이미지 생성</h1>', unsafe_allow_html=True)
    st.info("💡 준비 중입니다...")
