
import base64
import streamlit as st
from groq import Groq

# ── Page config — must be the very first Streamlit call ───────────────────────
st.set_page_config(
    page_title="Jojo",
    page_icon="logo_b64.png",  # base64-encoded logo (see below)
    layout="centered",
    initial_sidebar_state="expanded",   # sidebar always open on load
)

# ── Logo (base64-embedded — no file dependency) ───────────────────────────────
LOGO_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCAHCAcIDASIAAhEBAxEB/8QAHQABAAAHAQEAAAAAAAAAAAAAAAECAwQGBwgFCf/EAEgQAAEDAgMFBQUFBgQEBQUAAAEAAgMEEQUGIQcSMUFREyJhcfAIgZGhwRQyQrHRFSMzUmLhJHKC8RZDU6IlJmOSspOjs8LS/8QAGwEBAAIDAQEAAAAAAAAAAAAAAAQFAQMGAgf/xAA0EQACAgECAwQJBQADAQEAAAAAAQIDBAUREiExQVFhsQYTIjJxgZHB0SNCoeHwFFLxFUP/2gAMAwEAAhEDEQA/AOMkREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEWT7PMh5nz7jAw3LeGvqHN1mnf3YYB1e/gPLieQK6qyF7KWVKCGObM1ZXY/VWu+OMmmpgegt33DxuL9AoeTn0Y3Kb593abqsedvurkcXIvpPQ7Hdn1FGG0+QstAdZaNkrufN4J5qxxzYxs3r4JIqvIWDMDzcvpYDA4eRjLSFX/AP3qd+cWSP8AgT7Gj5zIuqNqHssxGOXENnmJODgS44ZiEnEdI5bceOj7cu8uaMyYFjGW8YnwjHsNqcOr4DaSCdha4eI6g8iNDyVnj5dOSt63uRrKZ1vaSPOREUk1BERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREAREQBERAEREARFXoKSqr62Gioaaaqqp3iOKGFhe+RxNg1oGpJ6ICgt0bBdgmObQZYMXxhtRhWWibiYACer8IQRwvxeRbja5BC2r7P8A7M0VI+DH9odOyprGkPhwk2dDFzBmI0e7+gd0c97gOqqOlipo2tjaBYAaC1gOAA5DwVDnauo710de/wDBPpxP3WfQ8PI2TsDyjgFNguC4fFR0UA7kTdbnm5zjq5x5k/ksjAAFhopZpYoWF8sjI2Di5zgAvNkzHgEcvZSYzQNd4ztA+N7ciqBQnY3LZtk1tLkeooEKSnqIKiMyU88crOG8xwcPkpzxXhmSyqaKOXvN7r+vJYhn3JOAZuwr9l5pwiHEKUG8bnXD4j1Y8atPkdeYKzkqVwa4WIBC8xcoS4oPZnvfdbS5o4a2sezLmDBO1xPJEsmPYeLudSOAbVwjjYC9pR4ts7T7q0BUwT0tTJTVMMkE8TiySORpa5jgbEEHUEdF9VqmgabuhIaeh4LXG1TZPlDaBE8Y/hvYYj+DEqVoZUtt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"
LOGO_SRC = f"data:image/png;base64,{LOGO_B64}"

# ── Load CSS ──────────────────────────────────────────────────────────────────
def load_css(path: str) -> None:
    with open(path, "r", encoding="utf-8") as fh:
        st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# ── Secrets check ─────────────────────────────────────────────────────────────
if "GROQ_API_KEY" not in st.secrets:
    st.error(
        "GROQ_API_KEY missing from Streamlit secrets.\n"
        "Settings → Secrets → add:  GROQ_API_KEY = \"your-key-here\""
    )
    st.stop()

# ── Groq client — created once, reused forever ────────────────────────────────
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

# ── Context window cap — prevents Groq free-tier rate limit at ~message 17 ────
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

    # Brand — real logo image + name
    st.markdown(f"""
    <div class="sb-brand">
      <img src="{LOGO_SRC}" class="sb-logo" alt="FraudGuard shield logo"/>
      <div>
        <div class="sb-title">Jojo</div>
        <div class="sb-country"></div>
      </div>
    </div>
    <div class="status-live">System online</div>
    <div class="sb-divider"></div>
    """, unsafe_allow_html=True)

    # Model picker
    st.markdown('<p class="sb-label">AI ENGINE</p>', unsafe_allow_html=True)
    selected_model_name = st.selectbox(
        label="model", options=list(MODELS.keys()),
        index=0, label_visibility="collapsed",
    )
    selected_model_id = MODELS[selected_model_name]
    st.markdown(
        f'<div class="model-badge">▶ {selected_model_id}</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # Scan types
    st.markdown("""
    <p class="sb-label">SCAN TYPES</p>
    <div class="sb-card">
      <div class="sb-item">📱  WhatsApp &amp; text messages</div>
      <div class="sb-item">📞  Suspicious phone calls</div>
      <div class="sb-item">💼  Fake job offers</div>
      <div class="sb-item">📈  Investment scams</div>
      <div class="sb-item">🎥  Deepfake celebrity videos</div>
      <div class="sb-item">💸  Money transfer requests</div>
    </div>
    <div class="sb-divider"></div>
    """, unsafe_allow_html=True)

    # Emergency contacts
    st.markdown("""
    <p class="sb-label">ALREADY SCAMMED?</p>
    <div class="sb-card sb-emergency">
      <div class="sb-erow">
        <span class="sb-etag">EFCC</span>
        <span class="sb-eval">efcc.gov.ng</span>
      </div>
      <div class="sb-erow">
        <span class="sb-etag">NIBSS</span>
        <span class="sb-eval">07002255677</span>
      </div>
      <div class="sb-erow">
        <span class="sb-etag">Bank</span>
        <span class="sb-eval">Call immediately</span>
      </div>
    </div>
    <div class="sb-divider"></div>
    """, unsafe_allow_html=True)

    # Session counter
    msg_count = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    st.markdown(
        f'<p class="sb-meta">Session scans: <strong>{msg_count}</strong></p>',
        unsafe_allow_html=True,
    )

    if st.button("↺  Clear session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("""
    <div class="sb-footer">
      Built by Derek Chizogam <br>
     No data stored
    </div>
    """, unsafe_allow_html=True)

# ── MAIN AREA ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-glow"></div>
  <img src="{LOGO_SRC}" class="hero-logo" alt="Jojo"/>
  <div>
    <div class="hero-title">Jojo </div>
    <div class="hero-sub">
      AI-powered scam detection &nbsp;·&nbsp; Free &nbsp;·&nbsp;
      No sign-up &nbsp;·&nbsp; Built for every Nigerian
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
            "and I will tell you honestly whether it is a scam.\n\n"
            "How can I help you today?"
        ),
    })

# ── Render chat ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── Handle input ──────────────────────────────────────────────────────────────
if prompt := st.chat_input("Paste or describe the suspicious message, call, or offer…"):

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
                        "Too many requests right now — please wait about 30 seconds "
                        "and try again. You can also switch to **Llama 3.1 8B** in the "
                        "sidebar for a higher free-tier limit."
                    )
                else:
                    reply = (
                        f"Something went wrong: {err}\n\n"
                        "Please try again or switch to a different model in the sidebar."
                    )

        st.write(reply)

    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})