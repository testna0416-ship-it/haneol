import time
from langdetect import DetectorFactory, detect
from groq import Groq
import streamlit as st

DetectorFactory.seed = 0

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="HANEOL AI",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 세션 상태에 테마 초기화
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# 사이드바 테마 전환 컨트롤
with st.sidebar:
    st.title("🧭 HANEOL AI")
    st.caption("본질 & 맥락 융합 분석기")

    # 다크 모드 스위치
    is_dark = st.toggle("🌙 다크 모드", value=(st.session_state.theme == "Dark"))
    st.session_state.theme = "Dark" if is_dark else "Light"

    st.markdown("---")

    if st.button("🧹 대화내용 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if "messages" in st.session_state and st.session_state.messages:
        chat_text = "\n\n".join(
            [
                f"[{m['role'].upper()}]\n{m['content']}"
                for m in st.session_state.messages
            ]
        )
        st.download_button(
            label="📥 대화 기록 내보내기",
            data=chat_text,
            file_name="haneol_ai_history.txt",
            mime="text/plain",
            use_container_width=True,
        )

# 2. 동적 테마 CSS 적용
if st.session_state.theme == "Dark":
    theme_css = """
    <style>
        /* 메인 배경 */
        .stApp {
            background-color: #3b4252 !important;
            background-image: 
                linear-gradient(to right, #4c566a 1px, transparent 1px),
                linear-gradient(to bottom, #4c566a 1px, transparent 1px) !important;
            background-size: 24px 24px !important;
            color: #ffffff !important;
        }

        /* 헤더 투명화 */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* 하단 컨테이너 배경 */
        [data-testid="stBottom"], [data-testid="stBottom"] > div {
            background-color: #3b4252 !important;
            background-image: 
                linear-gradient(to right, #4c566a 1px, transparent 1px),
                linear-gradient(to bottom, #4c566a 1px, transparent 1px) !important;
            background-size: 24px 24px !important;
            border-top: none !important;
        }

        /* 사이드바 기본 */
        [data-testid="stSidebar"] {
            background-color: #2e3440 !important;
            border-right: 1px solid #4c566a !important;
        }
        [data-testid="stSidebar"] *, 
        [data-testid="stSidebar"] div, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1 {
            color: #ffffff !important;
        }

        /* [수정] 지우기/내보내기 버튼 이중 테두리 제거 및 깔끔한 단일 스타일 적용 */
        [data-testid="stSidebar"] div.stButton,
        [data-testid="stSidebar"] div.stDownloadButton {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
        }
        [data-testid="stSidebar"] button {
            background-color: #434c5e !important;
            color: #ffffff !important;
            border: 1px solid #d8dee9 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
            outline: none !important;
        }
        [data-testid="stSidebar"] button * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-weight: 700 !important;
        }

        /* 대화 메시지 카드 */
        [data-testid="stChatMessage"] {
            border-radius: 16px !important;
            padding: 1.1rem 1.3rem !important;
            margin-bottom: 1rem !important;
        }

        /* 사용자 카드 */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            background: #4c566a !important;
            border: 1px solid #d8dee9 !important;
            color: #ffffff !important;
        }

        /* AI 카드 */
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
            background: #2e3440 !important;
            border: 1px solid #d8dee9 !important;
            border-left: 4px solid #88c0d0 !important;
            color: #ffffff !important;
        }

        /* [수정] 입력창 박스 밝게 및 입력 글자색 검은색(#000000) 지정 */
        [data-testid="stChatInput"] {
            background-color: #f8fafc !important;
            border: 2px solid #cbd5e1 !important;
            border-radius: 14px !important;
        }
        
        /* 입력 글자 검은색 강제 적용 */
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] textarea * {
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
        }

        /* 입력 힌트(Placeholder) 글자색 다크 그레이 적용 */
        [data-testid="stChatInput"] textarea::placeholder {
            color: #64748b !important;
            -webkit-text-fill-color: #64748b !important;
            opacity: 1 !important;
        }

        .title-text {
            color: #ffffff !important;
        }

        .sub-badge {
            display: inline-block;
            background: #2e3440;
            color: #ffffff;
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid #d8dee9;
            margin-bottom: 1.5rem;
        }
    </style>
    """
else:
    theme_css = """
    <style>
        .stApp {
            background-color: #f8fafc !important;
            background-image: 
                linear-gradient(to right, #cbd5e1 1px, transparent 1px),
                linear-gradient(to bottom, #cbd5e1 1px, transparent 1px) !important;
            background-size: 24px 24px !important;
            color: #0f172a !important;
        }

        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }

        [data-testid="stBottom"], [data-testid="stBottom"] > div {
            background-color: #f8fafc !important;
            background-image: 
                linear-gradient(to right, #cbd5e1 1px, transparent 1px),
                linear-gradient(to bottom, #cbd5e1 1px, transparent 1px) !important;
            background-size: 24px 24px !important;
        }

        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid #e2e8f0 !important;
        }

        [data-testid="stChatMessage"] {
            border-radius: 16px !important;
            padding: 1.1rem 1.3rem !important;
            margin-bottom: 1rem !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            background: #f1f5f9 !important;
            border: 1px solid #cbd5e1 !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-left: 4px solid #2563eb !important;
            box-shadow: 0 4px 15px rgba(15, 23, 42, 0.04) !important;
        }

        [data-testid="stChatInput"] {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 14px !important;
        }

        .title-text {
            color: #0f172a !important;
        }

        .sub-badge {
            display: inline-block;
            background: #ffffff;
            color: #475569;
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid #cbd5e1;
            margin-bottom: 1.5rem;
        }
    </style>
    """

st.markdown(
    theme_css
    + """
<style>
    .title-container {
        text-align: center;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .title-emoji {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif;
        display: inline-block;
        margin-right: 6px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 3. 타이틀 애니메이션
title_placeholder = st.empty()

if "typed" not in st.session_state:
    typed_text = ""
    for char in "HANEOL AI":
        typed_text += char
        title_placeholder.markdown(
            f"<h1 class='title-container'><span class='title-emoji'>🧭</span><span class='title-text'>{typed_text}▌</span></h1>",
            unsafe_allow_html=True,
        )
        time.sleep(0.06)
    title_placeholder.markdown(
        "<h1 class='title-container'><span class='title-emoji'>🧭</span><span class='title-text'>HANEOL AI</span></h1>",
        unsafe_allow_html=True,
    )
    st.session_state.typed = True
else:
    title_placeholder.markdown(
        "<h1 class='title-container'><span class='title-emoji'>🧭</span><span class='title-text'>HANEOL AI</span></h1>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<div style='text-align: center;'><span class='sub-badge'>본질과 맥락을 가로지르는 입체적 통찰</span></div>",
    unsafe_allow_html=True,
)

# SYSTEM PROMPT
SYSTEM_PROMPT = """You are 'HANEOL', an AI that provides unified, multi-dimensional insights by analyzing both 'independent essence' and 'relational context'.

[INTERNAL REASONING PIPELINE]
Step 1: Capture the nuances and core intent of the user's input directly in the user's language.
Step 2: Cross-verify through Korean and English cognitive structures to eliminate cultural bias and ensure solid logical coherence.
Step 3: Synthesize into a final, natural narrative in the EXACT SAME language used by the user.

[STRICT OUTPUT FORMAT RULES]
1. NO LANGUAGE TAGS: NEVER start or include language labels, tags, or headers such as "(한국어)", "(English)", "[Korean]", or "Korean:". Begin the actual answer DIRECTLY without any preamble.
2. Seamless Transitions: Connect the individual perspective (essence) and environmental perspective (context) smoothly using natural transition words without any artificial breaks.
3. Tone & Format: Calm, refined, clear, and insightful. Write in elegant paragraphs (5 to 12 sentences). Do NOT use bullet points, numbered lists, subheadings, or explicit labels.
4. Casual Interaction: For light greetings, respond naturally with 1-2 friendly sentences.
5. Language: Output ONLY in the user's language."""


def get_loading_message(text):
    try:
        lang = detect(text)
        loading_messages = {
            "ko": "🧭 HANEOL이 생각하고 있어요...",
            "es": "🧭 HANEOL está pensando...",
            "ja": "🧭 HANEOL가考えています...",
            "zh-cn": "🧭 HANEOL 正在思考...",
            "zh-tw": "🧭 HANEOL 正在思考...",
            "fr": "🧭 HANEOL réfléchit...",
            "de": "🧭 HANEOL denkt nach...",
        }
        return loading_messages.get(lang, "🧭 HANEOL is thinking...")
    except Exception:
        return "🧭 HANEOL이 생각하고 있어요..."


# 4. Groq 클라이언트 초기화 (무료 사용량 한도 내에서 완전 무료)
# Streamlit Cloud에서는 앱 설정 > Secrets 에 아래처럼 등록하세요:
# GROQ_API_KEY = "gsk_..."
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL_NAME = "openai/gpt-oss-20b"

if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 출력
for message in st.session_state.messages:
    avatar = "📍" if message["role"] == "user" else "🧭"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 입력 처리
if prompt := st.chat_input("질문이나 고민을 입력해 보세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="📍"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🧭"):
        recent_messages = st.session_state.messages[-10:]
        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]} for m in recent_messages
        ]

        loading_msg = get_loading_message(prompt)

        with st.spinner(loading_msg):
            try:
                def generate_response():
                    stream = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=api_messages,
                        stream=True,
                    )
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            yield delta

                full_response = st.write_stream(generate_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                st.error(
                    f"Groq API 호출 실패! API 키가 올바르게 설정되었는지 확인해 주세요. (에러: {e})"
                )
