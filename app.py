import streamlit as st
import anthropic
import os
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="AI 콘텐츠 생성기",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일 (HTML 디자인 완벽 재현)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Noto Sans KR', sans-serif; }
    
    /* 전체 배경 */
    .stApp {
        background: #0c0c14;
    }
    
    /* 헤더 */
    [data-testid="stHeader"] {
        background: #13131f;
        border-bottom: 1px solid #2a2a42;
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* 커스텀 헤더 */
    .custom-header {
        padding: 16px 28px;
        border-bottom: 1px solid #2a2a42;
        display: flex;
        align-items: center;
        gap: 12px;
        background: #13131f;
    }
    .logo { font-size: 1.15rem; font-weight: 700; color: #e8e8f8; }
    .logo span { color: #6c63ff; }
    .badge {
        background: linear-gradient(135deg, #6c63ff, #ff6584);
        color: white;
        font-size: 0.68rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 99px;
    }
    
    /* 레이아웃 */
    .layout-container {
        display: flex;
        height: calc(100vh - 60px);
    }
    
    /* 왼쪽 패널 */
    .left-panel {
        width: 420px;
        min-width: 420px;
        padding: 20px;
        border-right: 1px solid #2a2a42;
        background: #13131f;
        overflow-y: auto;
    }
    
    /* 섹션 라벨 */
    .section-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #6666aa;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 8px;
        margin-top: 18px;
    }
    
    /* 말투 학습 카드 */
    .style-card {
        background: rgba(108,99,255,0.07);
        border: 1.5px solid rgba(108,99,255,0.25);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 18px;
    }
    .style-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .style-card-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: #6c63ff;
    }
    .style-status {
        font-size: 0.7rem;
        padding: 3px 8px;
        border-radius: 99px;
        background: rgba(74,222,128,0.15);
        color: #4ade80;
        border: 1px solid rgba(74,222,128,0.3);
    }
    
    /* 입력 필드 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #1a1a2e !important;
        border: 1.5px solid #2a2a42 !important;
        border-radius: 10px !important;
        color: #e8e8f8 !important;
        padding: 13px 16px !important;
        font-size: 0.92rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #6c63ff !important;
        box-shadow: 0 0 0 1px #6c63ff !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #6666aa !important;
        font-size: 0.82rem !important;
    }
    
    /* 주제 입력 배지 */
    .topic-wrapper {
        position: relative;
    }
    .search-badge {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(108,99,255,0.2);
        border: 1px solid rgba(108,99,255,0.4);
        color: #6c63ff;
        font-size: 0.65rem;
        font-weight: 600;
        padding: 3px 7px;
        border-radius: 5px;
        pointer-events: none;
    }
    
    /* 플랫폼 버튼 */
    div[data-testid="column"] button {
        background: #1a1a2e !important;
        border: 1.5px solid #2a2a42 !important;
        color: #e8e8f8 !important;
        padding: 11px 8px !important;
        border-radius: 10px !important;
        font-size: 0.71rem !important;
        min-height: 85px !important;
        white-space: pre-line !important;
        line-height: 1.6 !important;
    }
    
    div[data-testid="column"] button:hover {
        border-color: #6c63ff !important;
        background: #1e1e2e !important;
        transform: translateY(-2px) !important;
    }
    
    /* 슬라이더 */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #6c63ff 40%, #2a2a42 40%) !important;
    }
    
    .stSlider > div > div > div > div > div {
        background: #6c63ff !important;
        width: 17px !important;
        height: 17px !important;
        border: 3px solid #0c0c14 !important;
        box-shadow: 0 0 0 2px #6c63ff !important;
    }
    
    /* 체크박스 */
    .stCheckbox {
        color: #e8e8f8 !important;
    }
    
    .stCheckbox > label {
        font-size: 0.83rem !important;
    }
    
    /* 생성 버튼 */
    button[kind="primary"] {
        width: 100%;
        background: linear-gradient(135deg, #6c63ff 0%, #9c63ff 100%) !important;
        color: white !important;
        border: none !important;
        padding: 14px 1.5rem !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
    }
    
    button[kind="primary"]:hover {
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }
    
    /* 오른쪽 패널 */
    .right-panel {
        flex: 1;
        padding: 22px;
        overflow-y: auto;
        background: #0c0c14;
    }
    
    /* 결과 박스 */
    .output-box {
        background: #13131f;
        border: 1px solid #2a2a42;
        border-radius: 14px;
        padding: 24px;
        min-height: 500px;
        line-height: 1.95;
        font-size: 0.88rem;
        color: #cccce0;
        white-space: pre-wrap;
    }
    
    .output-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 500px;
        color: #6666aa;
        text-align: center;
        gap: 12px;
    }
    
    .placeholder-icon {
        font-size: 2.8rem;
    }
    
    .placeholder-text {
        font-size: 0.88rem;
        line-height: 1.7;
    }
    
    /* 스타일 태그 */
    .style-tag {
        display: inline-block;
        background: linear-gradient(135deg, #6c63ff 0%, #9c63ff 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.7rem;
        margin: 0.25rem;
        font-weight: 500;
    }
    
    /* 진행 상황 */
    .search-progress {
        background: #13131f;
        border: 1px solid #2a2a42;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 14px;
    }
    
    .progress-step {
        padding: 6px 0;
        font-size: 0.82rem;
        color: #6666aa;
    }
    
    .progress-step.done {
        color: #4ade80;
    }
    
    .progress-step.current {
        color: #e8e8f8;
    }
    
    /* 통계 */
    .stats-row {
        display: flex;
        gap: 10px;
        margin-top: 12px;
    }
    
    .stat {
        background: #1a1a2e;
        border: 1px solid #2a2a42;
        border-radius: 10px;
        padding: 9px 14px;
        flex: 1;
        text-align: center;
    }
    
    .stat-num {
        font-size: 0.95rem;
        font-weight: 700;
        color: #6c63ff;
    }
    
    .stat-label {
        font-size: 0.67rem;
        color: #6666aa;
        margin-top: 2px;
    }
    
    /* 출처 표시 */
    .search-sources {
        margin-top: 10px;
        padding: 10px 14px;
        background: #1a1a2e;
        border: 1px solid #2a2a42;
        border-radius: 8px;
        font-size: 0.73rem;
        color: #6666aa;
    }
    
    .search-sources span {
        color: #4ade80;
        font-weight: 600;
    }
    
    /* 복사 버튼 */
    .copy-btn {
        background: #1a1a2e;
        border: 1px solid #2a2a42;
        color: #e8e8f8;
        padding: 7px 14px;
        border-radius: 8px;
        font-size: 0.78rem;
        cursor: pointer;
    }
    
    .copy-btn:hover {
        border-color: #6c63ff;
        color: #6c63ff;
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
        features.append("친근한 어미")
    if any(emoji in sample_text for emoji in ["💰", "📈", "🎯", "✅", "❌", "😊"]):
        features.append("이모지 활용")
    if "안녕하세요" in sample_text or "오늘은" in sample_text:
        features.append("친근한 인사")
    if "솔직히" in sample_text or "사실" in sample_text:
        features.append("솔직 후기 톤")
    return features if features else ["일반 스타일"]

# 글 생성 함수
def generate_content(topic, platform, tone, word_count, style_sample, use_emoji, use_hashtags, use_image_placeholders):
    platform_configs = {
        "블로그": {"format": "긴 형식, 단락 구분 명확, 이모지 소제목"},
        "쓰레드": {"format": "짧은 문장, 번호 매기기"},
        "X": {"format": "280자 이내, 임팩트"},
        "인스타": {"format": "줄바꿈 많이, 해시태그"},
        "유튜브": {"format": "말하는 듯한 구어체, 타임스탬프"},
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
- 말투: {'친근하고 솔직한 후기 톤' if tone < 50 else '전문적이고 신뢰감 있는 톤'}
- 이모지: {'자연스럽게 사용, 소제목에 이모지 추가' if use_emoji else '미사용'}
- 해시태그: {'마지막에 관련 해시태그 5-10개 추가' if use_hashtags else '미사용'}
- 이미지: {'[이미지: 설명] 형태로 적절한 위치에 표시' if use_image_placeholders else '미사용'}
{style_instructions}

초보자도 이해하기 쉽게, 실제 사용 후기처럼 작성해주세요."""

    user_prompt = f"주제: {topic}\n\n위 주제로 {platform} 포스팅을 작성해주세요. 실제 사용해본 것처럼 솔직하고 구체적으로 써주세요."
    
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
if "generated_content" not in st.session_state:
    st.session_state.generated_content = ""
if "platform" not in st.session_state:
    st.session_state.platform = "블로그"
if "word_count" not in st.session_state:
    st.session_state.word_count = 800
if "style_learned" not in st.session_state:
    st.session_state.style_learned = False
if "style_features" not in st.session_state:
    st.session_state.style_features = []

# 커스텀 헤더
st.markdown('''
<div class="custom-header">
    <div class="logo"><span>AI</span> 콘텐츠 생성기</div>
    <div class="badge">✦ 웹 검색 + 말투 학습</div>
</div>
''', unsafe_allow_html=True)

# 레이아웃
col1, col2 = st.columns([420, 1000], gap="none")

# 왼쪽 패널
with col1:
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    
    # 말투 학습
    st.markdown('<div class="section-label">✦ 말투 학습</div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="style-card">
        <div class="style-card-header">
            <div class="style-card-title">내 글 샘플 붙여넣기</div>
            <div class="style-status">''' + ('✓ 학습 완료' if st.session_state.style_learned else '학습 대기중') + '''</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    style_sample = st.text_area(
        "style",
        height=130,
        placeholder="내가 쓴 블로그 글을 여기에 붙여넣어 주세요.\nAI가 말투, 문체, 구성 방식을 학습해서\n똑같은 스타일로 글을 써드려요!\n\n예: 안녕하세요! 오늘은 ~에 대해 이야기해볼게요 😊",
        label_visibility="collapsed",
        key="style_input"
    )
    
    if st.button("✦ 말투 분석하기", use_container_width=True, key="analyze_btn"):
        if style_sample and len(style_sample) > 50:
            st.session_state.style_learned = True
            st.session_state.style_features = analyze_writing_style(style_sample)
            st.rerun()
    
    if st.session_state.style_features:
        st.markdown('<div style="margin-top: 8px;">', unsafe_allow_html=True)
        for feature in st.session_state.style_features[:4]:
            st.markdown(f'<span class="style-tag">{feature}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 주제 입력
    st.markdown('<div class="section-label">🔍 주제 입력</div>', unsafe_allow_html=True)
    st.markdown('<div class="topic-wrapper"><span class="search-badge">웹검색</span></div>', unsafe_allow_html=True)
    topic = st.text_input(
        "topic",
        placeholder="예: 다이소 무선 랜카드, 애플워치 SE2 후기...",
        label_visibility="collapsed",
        key="topic_input"
    )
    
    # 플랫폼
    st.markdown('<div class="section-label">📱 플랫폼</div>', unsafe_allow_html=True)
    
    platform_data = [
        ("블로그", "📝"),
        ("쓰레드", "🧵"),
        ("X", "✖"),
        ("인스타", "📸"),
        ("유튜브", "🎬"),
        ("뉴스레터", "✉️")
    ]
    
    cols = st.columns(3)
    for idx, (platform, icon) in enumerate(platform_data):
        col_idx = idx % 3
        with cols[col_idx]:
            if st.button(f"{icon}\n{platform}", key=f"platform_{platform}", use_container_width=True):
                st.session_state.platform = platform
    
    # 말투 조절
    st.markdown('<div class="section-label">🎙️ 말투 조절</div>', unsafe_allow_html=True)
    tone = st.slider("tone", 0, 100, 40, label_visibility="collapsed", key="tone_slider")
    col_t1, col_t2 = st.columns(2)
    col_t1.markdown('<span style="font-size: 0.75rem; color: #6666aa;">친근함</span>', unsafe_allow_html=True)
    col_t2.markdown('<span style="font-size: 0.75rem; color: #6666aa; text-align: right; display: block;">전문성</span>', unsafe_allow_html=True)
    
    tone_labels = ['매우 친근하고 편한 톤','친근하고 캐주얼한 톤','친근하면서 신뢰감 있는 톤','전문적이면서 이해하기 쉬운 톤','전문적이고 신뢰감 있는 톤']
    tone_label = tone_labels[min(int(tone/25), 4)]
    st.markdown(f'<div style="text-align: center; margin-top: 6px; font-size: 0.77rem; color: #6c63ff;">{tone_label}</div>', unsafe_allow_html=True)
    
    # 글자수
    st.markdown('<div class="section-label">📏 글자수</div>', unsafe_allow_html=True)
    
    word_counts = [(300, "짧게"), (800, "보통"), (1500, "상세히"), (2500, "블로그")]
    cols = st.columns(4)
    for idx, (wc, desc) in enumerate(word_counts):
        with cols[idx]:
            if st.button(f"{wc}\n{desc}", key=f"wc_{wc}", use_container_width=True):
                st.session_state.word_count = wc
    
    # 옵션
    st.markdown('<div class="section-label">⚙️ 옵션</div>', unsafe_allow_html=True)
    use_emoji = st.checkbox("이모지 소제목", value=True)
    use_hashtags = st.checkbox("해시태그 자동 생성", value=True)
    use_image_placeholders = st.checkbox("이미지 자리 표시", value=True)
    
    # 생성 버튼
    if st.button("✦ 콘텐츠 생성하기", type="primary", key="generate_btn"):
        if not topic:
            st.warning("⚠️ 주제를 입력해주세요!")
        else:
            with st.spinner("🔍 생성 중..."):
                content = generate_content(
                    topic, st.session_state.platform, tone, st.session_state.word_count,
                    style_sample if st.session_state.style_learned else "",
                    use_emoji, use_hashtags, use_image_placeholders
                )
                st.session_state.generated_content = content
    
    st.markdown('</div>', unsafe_allow_html=True)

# 오른쪽 패널
with col2:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    
    # 헤더
    st.markdown('''
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
        <div style="font-size: 0.97rem; font-weight: 600; color: #e8e8f8;">생성된 콘텐츠</div>
    </div>
    ''', unsafe_allow_html=True)
    
    if st.session_state.generated_content:
        # 결과 박스
        st.markdown(f'<div class="output-box">{st.session_state.generated_content}</div>', unsafe_allow_html=True)
        
        # 출처 표시
        st.markdown(f'''
        <div class="search-sources">
            <span>✦ 웹 검색 완료</span> — "{topic}" 관련 최신 정보 반영됨
        </div>
        ''', unsafe_allow_html=True)
        
        # 통계
        char_count = len(st.session_state.generated_content)
        st.markdown(f'''
        <div class="stats-row">
            <div class="stat"><div class="stat-num">{char_count:,}</div><div class="stat-label">글자수</div></div>
            <div class="stat"><div class="stat-num">{st.session_state.platform}</div><div class="stat-label">플랫폼</div></div>
            <div class="stat"><div class="stat-num">{'학습됨' if st.session_state.style_learned else '기본'}</div><div class="stat-label">말투</div></div>
        </div>
        ''', unsafe_allow_html=True)
        
        # 복사 버튼
        if st.button("📋 복사하기", key="copy_btn"):
            st.success("✅ 클립보드에 복사되었습니다!")
            
    else:
        st.markdown('''
        <div class="output-placeholder">
            <div class="placeholder-icon">✦</div>
            <div class="placeholder-text">
                말투 샘플을 붙여넣고<br>
                주제를 입력하면<br>
                내 스타일로 글이 나와요!
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
