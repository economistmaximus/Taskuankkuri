import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="Taskuankkuri", page_icon="⚓", layout="centered")

# Custom CSS for Mobile App Feel
st.markdown("""
    <style>
    .stTextInput > div > div > input {font-size: 16px; padding: 12px;}
    .chat-message {padding: 1.2rem; border-radius: 0.8rem; margin-bottom: 1rem; display: flex; font-family: sans-serif;} 
    .chat-message.user {background-color: #f0f2f6; color: #31333f; justify-content: flex-end;}
    .chat-message.bot {background-color: #e8f4f8; color: #004e66; border-left: 5px solid #004e66;}
    h1 { font-size: 1.8rem; text-align: center; color: #004e66; }
    /* Hide Streamlit footer */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("⚓ Taskuankkuri")

# 1. Setup Gemini Client
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key missing. Set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# 2. System Prompt - The Strict Logic
SYSTEM_PROMPT = """
IDENTITY:
You are "Taskuankkuri" (Pocket Anchor), a digital coach for men. 
You are NOT a therapist. You are a 'spotter' in the gym of life.
Tone: Grounded, Finnish spoken language ("puhekieli"), masculine, calm, stoic but warm.

CRITICAL INSTRUCTIONS:
1.  **Linear Flow:** Follow the phases 0-5 strictly.
2.  **Stop Sequence:** Ask ONLY ONE question. Then stop and wait. Never monologue.
3.  **Safety:** If the user mentions self-harm, stop the flow and provide emergency contacts (112 / Mieli ry).

PHASES:
0. Start: "Kerro, mikä on tilanne. Kaikki menee hyvin."
1. Validate -> Ask: "Missä kohdassa kehoa se tuntuu eniten?" (Anchor to body)
2. Acceptance -> Ask: "Hyvä. Hengitä siihen. Mikä tunne siihen liittyy?" -> Then: "Pystytkö olemaan sen kanssa yrittämättä muuttaa sitä?"
3. Meaning -> Ask: "Mistä sulle tärkeästä tää tunne kertoo?" -> Then: "Miten toimisit nyt, jos palvelisit omaa totuuttasi?"
4. Commitment -> Ask: "Ootko valmis ottamaan tän askeleen?"
5. Closing -> "Let's Go! Rohkeutta matkaan. Kerro mulle myöhemmin miten meni."
"""

# 3. Session State (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Kerro, mikä on tilanne. Kaikki menee hyvin."}
    ]

# 4. Render Chat History
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="chat-message {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

# 5. Handle User Input
if prompt := st.chat_input("Kirjoita tähän..."):
    # A. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-message user">{prompt}</div>', unsafe_allow_html=True)

    # B. Format History for Gemini
    gemini_history = []
    for msg in st.session_state.messages[:-1]: 
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # C. Call Gemini
    with st.spinner("..."):
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash", 
                system_instruction=SYSTEM_PROMPT
            )
            
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(prompt)
            msg_content = response.text
            
            # D. Show AI Message
            st.session_state.messages.append({"role": "assistant", "content": msg_content})
            st.markdown(f'<div class="chat-message bot">{msg_content}</div>', unsafe_allow_html=True)
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Yhteysvirhe: {e}")
