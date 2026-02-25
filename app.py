import streamlit as st
import anthropic
import json
import os
from datetime import datetime

st.set_page_config(page_title="AI 콘텐츠 생성기", page_icon="✦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; }

:root {
    --bg: #0c0c14; --surface: #13131f; --surface2: #1a1a2e;
    --border: #2a2a42; --accent: #6c63ff; --text: #e8e8f8; --muted: #6666aa;
}

[data-testid="stAppViewContainer"] { background: var(--bg) !important; }
[data-testid="stHeader"] { display: none !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

.custom-header {
    padding: 14px 24px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    display: flex;
    align-items: center;
    gap: 10px;
}
.logo { font-size: 1.1rem; font-weight: 700; color: var(--text) !important; }
.logo span { color: var(--accent) !important; }
.badge {
    background: linear-gradient(135deg, var(--accent), #ff6584);
    color: white !important;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 99px;
}

.sec-label {
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--muted) !important;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin: 16px 0 8px 0;
    display: block;
}
.sec-label:first-child { margin-top: 0; }

.stTextArea textarea, .stTextInput input {
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-size: 0.85rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent) !important;
}

.stRadio > div {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 6px !important;
}
.stRadio > div > label {
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 10px 6px !important;
    text-align: center !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    margin: 0 !important;
}
.stRadio > div > label:hover {
    border-color: var(--accent) !important;
    transform: translateY(-1px) !important;
}
.stRadio > div > label:has(input:checked) {
    background: rgba(108,99,255,0.15) !important;
    border-color: var(--accent) !important;
}
.stRadio > div > label > div {
    font-size: 0.7rem !important;
    color: var(--text) !important;
    font-weight: 500 !important;
}

.stSlider > div > div > div {
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent) 100%) !important;
}
.stSlider > div > div > div > div {
    background: white !important;
    border: 3px solid var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(108,99,255,0.3) !important;
}

.stCheckbox {
    margin: 6px 0 !important;
}
.stCheckbox > label {
    font-size: 0.8rem !important;
    color: var(--text) !important;
}
.stCheckbox > label > div:first-child {
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 4px !important;
}
.stCheckbox > label > div:first-child[data-checked="true"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #6c63ff, #9c63ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    padding: 13px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(108,99,255,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(108,99,255,0.4) !important;
}

.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 22px;
    line-height: 1.9;
    font-size: 0.86rem;
    white-space: pre-wrap;
    color: #cccce0 !important;
    margin-bottom: 12px;
}

.stat-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px;
    text-align: center;
}
.stat-num {
    font-size: 1rem;
    font-weight: 700;
    color: var(--accent) !important;
}
.stat-label {
    font-size: 0.68rem;
    color: var(--muted) !important;
    margin-top: 2px;
}

.stDivider {
    border-color: var(--border) !important;
    margin: 10px 0 !important;
}

h1,h2,h3,p,div,label,span { color: var(--text) !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
""", unsafe_allow_html=True)

def get_api_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except:
        pass
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)["anthropic"]["api_key"]
    except:
        return None

st.markdown("""
<div class="custom-header">
    <div class="logo"><span>AI</span> 콘텐츠 생성기</div>
    <div class="badge">✦ 말투 학습 + 웹 검색</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2.5])

