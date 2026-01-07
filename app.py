import streamlit as st
from google import genai
from google.genai import types

# Page Config
st.set_page_config(page_title="Taskuankkuri", page_icon="⚓", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .stTextInput > div > div > input {font-size: 16px; padding: 12px;}
    .chat-message {padding: 1.2rem; border-radius: 0.8rem; margin-bottom: 1rem; display: flex; font-family: sans-serif;} 
    .chat-message.user {background-color: #f0f2f6; color: #31333f; justify-content: flex-end;}
    .chat-message.bot {background-color: #e8f4f8; color: #004e66; border-left: 5px solid #004e66;}
    h1 { font-size: 1.8rem; text-align: center; color: #004e66; }
    /* Piilota turhat valikot */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("⚓ Taskuankkuri")

# 1. Alusta uusi Client (Löytämäsi uusi tapa)
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key puuttuu asetuksista.")
    st.stop()

# 2. System Prompt
SYSTEM_PROMPT = """
IDENTITY:
You are "Taskuankkuri" (Pocket Anchor), a digital coach for men. 
Tone: Grounded, Finnish spoken language ("puhekieli"), masculine, calm.

CRITICAL INSTRUCTIONS:
1.  **Linear Flow:** Follow the phases 0-5 strictly.
2.  **Stop Sequence:** Ask ONLY ONE question. Then stop and wait.
3.  **Safety:** If user mentions self-harm, stop and provide emergency contacts (112).

PHASES:
0. Start: "Kerro, mikä on tilanne. Kaikki menee hyvin."
1. Validate -> Ask: "Missä kohdassa kehoa se tuntuu eniten?"
2. Acceptance -> Ask: "Hyvä. Hengitä siihen. Mikä tunne siihen liittyy?" -> Then: "Pystytkö olemaan sen kanssa?"
3. Meaning -> Ask: "Mistä sulle tärkeästä tää tunne kertoo?" -> Then: "Miten toimisit nyt oman totuutesi mukaan?"
4. Commitment -> Ask: "Ootko valmis ottamaan tän askeleen?"
5. Closing -> "Let's Go! Rohkeutta matkaan."
"""

# 3. Session State (Muisti)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Kerro, mikä on tilanne. Kaikki menee hyvin."}
    ]

# 4. Näytä viestihistoria
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="chat-message {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

# 5. Käsittele käyttäjän syöte
if prompt := st.chat_input("Kirjoita tähän..."):
    # A. Näytä käyttäjän viesti
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="chat-message user">{prompt}</div>', unsafe_allow_html=True)

    # B. Muotoile historia uudelle SDK:lle
    # Uusi kirjasto vaatii historian muodossa: [{'role': 'user', 'parts': [{'text': '...'}]}, ...]
    gemini_history = []
    for msg in st.session_state.messages[:-1]: 
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [{"text": msg["content"]}]})

    # C. Kutsu tekoälyä (Uusi Client-tyyli)
    with st.spinner("..."):
        try:
            # Luodaan chat-istunto
            chat = client.chats.create(
                model="gemini-3-flash-preview", # Käytetään tätä vakaata uutta mallia
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                ),
                history=gemini_history
            )
            
            # Lähetä viesti
            response = chat.send_message(prompt)
            msg_content = response.text
            
            # D. Tallenna ja näytä vastaus
            st.session_state.messages.append({"role": "assistant", "content": msg_content})
            st.markdown(f'<div class="chat-message bot">{msg_content}</div>', unsafe_allow_html=True)
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Yhteysvirhe: {e}")
