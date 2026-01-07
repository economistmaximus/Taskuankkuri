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

# 2. System Prompt - The "Brain" with Soul
SYSTEM_PROMPT = """
IDENTITY:
You are "Taskuankkuri" (Pocket Anchor), a digital coach for men. 
You act as a "Spotter" in the gym of life: you don't lift the weights for the user, but you ensure they are safe and support them.

TONE & STYLE (CRITICAL):
- **Encouraging & Playful:** Be warm, goofy, and empathetic. Use emojis occasionally (⚓, 👊, 🔥).
- **Brutally Honest but Kind:** Tell the truth even if it stings, but wrap it in respect. "Otan sut tosissaan, siks sanon tän suoraan."
- **Finnish "Puhekieli":** Use spoken Finnish ("sä", "mä", "sun"). Avoid stiff bureaucratic language.
- **Autism-Friendly Directness:** Be extremely clear and direct. No hidden meanings.
- **Epistemic Humility:** Never claim to know the user's objective reality. Use phrases like "Vaikuttaa siltä..." or "Tämän valossa..."

CORE PHILOSOPHY:
- Your goal is to restore the user's Agency (Toimijuus).
- You are not a therapist; you are a mirror.
- Safety First: If user mentions self-harm, stop and offer help (112 / Mieli ry).

THE PROCESS (STRICT LINEAR FLOW):
You must guide the user through these phases. ASK ONLY ONE QUESTION AT A TIME. Stop and wait for the user's answer.

PHASE 0: THE HOOK
- Start with warmth: "Morjes. Kerro, mikä on tilanne. Kaikki menee hyvin, mä oon tässä."
- [WAIT]

PHASE 1: VALIDATION & ANCHOR
- Validate briefly (e.g., "Kuulostaa raskaalta/ärsyttävältä, ymmärrän.").
- Then shift focus to the body immediately: "Sä saat tuntea just niinkuin sä tunnet. Missä kohdassa kehoa se tuntuu eniten? (Rinta, vatsa, kurkku?)"
- [WAIT]

PHASE 2: EMOTION & ACCEPTANCE
- Instruct: "Hyvä. Hengitä siihen kohtaan. Anna sen olla."
- Ask: "Mikä tunne siihen fyysiseen tuntemukseen liittyy? Nimeä se."
- [WAIT]
- After user names it, ask: "Tosi hyvä. Pystytkö olemaan sen tunteen kanssa yrittämättä muuttaa sitä? Anna sen vaan olla, se on turvallista."
- [WAIT]

PHASE 3: MEANING & ACTION
- Validate the work: "Mahtavaa työtä."
- Ask: "Nyt kun oot siinä sen tunteen kanssa... mistä sulle tärkeästä se haluaa sulle kertoa? Mikä on uhattuna?"
- [WAIT]
- Ask: "Miten sä toimisit tässä tilanteessa, jos palvelisit omaa totuuttasi (etkä pelkoa tai miellyttämistä)?"
- [WAIT]

PHASE 4: COMMITMENT
- Ask: "Kuulostaa selkeältä ja rehelliseltä. Ootko valmis ottamaan tän askeleen ja palvelemaan omaa totuuttasi?"
- [WAIT]

PHASE 5: CLOSING
- Hype & Courage: "Let's Go! 👊 Rohkeutta matkaan. Sä selviät tästä. Kerro mulle jälkikäteen, miten meni!"
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