with col1:
    st.markdown('<span class="sec-label">✦ 말투 학습</span>', unsafe_allow_html=True)
    style = st.text_area("샘플", placeholder="내 글 샘플 붙여넣기", height=100, label_visibility="collapsed")
    
    st.divider()
    st.markdown('<span class="sec-label">🔍 주제</span>', unsafe_allow_html=True)
    topic = st.text_input("주제", placeholder="예: 다이소 무선 랜카드", label_visibility="collapsed")
    
    st.divider()
    st.markdown('<span class="sec-label">📱 플랫폼</span>', unsafe_allow_html=True)
    plat = st.radio("플랫폼", ["📝 블로그","🧵 쓰레드","✖ X","📸 인스타","🎬 유튜브","✉️ 뉴스레터"], label_visibility="collapsed")
    
    st.divider()
    st.markdown('<span class="sec-label">🎙️ 말투</span>', unsafe_allow_html=True)
    tone = st.select_slider("말투", [0,25,50,75,100], 50,
        format_func=lambda x:["😊친근","😄캐주얼","🤝균형","📘전문","🎩격식"][x//25],
        label_visibility="collapsed")
    
    st.markdown('<span class="sec-label">📏 글자수</span>', unsafe_allow_html=True)
    wc = st.select_slider("글자수", [300,800,1500,2500], 800,
        format_func=lambda x:f"{x}자",
        label_visibility="collapsed")
    
    st.divider()
    st.markdown('<span class="sec-label">⚙️ 옵션</span>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        emoji = st.checkbox("이모지", True)
        tag = st.checkbox("해시태그", True)
    with c2:
        img = st.checkbox("이미지", True)
        nxt = st.checkbox("다음편", False)
    
    st.divider()
    gen = st.button("✦ 생성하기", use_container_width=True)

with col2:
    st.markdown('<span class="sec-label">생성된 콘텐츠</span>', unsafe_allow_html=True)
    
    if gen:
        if not topic:
            st.warning("주제를 입력해주세요!")
        else:
            api = get_api_key()
            if not api:
                st.error("API 키를 확인해주세요!")
            else:
                client = anthropic.Anthropic(api_key=api)
                plat_map = {"📝 블로그":"블로그","🧵 쓰레드":"쓰레드","✖ X":"X","📸 인스타":"인스타","🎬 유튜브":"유튜브","✉️ 뉴스레터":"뉴스레터"}
                tone_map = {0:"친근",25:"캐주얼",50:"균형",75:"전문",100:"격식"}
                
                opts = []
                if emoji: opts.append("이모지")
                if tag: opts.append("해시태그")
                if img: opts.append("이미지")
                if nxt: opts.append("예고")
                
                sys = f"""블로그 작성.
규칙: 플랫폼={plat_map[plat]}, 말투={tone_map[tone]}, {wc}자, 옵션={','.join(opts)}
{"말투샘플:"+style[:800] if style and len(style)>50 else ""}
웹검색으로 최신정보."""
                
                qs = []
                res = ""
                
                with st.status("작성 중...", expanded=True) as st_:
                    st.write("🔍 검색...")
                    r = client.messages.create(
                        model="claude-sonnet-4-5-20250929",
                        max_tokens=4096,
                        system=sys,
                        tools=[{"type":"web_search_20250305","name":"web_search"}],
                        messages=[{"role":"user","content":f'"{topic}" 콘텐츠 웹검색 후 작성'}]
                    )
                    
                    for b in r.content:
                        if b.type=="tool_use" and b.name=="web_search":
                            q = b.input.get("query","")
                            qs.append(q)
                            st.write(f"🔎 {q}")
                    
                    st.write("✍️ 작성...")
                    for b in r.content:
                        if hasattr(b,"text"):
                            res += b.text
                    
                    if r.stop_reason=="tool_use":
                        m = [
                            {"role":"user","content":f'"{topic}" 콘텐츠 웹검색 후 작성'},
                            {"role":"assistant","content":r.content},
                            {"role":"user","content":[{"type":"tool_result","tool_use_id":b.id,"content":"완료"} for b in r.content if b.type=="tool_use"]}
                        ]
                        r2 = client.messages.create(model="claude-sonnet-4-5-20250929",max_tokens=4096,system=sys,messages=m)
                        res = "".join(b.text for b in r2.content if hasattr(b,"text"))
                    
                    st_.update(label="✅ 완료!", state="complete")
                
                st.session_state["res"] = res.strip()
                st.session_state["qs"] = qs
    
    if "res" in st.session_state:
        res = st.session_state["res"]
        qs = st.session_state.get("qs",[])
        
        if qs:
            st.info(f"✦ 검색: {', '.join(qs)}")
        
        st.markdown(f'<div class="result-card">{res.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
        
        c1,c2,c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{len(res):,}</div><div class="stat-label">글자수</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{plat_map.get(plat,"블로그")}</div><div class="stat-label">플랫폼</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-box"><div class="stat-num">{"학습" if style else "기본"}</div><div class="stat-label">말투</div></div>', unsafe_allow_html=True)
        
        bc1,bc2 = st.columns(2)
        with bc1:
            st.download_button("⬇️ 저장", res, f"{datetime.now().strftime('%m%d')}_{topic[:10]}.txt", use_container_width=True)
        with bc2:
            if st.button("🔄 다시", use_container_width=True):
                del st.session_state["res"]
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center;padding:100px 0;color:#6666aa">
            <div style="font-size:3rem">✦</div>
            <div style="font-size:0.88rem;margin-top:14px;line-height:1.7">
                주제를 입력하고<br>생성 버튼을 눌러보세요!
            </div>
        </div>
        """, unsafe_allow_html=True)
