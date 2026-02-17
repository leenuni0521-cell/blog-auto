import streamlit as st
import anthropic
import json
import os
import requests
import base64
from datetime import datetime
from openai import OpenAI

st.set_page_config(page_title="AI 콘텐츠 생성기", page_icon="✦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #0c0c14; }
[data-testid="stSidebar"] { background: #13131f !important; border-right: 1px solid #2a2a42; }
[data-testid="stSidebarContent"] { padding: 20px 16px; }
.main .block-container { padding: 24px 32px; }
h1,h2,h3,p,div,label,span { color: #e8e8f8 !important; }

.nav-logo { font-size: 1.1rem; font-weight: 700; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #2a2a42; }
.nav-logo span { color: #6c63ff !important; }

.stRadio > div { flex-direction: column !important; gap: 6px !important; }
.stRadio > div > label {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    cursor: pointer !important;
    font-size: 0.9rem !important;
    transition: all 0.15s !important;
}
.stRadio > div > label:hover { background: rgba(108,99,255,0.08) !important; }
.stRadio > div > label:has(input:checked) {
    background: rgba(108,99,255,0.15) !important;
    border-color: rgba(108,99,255,0.4) !important;
}

.style-card { background: rgba(108,99,255,0.07); border: 1.5px solid rgba(108,99,255,0.3); border-radius: 12px; padding: 16px; margin-bottom: 8px; }
.result-card { background: #13131f; border: 1px solid #2a2a42; border-radius: 14px; padding: 24px; line-height: 1.95; font-size: 0.9rem; white-space: pre-wrap; color: #cccce0 !important; }
.search-info { background: rgba(74,222,128,0.07); border: 1px solid rgba(74,222,128,0.25); border-radius: 8px; padding: 10px 14px; font-size: 0.78rem; color: #4ade80 !important; margin-top: 8px; }
.stat-box { background: #1a1a2e; border: 1px solid #2a2a42; border-radius: 10px; padding: 12px; text-align: center; }
.img-prompt-card { background: rgba(255,101,132,0.06); border: 1.5px solid rgba(255,101,132,0.25); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.sec-label { font-size: 0.7rem; font-weight: 700; color: #6666aa !important; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 6px; display: block; }

.stButton > button { background: linear-gradient(135deg, #6c63ff, #9c63ff) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; width: 100% !important; padding: 12px !important; }
.stButton > button:hover { opacity: 0.88 !important; }
.stTextArea textarea, .stTextInput input { background: #1a1a2e !important; border: 1.5px solid #2a2a42 !important; color: #e8e8f8 !important; border-radius: 10px !important; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color: #6c63ff !important; }
.stSelectbox > div > div { background: #1a1a2e !important; border: 1.5px solid #2a2a42 !important; color: #e8e8f8 !important; border-radius: 10px !important; }
.stSlider > div > div > div { background: #6c63ff !important; }
.stDivider { border-color: #2a2a42 !important; }
[data-testid="stMarkdownContainer"] p { color: #cccce0 !important; }
</style>
""", unsafe_allow_html=True)


# ── API 키 로드 ──────────────────────────────────────
def get_anthropic_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)["anthropic"]["api_key"]
    except:
        return None

def get_openai_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        pass
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f).get("openai", {}).get("api_key", "")
    except:
        return None


# ── 사이드바 ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nav-logo"><span>AI</span> 콘텐츠 생성기</div>', unsafe_allow_html=True)
    menu = st.radio(
        "메뉴",
        ["✍️  콘텐츠 생성", "🖼️  이미지 생성"],
        label_visibility="collapsed"
    )
    st.divider()
    st.markdown('<p style="font-size:0.72rem;color:#6666aa !important">Claude + GPT-Image-1<br>블로그 자동화 도구</p>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# 페이지 1: 콘텐츠 생성
# ════════════════════════════════════════════════════
if menu == "✍️  콘텐츠 생성":

    st.markdown("# ✍️ 콘텐츠 생성")
    st.markdown('<p style="color:#6666aa;margin-top:-12px">내 말투 학습 + 웹 검색 기반 자동 작성</p>', unsafe_allow_html=True)
    st.divider()

    col_left, col_right = st.columns([1, 1.6], gap="large")

    with col_left:
        st.markdown('<span class="sec-label">✦ 말투 학습</span>', unsafe_allow_html=True)
        st.markdown('<div class="style-card">', unsafe_allow_html=True)
        style_sample = st.text_area(
            "말투 샘플",
            placeholder="내가 쓴 블로그 글을 여기에 붙여넣어 주세요!\nAI가 말투, 어미, 구성 방식을 학습해서\n똑같은 스타일로 글을 써드려요 😊",
            height=150, label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

        st.markdown('<span class="sec-label">🔍 주제 입력</span>', unsafe_allow_html=True)
        topic = st.text_input("주제", placeholder="예: 다이소 무선 랜카드, 애플워치 SE2 후기...", label_visibility="collapsed")
        st.divider()

        st.markdown('<span class="sec-label">📱 플랫폼</span>', unsafe_allow_html=True)
        platform = st.radio("플랫폼", ["네이버 블로그","쓰레드","X(트위터)","인스타그램","유튜브 스크립트","뉴스레터"], horizontal=True, label_visibility="collapsed")
        st.divider()

        st.markdown('<span class="sec-label">🎙️ 말투 조절</span>', unsafe_allow_html=True)
        tone = st.select_slider("말투", options=[0,25,50,75,100], value=50,
            format_func=lambda x: ["😊 친근","😄 캐주얼","🤝 균형","📘 전문","🎩 격식"][x//25],
            label_visibility="collapsed")

        st.markdown('<span class="sec-label">📏 글자수</span>', unsafe_allow_html=True)
        wc_map = {"짧게 (300자)":300,"보통 (800자)":800,"상세히 (1500자)":1500,"블로그 (2500자)":2500}
        wc_label = st.select_slider("글자수", options=list(wc_map.keys()), value="보통 (800자)", label_visibility="collapsed")
        word_count = wc_map[wc_label]
        st.divider()

        st.markdown('<span class="sec-label">⚙️ 옵션</span>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            use_emoji = st.checkbox("이모지 소제목", value=True)
            use_hashtag = st.checkbox("해시태그 생성", value=True)
        with c2:
            use_img = st.checkbox("이미지 자리 표시", value=True)
            use_next = st.checkbox("다음 편 예고")
        st.divider()
        generate_btn = st.button("✦ 콘텐츠 생성하기")

    with col_right:
        st.markdown('<span class="sec-label">생성된 콘텐츠</span>', unsafe_allow_html=True)

        if generate_btn:
            if not topic:
                st.warning("주제를 입력해주세요!")
            else:
                api_key = get_anthropic_key()
                if not api_key:
                    st.error("config.json에서 Anthropic API 키를 확인해주세요!")
                else:
                    client = anthropic.Anthropic(api_key=api_key)
                    tone_desc = {0:"매우 친근하고 편한 말투",25:"친근하고 캐주얼한 해요체",50:"친근하면서 신뢰감 있는 해요체",75:"전문적이면서 이해하기 쉬운 톤",100:"전문적이고 격식 있는 톤"}
                    tone_text = tone_desc[min(tone_desc.keys(), key=lambda x: abs(x-tone))]
                    platform_guide = {
                        "네이버 블로그": f"네이버 블로그. {word_count}자 내외. 소제목 구분, 이미지 자리 포함.",
                        "쓰레드": "쓰레드. 500자 이내. 짧고 임팩트 있게.",
                        "X(트위터)": "X. 280자 이내. 핵심만.",
                        "인스타그램": "인스타그램. 이모지 적극 활용. 해시태그 10개 이상.",
                        "유튜브 스크립트": f"유튜브 스크립트. {word_count}자 내외. 인트로/본론/아웃트로.",
                        "뉴스레터": f"이메일 뉴스레터. {word_count}자 내외."
                    }
                    opts = []
                    if use_emoji: opts.append("소제목 앞 이모지")
                    if use_hashtag: opts.append("글 끝 해시태그")
                    if use_img: opts.append("[이미지: 설명] 형식 이미지 자리")
                    if use_next: opts.append("다음 편 예고")

                    style_inst = ""
                    if style_sample and len(style_sample) > 50:
                        style_inst = f"\n## 말투 학습\n아래 샘플의 말투, 어미, 구성 방식을 그대로 따라주세요.\n---\n{style_sample[:1500]}\n---\n"

                    system = f"""당신은 블로그 콘텐츠 작성 전문가예요.
{style_inst}
규칙: 말투={tone_text}, 플랫폼={platform_guide.get(platform,'')}, 옵션={', '.join(opts)}
웹 검색으로 최신 정보를 찾아서 정확하고 자연스럽게 써주세요."""

                    search_queries = []
                    final_text = ""

                    with st.status("✦ AI가 글을 작성하고 있어요...", expanded=True) as status:
                        st.write("🔍 최신 정보 검색 중...")
                        response = client.messages.create(
                            model="claude-sonnet-4-5-20250929",
                            max_tokens=4096,
                            system=system,
                            tools=[{"type": "web_search_20250305", "name": "web_search"}],
                            messages=[{"role": "user", "content": f'"{topic}"에 대한 콘텐츠를 웹 검색 후 작성해주세요.'}]
                        )
                        for block in response.content:
                            if block.type == "tool_use" and block.name == "web_search":
                                search_queries.append(block.input.get("query", ""))
                                st.write(f"🔎 검색: {block.input.get('query','')}")
                        st.write("✍️ 글 작성 중...")
                        for block in response.content:
                            if hasattr(block, "text"):
                                final_text += block.text

                        if response.stop_reason == "tool_use":
                            msgs = [
                                {"role": "user", "content": f'"{topic}"에 대한 콘텐츠를 웹 검색 후 작성해주세요.'},
                                {"role": "assistant", "content": response.content},
                                {"role": "user", "content": [{"type":"tool_result","tool_use_id":b.id,"content":"검색 완료."} for b in response.content if b.type=="tool_use"]}
                            ]
                            r2 = client.messages.create(model="claude-sonnet-4-5-20250929", max_tokens=4096, system=system, messages=msgs)
                            final_text = "".join(b.text for b in r2.content if hasattr(b,"text"))
                        status.update(label="✅ 완료!", state="complete")

                    st.session_state["result"] = final_text.strip()
                    st.session_state["queries"] = search_queries
                    st.session_state["topic"] = topic
                    st.session_state["platform"] = platform

        if "result" in st.session_state:
            result = st.session_state["result"]
            queries = st.session_state.get("queries", [])
            if queries:
                st.markdown(f'<div class="search-info">✦ 웹 검색 완료 — {len(queries)}개 검색: {" / ".join(queries)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-card">{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            with c1: st.markdown(f'<div class="stat-box"><div style="font-size:1.1rem;font-weight:700;color:#6c63ff">{len(result):,}</div><div style="font-size:0.7rem;color:#6666aa">글자수</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="stat-box"><div style="font-size:0.85rem;font-weight:700;color:#6c63ff">{st.session_state["platform"]}</div><div style="font-size:0.7rem;color:#6666aa">플랫폼</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="stat-box"><div style="font-size:1rem;font-weight:700;color:#6c63ff">{"학습됨" if style_sample else "기본"}</div><div style="font-size:0.7rem;color:#6666aa">말투</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            bc1, bc2 = st.columns(2)
            with bc1:
                st.download_button("⬇️ 파일 저장", result,
                    file_name=f"[{datetime.now().strftime('%m.%d')}] {st.session_state['topic'][:20]}.txt",
                    mime="text/plain", use_container_width=True)
            with bc2:
                if st.button("🔄 다시 생성", use_container_width=True):
                    del st.session_state["result"]
                    st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center;padding:80px 0;color:#6666aa">
                <div style="font-size:3rem;margin-bottom:16px">✍️</div>
                <div style="font-size:0.9rem;line-height:1.8">말투 샘플을 붙여넣고<br>주제를 입력하면<br>내 스타일로 글이 나와요!</div>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════
# 페이지 2: 이미지 생성 (gpt-image-1)
# ════════════════════════════════════════════════════
elif menu == "🖼️  이미지 생성":

    st.markdown("# 🖼️ 이미지 생성")
    st.markdown('<p style="color:#6666aa;margin-top:-12px">ChatGPT gpt-image-1 기반 블로그 이미지 자동 생성</p>', unsafe_allow_html=True)
    st.divider()

    col_left, col_right = st.columns([1, 1.4], gap="large")

    with col_left:
        st.markdown('<span class="sec-label">🎨 이미지 설명</span>', unsafe_allow_html=True)
        st.markdown('<div class="img-prompt-card">', unsafe_allow_html=True)
        img_topic = st.text_input("블로그 주제 (자동 프롬프트 생성)", placeholder="예: 다이소 무선 랜카드 리뷰, S&P500 투자 입문", label_visibility="collapsed")
        img_prompt = st.text_area("직접 설명 (선택)", placeholder="원하는 이미지를 자세히 설명해주세요.\n비워두면 주제를 보고 자동으로 만들어요!", height=120, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

        st.markdown('<span class="sec-label">📐 이미지 크기</span>', unsafe_allow_html=True)
        size = st.radio("크기", ["1024x1024 (정사각형)", "1536x1024 (가로형)", "1024x1536 (세로형)"],
                        label_visibility="collapsed")
        size_map = {"1024x1024 (정사각형)":"1024x1024","1536x1024 (가로형)":"1536x1024","1024x1536 (세로형)":"1024x1536"}
        img_size = size_map[size]
        st.divider()

        st.markdown('<span class="sec-label">🎭 스타일</span>', unsafe_allow_html=True)
        style_type = st.radio("스타일", ["📸 실사 사진 스타일", "🎨 일러스트/디지털아트", "📊 인포그래픽/깔끔한 디자인", "✏️ 미니멀 플랫 디자인"], label_visibility="collapsed")
        st.divider()

        st.markdown('<span class="sec-label">🌍 언어 설정</span>', unsafe_allow_html=True)
        lang = st.radio("텍스트 없음 / 영문 / 한글", ["텍스트 없음", "영문 텍스트 포함", "한글 텍스트 포함"], horizontal=True, label_visibility="collapsed")
        st.divider()

        num_images = st.slider("생성 개수", 1, 4, 1)
        generate_img_btn = st.button("🖼️ 이미지 생성하기")

    with col_right:
        st.markdown('<span class="sec-label">생성된 이미지</span>', unsafe_allow_html=True)

        if generate_img_btn:
            if not img_topic and not img_prompt:
                st.warning("주제나 이미지 설명을 입력해주세요!")
            else:
                openai_key = get_openai_key()
                if not openai_key:
                    st.error("config.json에 OpenAI API 키가 없어요!\n\n`config.json`의 `openai.api_key`를 채워주세요.")
                else:
                    # 스타일 프롬프트 매핑
                    style_prompts = {
                        "📸 실사 사진 스타일": "photorealistic, high quality photography, professional lighting, sharp focus",
                        "🎨 일러스트/디지털아트": "digital illustration, colorful, modern art style, clean lines",
                        "📊 인포그래픽/깔끔한 디자인": "clean infographic design, flat design, professional, modern layout",
                        "✏️ 미니멀 플랫 디자인": "minimalist flat design, simple shapes, pastel colors, clean"
                    }
                    lang_prompts = {
                        "텍스트 없음": "no text, no letters, no words",
                        "영문 텍스트 포함": "with English text overlay",
                        "한글 텍스트 포함": "with Korean text overlay"
                    }

                    # 프롬프트 자동 생성
                    if img_prompt:
                        final_prompt = f"{img_prompt}, {style_prompts[style_type]}, {lang_prompts[lang]}"
                    else:
                        topic_prompt = f"Blog thumbnail image about '{img_topic}', for Korean lifestyle/economy blog"
                        final_prompt = f"{topic_prompt}, {style_prompts[style_type]}, {lang_prompts[lang]}, high quality"

                    with st.status(f"🎨 이미지 생성 중... ({num_images}장)", expanded=True) as status:
                        st.write(f"📝 프롬프트: {final_prompt[:80]}...")
                        try:
                            oai_client = OpenAI(api_key=openai_key)
                            images = []
                            for i in range(num_images):
                                st.write(f"🖼️ {i+1}/{num_images}번째 이미지 생성 중...")
                                response = oai_client.images.generate(
                                    model="gpt-image-1",
                                    prompt=final_prompt,
                                    size=img_size,
                                    quality="high",
                                    n=1,
                                )
                                # base64로 받기
                                img_b64 = response.data[0].b64_json
                                if img_b64:
                                    img_bytes = base64.b64decode(img_b64)
                                else:
                                    img_url = response.data[0].url
                                    img_bytes = requests.get(img_url).content
                                images.append(img_bytes)

                            st.session_state["gen_images"] = images
                            st.session_state["img_topic"] = img_topic or "이미지"
                            status.update(label=f"✅ {num_images}장 완성!", state="complete")

                        except Exception as e:
                            status.update(label="❌ 오류 발생", state="error")
                            st.error(f"오류: {str(e)}")

        if "gen_images" in st.session_state:
            images = st.session_state["gen_images"]
            topic_name = st.session_state.get("img_topic", "이미지")

            if len(images) == 1:
                st.image(images[0], use_container_width=True)
                st.download_button("⬇️ 이미지 저장", images[0],
                    file_name=f"[{datetime.now().strftime('%m.%d')}] {topic_name[:20]}.png",
                    mime="image/png", use_container_width=True)
            else:
                cols = st.columns(2)
                for i, img in enumerate(images):
                    with cols[i % 2]:
                        st.image(img, use_container_width=True)
                        st.download_button(f"⬇️ {i+1}번 저장", img,
                            file_name=f"[{datetime.now().strftime('%m.%d')}] {topic_name[:15]}_{i+1}.png",
                            mime="image/png", use_container_width=True, key=f"dl_{i}")

            if st.button("🔄 다시 생성"):
                del st.session_state["gen_images"]
                st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center;padding:80px 0;color:#6666aa">
                <div style="font-size:3rem;margin-bottom:16px">🖼️</div>
                <div style="font-size:0.9rem;line-height:1.8">블로그 주제를 입력하면<br>어울리는 이미지를<br>자동으로 만들어드려요!</div>
            </div>""", unsafe_allow_html=True)
