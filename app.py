
import streamlit as st
from groq import Groq

# ── Page config — MUST be first Streamlit call ────────────────────────────────
st.set_page_config(
    page_title="Jojo",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded",  
)

# ── Load CSS ──────────────────────────────────────────────────────────────────
def load_css(path: str) -> None:
    with open(path, "r", encoding="utf-8") as fh:
        st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# ── Secrets check ─────────────────────────────────────────────────────────────
if "GROQ_API_KEY" not in st.secrets:
    st.error(
        "GROQ_API_KEY is missing from Streamlit secrets.\n"
        "Settings → Secrets → add:  GROQ_API_KEY = \"your-key-here\""
    )
    st.stop()

# ── Groq client — built once, shared across all users and reruns ──────────────
@st.cache_resource
def get_groq_client() -> Groq:
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

client = get_groq_client()

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Jojo — an AI-powered fraud detection and awareness
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

# ── Context window limit ──────────────────────────────────────────────────────
# Sending the full history causes Groq free-tier token-per-minute limits to
# trigger at ~message 17. Only the last 10 messages are sent to the API.
# The full history is always shown to the user on screen.
MAX_HISTORY_MESSAGES = 10

# ── Models ────────────────────────────────────────────────────────────────────
MODELS = {
    "Llama 3.3 70B  ·  Best quality":  "llama-3.3-70b-versatile",
    "Llama 3.1 8B   ·  Fastest":       "llama-3.1-8b-instant",
    "Gemma 2 9B     ·  Google model":  "gemma2-9b-it",
    "Mixtral 8×7B   ·  Balanced":      "mixtral-8x7b-32768",
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div class="sb-brand">
      <span class="sb-shield">🛡️</span>
      <div>
        <div class="sb-title">FraudGuard</div>
        <div class="sb-sub">Nigeria</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Live status dot
    st.markdown("""
    <div class="status-live">System online</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # Model picker
    st.markdown('<div class="sb-section-label">AI ENGINE</div>', unsafe_allow_html=True)
    selected_model_name = st.selectbox(
        label="model",
        options=list(MODELS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    selected_model_id = MODELS[selected_model_name]
    st.markdown(
        f'<div class="model-badge">▶ {selected_model_id}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # What it can check
    st.markdown("""
    <div class="sb-section-label">SCAN TYPES</div>
    <div class="sb-card">
      <div class="sb-item">📱 WhatsApp &amp; text messages</div>
      <div class="sb-item">📞 Suspicious phone calls</div>
      <div class="sb-item">💼 Fake job offers</div>
      <div class="sb-item">📈 Investment scams</div>
      <div class="sb-item">🎥 Deepfake videos</div>
      <div class="sb-item">💸 Money transfer requests</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # Emergency contacts
    st.markdown("""
    <div class="sb-section-label">ALREADY SCAMMED?</div>
    <div class="sb-card sb-emergency">
      <div class="sb-emergency-row">
        <span class="sb-emergency-label">EFCC</span>
        <span class="sb-emergency-val">efcc.gov.ng</span>
      </div>
      <div class="sb-emergency-row">
        <span class="sb-emergency-label">NIBSS</span>
        <span class="sb-emergency-val">07002255677</span>
      </div>
      <div class="sb-emergency-row">
        <span class="sb-emergency-label">Action</span>
        <span class="sb-emergency-val">Call your bank now</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # Session info
    msg_count = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    st.markdown(
        f'<div class="sb-meta">Session scans: <strong>{msg_count}</strong></div>',
        unsafe_allow_html=True,
    )

    if st.button("↺  Clear session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div class="sb-footer">
      Built by Derek Chizogam<br>
       No data stored
    </div>
    """, unsafe_allow_html=True)

# ── MAIN AREA ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-glow"></div>
  <div class="hero-icon-wrap">🛡️</div>
  <div class="hero-text">
    <div class="hero-title">Jojo <span class="hero-ng">Nigeria</span></div>
    <div class="hero-sub">
      AI-powered scam detection · Free · No sign-up · Built for every Nigerian
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hello! I am Jojo — your personal fraud detection assistant.\n\n"
            "Paste or describe any suspicious message, phone call, job offer, or investment "
            "and I will tell you honestly whether it is a scam, for free.\n\n"
            "How can I help you today?"
        ),
    })

# ── Render chat ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Handle input ──────────────────────────────────────────────────────────────
if prompt := st.chat_input("Paste or describe the suspicious message, call or offer…"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    reply = ""  # always defined before try/except

    with st.chat_message("assistant"):
        with st.spinner("Scanning…"):
            recent = st.session_state.messages[-MAX_HISTORY_MESSAGES:]
            try:
                response = client.chat.completions.create(
                    model=selected_model_id,
                    messages=(
                        [{"role": "system", "content": SYSTEM_PROMPT}]
                        + [{"role": m["role"], "content": m["content"]} for m in recent]
                    ),
                    max_tokens=900,
                    temperature=0.4,
                )
                reply = response.choices[0].message.content

            except Exception as exc:
                err = str(exc)
                if "429" in err or "rate_limit" in err.lower():
                    reply = (
                        "I am receiving too many requests right now — please wait "
                        "about 30 seconds and try again. You can also switch to "
                        "**Llama 3.1 8B** in the sidebar; it has a higher free-tier "
                        "request limit."
                    )
                else:
                    reply = (
                        f"Something went wrong ({err}). "
                        "Please try again or switch to a different model in the sidebar."
                    )

        st.write(reply)

    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})