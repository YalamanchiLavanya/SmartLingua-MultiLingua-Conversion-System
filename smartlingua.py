# smartlingua.py
import streamlit as st
from googletrans import Translator
from gtts import gTTS
import tempfile
import io
import fitz
import docx
import speech_recognition as sr
import os

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="SmartLingua",
    page_icon="🌍",
    layout="wide"
)

# ---------------------------
# Persistent Credentials Setup
# ---------------------------
CREDENTIALS_FILE = "credentials.txt"

# Default credentials
default_username = "admin"
default_password = "1234"
default_hero = "dad"
default_place = "srikakulam"

# Read credentials from file or use default
if os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, "r") as f:
        lines = f.read().splitlines()
        if len(lines) >= 4:
            username = lines[0].strip()
            password = lines[1].strip()
            hero = lines[2].strip()
            place = lines[3].strip()
        else:
            username = default_username
            password = default_password
            hero = default_hero
            place = default_place
else:
    username = default_username
    password = default_password
    hero = default_hero
    place = default_place

# Track last set password
if "last_password" not in st.session_state:
    st.session_state.last_password = password

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ---------------------------
# Authentication Page
# ---------------------------
if not st.session_state.authenticated:
    # Background for authentication page
    auth_bg = """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
        url("https://images.unsplash.com/photo-1522202176988-66273c2fd55f?fit=crop&w=800&h=600");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.7);
    }
    h1, h2, h3, h4, h5, h6, p, div, label {
        color: white !important;
    }
    </style>
    """
    st.markdown(auth_bg, unsafe_allow_html=True)

    # Centered heading
    st.markdown(
        """
        <div style="text-align:center; margin-top:50px;">
            <h1>🔒 SmartLingua Access</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Columns to center the login area
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_set, tab_forget = st.tabs(["Login", "Set Credentials", "Forget Credentials"])

        # -------- Login Tab --------
        with tab_login:
            input_username = st.text_input("Enter Username:")
            input_password = st.text_input("Enter Password:", type="password")
            if st.button("Unlock"):
                if input_username == username and input_password == password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password")

        # -------- Set Credentials Tab --------
        with tab_set:
            st.info("Set a new username, password and security questions")
            new_username = st.text_input("New Username:")
            new_pass = st.text_input("New Password:", type="password")
            confirm_pass = st.text_input("Confirm Password:", type="password")
            new_hero = st.text_input("Your Favorite Hero (Security Question):")
            new_place = st.text_input("Your Favorite Place (Security Question):")
            if st.button("Set Credentials"):
                if new_username and new_pass and new_pass == confirm_pass and new_hero and new_place:
                    with open(CREDENTIALS_FILE, "w") as f:
                        f.write(new_username + "\n")
                        f.write(new_pass + "\n")
                        f.write(new_hero + "\n")
                        f.write(new_place + "\n")
                    username = new_username
                    password = new_pass
                    hero = new_hero
                    place = new_place
                    st.session_state.last_password = new_pass
                    st.success("✅ Credentials and security questions updated successfully!")
                else:
                    st.error("❌ Fill all fields and ensure passwords match")

        # -------- Forget Credentials Tab --------
        with tab_forget:
            st.info("Recover credentials by answering security questions")
            f_hero = st.text_input("Your Favorite Hero:")
            f_place = st.text_input("Your Favorite Place:")
            if st.button("Recover Credentials"):
                if f_hero.strip().lower() == hero.strip().lower() and f_place.strip().lower() == place.strip().lower():
                    # Restore last password
                    password = st.session_state.last_password
                    with open(CREDENTIALS_FILE, "w") as f:
                        f.write(username + "\n")
                        f.write(password + "\n")
                        f.write(hero + "\n")
                        f.write(place + "\n")
                    st.success(f"✅ Correct! Your credentials are:\n**Username:** {username}\n**Password:** {password}")
                else:
                    st.error("❌ Incorrect answers to security questions")

# ---------------------------
# Main SmartLingua App (after unlock)
# ---------------------------
if st.session_state.authenticated:

    # Background image for main app
    page_bg = """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
        url("https://media.licdn.com/dms/image/v2/D4E12AQG8PurrlpiBgA/article-cover_image-shrink_720_1280/B4EZcci0ntHYAI-/0/1748530587429?e=2147483647&v=beta&t=ofXhzDi4_V_DZyD8E-95bM6xBiJw_8DH2225HjdnQjw");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.9);
    }
    h1, h2, h3, h4, h5, h6, p, div, label {
        color: white !important;
    }
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

    translator = Translator()

    # ---------------------------
    # Supported Languages
    # ---------------------------
    LANGUAGES = {
        "en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil", "kn": "Kannada",
        "ml": "Malayalam", "mr": "Marathi", "gu": "Gujarati", "pa": "Punjabi", "bn": "Bengali",
        "ur": "Urdu", "or": "Odia", "as": "Assamese", "ne": "Nepali", "si": "Sinhala",
        "fr": "French", "de": "German", "es": "Spanish", "it": "Italian", "pt": "Portuguese",
        "ru": "Russian", "ar": "Arabic", "tr": "Turkish", "nl": "Dutch", "sv": "Swedish",
        "pl": "Polish", "no": "Norwegian", "da": "Danish", "fi": "Finnish", "uk": "Ukrainian",
        "ro": "Romanian", "hu": "Hungarian", "cs": "Czech", "sk": "Slovak", "el": "Greek",
        "zh-cn": "Chinese (Simplified)", "zh-tw": "Chinese (Traditional)", "ja": "Japanese",
        "ko": "Korean", "th": "Thai", "vi": "Vietnamese", "id": "Indonesian", "ms": "Malay",
        "tl": "Filipino", "he": "Hebrew", "fa": "Persian", "sw": "Swahili"
    }

    # ---------------------------
    # Helper Functions
    # ---------------------------
    def text_to_speech(text, lang):
        tts = gTTS(text=text, lang=lang)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes

    def read_pdf(file):
        text = ""
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            text += page.get_text()
        return text

    def read_docx(file):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    def speech_to_text_live():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Speak now...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        try:
            return recognizer.recognize_google(audio)
        except:
            return "⚠️ Could not process audio"

    def speech_file_to_text(uploaded_file):
        recognizer = sr.Recognizer()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_path = temp_file.name
        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            return "⚠️ Could not process audio file"

    # ---------------------------
    # UI
    # ---------------------------
    st.title("🌍 SmartLingua: Multilingual Conversion System")

    mode = st.sidebar.selectbox(
        "Select Conversion Mode",
        [
            "Text → Text",
            "Text → Speech",
            "Document → Text",
            "Document → Speech",
            "Speech → Text (Mic)",
            "Speech → Speech (Mic)",
            "Voice File → Text",
            "Voice File → Speech"
        ]
    )

    target_lang = st.sidebar.selectbox(
        "Select Target Language",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x]
    )

    # ---------------------------
    # All Conversion Modes
    # ---------------------------
    # TEXT → TEXT
    if mode == "Text → Text":
        text_input = st.text_area("Enter Text")
        if st.button("Translate"):
            if text_input.strip():
                result = translator.translate(text_input, dest=target_lang)
                translated = result.text
                st.success(translated)
                st.download_button("⬇️ Download Text", translated,
                                   file_name="translated_text.txt",
                                   mime="text/plain")

    # TEXT → SPEECH
    elif mode == "Text → Speech":
        text_input = st.text_area("Enter Text")
        if st.button("Translate & Speak"):
            if text_input.strip():
                result = translator.translate(text_input, dest=target_lang)
                translated = result.text
                st.success(translated)
                audio_bytes = text_to_speech(translated, target_lang)
                st.audio(audio_bytes)
                st.download_button("⬇️ Download Audio", audio_bytes,
                                   file_name="translated_audio.mp3",
                                   mime="audio/mp3")

    # DOCUMENT → TEXT
    elif mode == "Document → Text":
        uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
        if uploaded_file:
            text = read_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else read_docx(uploaded_file)
            result = translator.translate(text, dest=target_lang)
            translated = result.text
            st.success(translated)
            st.download_button("⬇️ Download Text", translated,
                               file_name="translated_text.txt",
                               mime="text/plain")

    # DOCUMENT → SPEECH
    elif mode == "Document → Speech":
        uploaded_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
        if uploaded_file:
            text = read_pdf(uploaded_file) if uploaded_file.type == "application/pdf" else read_docx(uploaded_file)
            result = translator.translate(text, dest=target_lang)
            translated = result.text
            st.success(translated)
            audio_bytes = text_to_speech(translated, target_lang)
            st.audio(audio_bytes)
            st.download_button("⬇️ Download Audio", audio_bytes,
                               file_name="translated_audio.mp3",
                               mime="audio/mp3")

    # SPEECH → TEXT (MIC)
    elif mode == "Speech → Text (Mic)":
        placeholder = st.empty()
        if st.button("Start Listening"):
            text = speech_to_text_live()
            placeholder.text(f"🗣 You said: {text}")
            if text != "⚠️ Could not process audio":
                result = translator.translate(text, dest=target_lang)
                translated = result.text
                st.success(f"✅ Translated: {translated}")
                st.download_button("⬇️ Download Text", translated,
                                   file_name="translated_text.txt",
                                   mime="text/plain")

    # SPEECH → SPEECH (MIC)
    elif mode == "Speech → Speech (Mic)":
        placeholder = st.empty()
        if st.button("Start Listening"):
            text = speech_to_text_live()
            placeholder.text(f"🗣 You said: {text}")
            if text != "⚠️ Could not process audio":
                result = translator.translate(text, dest=target_lang)
                translated = result.text
                st.success(f"✅ Translated: {translated}")
                audio_bytes = text_to_speech(translated, target_lang)
                st.audio(audio_bytes)
                st.download_button("⬇️ Download Audio", audio_bytes,
                                   file_name="translated_audio.mp3",
                                   mime="audio/mp3")

    # VOICE FILE → TEXT
    elif mode == "Voice File → Text":
        uploaded_file = st.file_uploader("Upload Audio File (wav or mp3)", type=["wav", "mp3"])
        if uploaded_file:
            text = speech_file_to_text(uploaded_file)
            result = translator.translate(text, dest=target_lang)
            translated = result.text
            st.success(translated)
            st.download_button("⬇️ Download Text", translated,
                               file_name="translated_text.txt",
                               mime="text/plain")

    # VOICE FILE → SPEECH
    elif mode == "Voice File → Speech":
        uploaded_file = st.file_uploader("Upload Audio File (wav or mp3)", type=["wav", "mp3"])
        if uploaded_file:
            text = speech_file_to_text(uploaded_file)
            result = translator.translate(text, dest=target_lang)
            translated = result.text
            st.success(translated)
            audio_bytes = text_to_speech(translated, target_lang)
            st.audio(audio_bytes)
            st.download_button("⬇️ Download Audio", audio_bytes,
                               file_name="translated_audio.mp3",
                               mime="audio/mp3")


#streamlit run smartlingua.py