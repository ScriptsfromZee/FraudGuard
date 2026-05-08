import os
import streamlit as st
from groq import Groq

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Jojo",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# BASE64 LOGO
# (KEEP YOUR FULL BASE64 STRING HERE)
# ─────────────────────────────────────────────────────────────
LOGO_B64 = "PASTE_YOUR_EXISTING_BASE64_STRING_HERE"

LOGO_SRC = f"data:image/png;base64,{LOGO_B64}"

# ─────────────────────────────────────────────────────────────
# LOAD CSS SAFELY
# ─────────────────────────────────────────────────────────────
def load_css(path: str) -> None:
    if not os.path.exists(path):
        st.warning(f"CSS file not found: {path}")
        return

    try:
        with open(path, "r", encoding="utf-8") as fh:
            st.markdown(
                f"<style>{fh.read()}</style>",
                unsafe_allow_html=True,
            )
    except Exception as exc:
        st.error(f"Failed to load CSS: {exc}")

load_css("style.css")

# ─────────────────────────────────────────────────────────────
# SECRETS VALIDATION
# ─────────────────────────────────────────────────────────────
if "GROQ_API_KEY" not in st.secrets:
    st.error(
        "Missing GROQ_API_KEY.\n\n"
        "Add it in Streamlit Secrets."
    )
    st.stop()

# ─────────────────────────────────────────────────────────────
# GROQ CLIENT
# ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

client = get_groq_client()

# ─────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are Jojo — an AI-powered fraud detection and awareness assistant
built specifically to help Nigerians identify financial scams and AI-enabled fraud.

Speak in simple, calm, supportive English.

Always:
1. Give a clear verdict
2. Explain warning signs
3. Give next-step advice
4. Encourage the user

Never:
- Ask for passwords
- Ask for bank details
- Shame victims
"""

# ─────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────
MAX_HISTORY_MESSAGES = 10

MODELS = {
    "Llama 3.3 70B · Best quality": "llama-3.3-70b-versatile",
    "Llama 3.1 8B · Fastest": "llama-3.1-8b-instant",
    "Gemma 2 9B · Google model": "gemma2-9b-it",
    "Mixtral 8x7B · Balanced": "mixtral-8x7b-32768",
}

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I am Jojo — your fraud detection assistant.\n\n"
                "Paste any suspicious message, call, investment, "
                "or job offer and I will help you check if it looks dangerous."
            ),
        }
    ]

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown(f"""
    <div class="sb-brand">
      <img src="{LOGO_SRC}" class="sb-logo"/>
      <div>
        <div class="sb-title">Jojo</div>
      </div>
    </div>

    <div class="status-live">System online</div>

    <div class="sb-divider"></div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<p class="sb-label">AI ENGINE</p>',
        unsafe_allow_html=True
    )

    selected_model_name = st.selectbox(
        "Model",
        options=list(MODELS.keys()),
        label_visibility="collapsed",
    )

    selected_model_id = MODELS[selected_model_name]

    st.markdown(
        f'<div class="model-badge">{selected_model_id}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    msg_count = len([
        m for m in st.session_state.messages
        if m["role"] == "user"
    ])

    st.markdown(
        f'<p class="sb-meta">Session scans: <strong>{msg_count}</strong></p>',
        unsafe_allow_html=True,
    )

    if st.button("↺ Clear session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">

    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png"
         class="hero-logo">

    <div>
        <div class="hero-title">
            Jojo<span class="hero-accent">.</span>
        </div>

        <div class="hero-sub">
            AI-powered scam detection for Nigerians
        </div>
    </div>

</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ─────────────────────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────────────────────
prompt = st.chat_input(
    "Paste or describe a suspicious message..."
)

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
    })

    with st.chat_message("user"):
        st.write(prompt)

    reply = ""

    with st.chat_message("assistant"):

        with st.spinner("Scanning..."):

            try:

                recent = st.session_state.messages[
                    -MAX_HISTORY_MESSAGES:
                ]

                response = client.chat.completions.create(
                    model=selected_model_id,
                    messages=(
                        [{"role": "system", "content": SYSTEM_PROMPT}]
                        + [
                            {
                                "role": m["role"],
                                "content": m["content"],
                            }
                            for m in recent
                        ]
                    ),
                    max_tokens=700,
                    temperature=0.4,
                )

                if (
                    response
                    and response.choices
                    and response.choices[0].message
                ):
                    reply = response.choices[0].message.content
                else:
                    reply = (
                        "I could not generate a response. "
                        "Please try again."
                    )

            except Exception as exc:

                err = str(exc).lower()

                if "rate_limit" in err or "429" in err:
                    reply = (
                        "Too many requests right now.\n\n"
                        "Please wait a little and try again."
                    )

                elif "authentication" in err:
                    reply = (
                        "Authentication error.\n\n"
                        "Please verify your API key."
                    )

                else:
                    reply = (
                        "Something went wrong.\n\n"
                        f"Error: {exc}"
                    )

        st.write(reply)

    if reply:
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
        })