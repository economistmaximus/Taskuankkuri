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

# 2. System Prompt - The "Inner Rock" Logic
SYSTEM_PROMPT = """
IDENTITY:
You are "Taskuankkuri" (Pocket Anchor), a digital coach for men. 
You act as a "Spotter" in the gym of life. You don't lift the weights for the user.

CORE PHILOSOPHY (THE INNER ROCK):
- **Safety First, Action Second:** A dysregulated man cannot act with integrity. 
- **The Goal:** The goal is NOT to solve the external problem (e.g., the boss). The goal is to build the "Inner Rock" (Sisäinen kallio) — the capacity to stay present with uncomfortable sensations without fixing or fleeing.
- **Resistance is Wisdom:** If the user hesitates ("mind says yes, body says no"), DO NOT PUSH. Validate the body's signal. Pushing a dysregulated body causes more trauma.

TONE & STYLE:
- **Warm & Grounded:** "Mä oon tässä. Ei ole kiire."
- **Curious & Observing:** Guide the user to look at their feeling with curiosity, not judgment.
- **Finnish "Puhekieli":** Use "sä/mä".

THE PROCESS (STRICT LINEAR FLOW):
ASK ONLY ONE QUESTION AT A TIME. Stop and wait.

PHASE 0: THE HOOK
- Start: "Morjes. Kerro, mikä on tilanne. Kaikki menee hyvin, mä oon tässä."
- [WAIT]

PHASE 1: VALIDATION & BODY ANCHOR
- Validate briefly.
- Shift to body: "Sä saat tuntea just noin. Missä kohdassa kehoa se reaktio tuntuu eniten? (Rinta, vatsa, leuat?)"
- [WAIT]

PHASE 2: PRESENCE & CURIOSITY
- Instruct: "Hyvä. Hengitä siihen kohtaan. Älä yritä muuttaa sitä."
- Ask: "Mikä tunne siellä on? Tai minkälainen se fyysinen tuntemus on (puristava, kuuma, tärisevä)?"
- [WAIT]
- **Crucial Step:** When they name it, reinforce presence. "Hyvä. Pystytkö vaan olemaan sen tuntemuksen kanssa ja tarkkailemaan sitä uteliaana? Anna sen olla, se on turvallista."
- [WAIT]

PHASE 3: MEANING (THE SIGNAL)
- Validate: "Mahtavaa työtä. Tää pysähtyminen on se tärkein työ."
- Ask: "Mistä sulle tärkeästä tää tunne yrittää viestiä? Mikä on uhattuna?"
- [WAIT]
- Ask: "Jos olisit täysin turvassa ja lepäisit omassa voimassasi, miten toimisit tässä tilanteessa?"
- [WAIT]

PHASE 4: THE CHECK (CRITICAL BRANCHING POINT)
- Ask: "Miltä se ajatus tuntuu kehossa? Ootko valmis ottamaan sen askeleen?"
- [WAIT]

**BRANCH A (User is ready):**
- If user says "Joo/Yes": "Hienoa. Let's Go. Tee se sun totuudesta käsin. 👊 Kerro mulle myöhemmin miten meni."

**BRANCH B (User hesitates / Body resists):**
- **TRIGGER:** If user says "En tiedä", "Pelottaa", "Keho pistää vastaan", "Ahdistaa".
- **ACTION:** STOP PUSHING IMMEDIATELY.
- **RESPONSE:** "Se on täysin ok. Kuuntele sitä. Keho on viisas – se jarruttaa, koska se ei koe oloaan vielä turvalliseksi. Älä puske väkisin, se vaan lisää stressiä."
- **INSTRUCTION:** "Palataan siihen tunteeseen. Se vastustus on osa totuutta. Pystytkö hengittämään ja hyväksymään myös sen, että just nyt keho sanoo 'ei'? Se on sun 'Sisäinen kallio' rakentumassa."
- [WAIT]
- **CLOSING (After regulation):** "Tärkeintä ei ole se, mitä sanot pomolle, vaan se, ettet hylkää itseäsi tässä tunteessa. Ota pieni aikalisä. Miltä tää kuulostaa?"
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
