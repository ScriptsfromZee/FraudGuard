"""
FraudGuard — app.py
"""

import streamlit as st
from groq import Groq

# ── Page config (must be the FIRST Streamlit call in the file) ─────────────────
st.set_page_config(
    page_title="FraudGuard",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── Load external CSS ──────────────────────────────────────────────────────────
def load_css(path: str) -> None:
    """Read a CSS file from disk and inject it into the Streamlit page."""
    with open(path, "r", encoding="utf-8") as fh:
        st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# ── Validate secrets on startup ────────────────────────────────────────────────
# This runs every time the page loads. If the key is missing, the user sees
# a clear error immediately instead of a confusing crash mid-conversation.
if "GROQ_API_KEY" not in st.secrets:
    st.error(
        "Setup error: GROQ_API_KEY is not set in Streamlit secrets. "
        "Go to your Streamlit app settings > Secrets and add:\n\n"
        "GROQ_API_KEY = \"your-key-here\""
    )
    st.stop()

# ── Groq client — created ONCE and cached for the app lifetime ─────────────────
# BUG FIX: In the previous version, Groq() was called inside the if prompt block,
# which means a new client object was created on every single message.
# @st.cache_resource fixes this — the client is built once on first load and
# then reused for every user and every message for the lifetime of the app.
@st.cache_resource
def get_groq_client() -> Groq:
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

client = get_groq_client()

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are FraudGuard, an AI-powered fraud detection and awareness
assistant built specifically to help Nigerians identify financial scams and AI-enabled fraud.
You speak in plain, friendly, easy-to-understand English.

YOUR PURPOSE:
Help ordinary Nigerians — including elderly people, market traders, job seekers, and anyone
without a technology background — to identify whether a message, call, offer, video, or
situation they have encountered is likely to be a scam.

WHO YOU SERVE:
People who may not be tech-savvy. Never use jargon. Never assume the person knows what
deepfake or phishing means unless they use those words first. Always explain simply.

WHAT YOU CAN DO:
1. ANALYSE suspicious messages — text, WhatsApp, email, or letters
2. ANALYSE suspicious calls — phone calls matching voice cloning or impersonation patterns
3. ANALYSE suspicious job offers — fake job scams, upfront payment demands, vague companies
4. ANALYSE suspicious investments — fake platforms, deepfake celebrity endorsements
5. EDUCATE — explain scam types simply with Nigerian examples
6. ADVISE — if someone has already been scammed, give calm clear next steps

HOW TO RESPOND — always in this order:
1. Start with a clear verdict in ONE sentence: This looks like a scam, This is likely
   genuine, or This has some warning signs — be careful.
2. List the specific red flags (or reasons it looks genuine) in simple bullet points.
3. Give one clear piece of advice on what the person should do next.
4. End with an encouraging line — remind the person that asking is the right thing to do.

TONE:
- Warm, calm, and supportive — never make the person feel foolish
- Simple and direct — no long paragraphs, no unexplained technical words
- Nigerian-aware — you know CBN, GTBank, Zenith, Access, UBA, EFCC, INEC, NNPC,
  Dangote, NIBSS, BVN, NIN, USSD codes, mobile money patterns
- Never alarming or panicking — stay calm even in serious situations

THINGS YOU WILL NEVER DO:
- Ask for personal financial details, account numbers, or passwords
- Give legal advice or tell someone they have a legal case
- Guarantee that something is 100% safe — always encourage caution
- Shame or blame anyone for being scammed — fraud happens to smart people too"""

# ── Available models ───────────────────────────────────────────────────────────
MODELS = {
    "Llama 3.3 70B — Best quality (recommended)": "llama-3.3-70b-versatile",
    "Llama 3.1 8B — Fastest responses":           "llama-3.1-8b-instant",
    "Gemma 2 9B — Google's model":                "gemma2-9b-it",
    "Mixtral 8x7B — Good balance":                "mixtral-8x7b-32768",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ FraudGuard")
    st.markdown("---")

    st.markdown("""
    <div class="sidebar-card">
      <h4>Choose AI Model</h4>
      <p>All models are free. Switch anytime — your chat history stays.</p>
    </div>
    """, unsafe_allow_html=True)

    selected_model_name = st.selectbox(
        label="AI Model",
        options=list(MODELS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    selected_model_id = MODELS[selected_model_name]

    st.markdown(
        f'<div class="model-badge">Running: {selected_model_id}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("""
    <div class="sidebar-card">
      <h4>What I Can Check</h4>
      <ul>
        <li>Suspicious text / WhatsApp messages</li>
        <li>Fake phone calls from banks</li>
        <li>Investment opportunities</li>
        <li>Job offers that seem too good</li>
        <li>Celebrity endorsement videos</li>
        <li>Requests to send money</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
      <h4>Already Scammed?</h4>
      <p>
        Report to EFCC: efcc.gov.ng<br>
        Report to your bank immediately<br>
        Call NIBSS: 07002255677
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
      <h4>About</h4>
      <p>
        Built by Derek Chizogam<br>
        Always free<br>
        No data is stored or shared
      </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Clear chat history", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main area — hero + tip bar ─────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-icon">🛡️</div>
  <div>
    <p class="hero-title">FraudGuard</p>
    <p class="hero-sub">
      Your free AI-powered fraud detection assistant
      &nbsp;·&nbsp; No sign-up required &nbsp;·&nbsp; Always free
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Session state: chat history ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add greeting on first load or after clearing
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hello! I am FraudGuard, your personal fraud detection assistant. "
            "I am here to help you check if a message, call, job offer or investment "
            "opportunity is real or a scam.\n\n"
            "Just describe or paste what you received and I will tell you honestly what "
            "I think. No question is too small. How can I help you today?"
        ),
    })

# ── Render chat history ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Handle new user input ──────────────────────────────────────────────────────
if prompt := st.chat_input("Describe the suspicious message, call, or offer here..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking..."):
            try:
                response = client.chat.completions.create(
                    model=selected_model_id,
                    messages=(
                        [{"role": "system", "content": SYSTEM_PROMPT}]
                        + [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ]
                    ),
                    max_tokens=900,
                    temperature=0.4,
                )
                reply = response.choices[0].message.content

            except Exception as exc:
                reply = (
                    f"Something went wrong: {exc}\n\n"
                    "Please try again, or switch to a different model in the sidebar."
                )

        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})