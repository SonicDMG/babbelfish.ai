"""An application to translate any language to any other language using Langflow and Streamlit."""
import os
import logging
import streamlit as st
from dotenv import load_dotenv
import coloredlogs
from langflow_runner import LangflowRunner
from listen_and_convert import TranscribeAudio
from components.audio_component import audio_component
from components.elevenlabs_component import elevenlabs_component

# Configure logger
logger = logging.getLogger("BabbelfishLogger")
coloredlogs.install(level='DEBUG', logger=logger, fmt='%(levelname)s %(message)s')

# Load environment variables from .env file
load_dotenv()

FLOW_ID = os.getenv('FLOW_ID')
VOICE_ID = os.getenv('VOICE_ID')
MODEL_ID = os.getenv('MODEL_ID')
LANGUAGE_TO_SPEAK = os.getenv('LANGUAGE_TO_SPEAK')

# -------------- Streamlit app config ---------------
st.set_page_config(page_title="Babbelfish.ai", page_icon="🐠", layout="wide")
logger.info("--- Streamlit start app ---\n\n")

# -------------- Initialize session state variables ---------------
session_vars = {
    "messages": [],
    "transcriber": TranscribeAudio(),
    "is_recording": False,
    "history": [],
    "audio_data": None,
    "detected_language": None,
    "sentiment": None,
    "explanation": None
}

for var, default in session_vars.items():
    if var not in st.session_state:
        st.session_state[var] = default

# -------------- Define Layout ---------------
with st.sidebar:
    st.caption("🚀 A Streamlit translation chatbot powered by Langflow")
    st.image("./static/fish_ear.webp", use_column_width=True)

    language_options = ["English", "Brazilian Portuguese", "French", "Japanese", "Spanish", "Urdu", "Other"]
    selected_option = st.selectbox("Language to translate to", language_options)
    
    if selected_option == "Other":
        st.session_state.language = st.text_input("Please specify the language")
    else:
        st.session_state.language = selected_option

    voice_checkbox = st.checkbox("Enable voice translation", value=True)

    st.text_input("Audio voice for speech (can be a name like 'Nicole' or a voice ID)", value=VOICE_ID, key="voice_id")
    st.selectbox("ElevenLabs.io model (turbo is faster, but less accurate)", [MODEL_ID, "eleven_turbo_v2"], key="model_id")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Detected Language")
        add_detected_language = st.text(st.session_state.detected_language if st.session_state.detected_language else "Not detected yet")
    with col2:
        st.markdown("### Sentiment")
        add_sentiment = st.text(st.session_state.sentiment if st.session_state.sentiment else "Not detected yet")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        add_transcription_start = st.button("Start voice translation")
    with col2:
        add_transcription_stop = st.button("Stop voice translation")

# -------------- Handle button clicks and update session state ---------------
    if add_transcription_start:
        st.session_state.is_recording = True

    if add_transcription_stop:
        st.session_state.is_recording = False

    # Render the audio component
    st.session_state.audio_data = audio_component(is_recording=st.session_state.is_recording)

# Fixed title
st.markdown('<div class="fixed-header"><h1>Babbelfish.ai 💬🐠💬</h1></div>', unsafe_allow_html=True)

# Scrollable container for chat messages
chat_placeholder = st.empty()

# -------------- Render chat messages ---------------
def render_chat():
    """Render chat messages in a scrollable container."""
    with chat_placeholder.container():
        st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            st.chat_message(message['role']).write(message['content'])
        
        st.markdown(
            """
            <script>
            function scrollToBottom() {
                const chatContainer = document.querySelector('.scrollable-container');
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            scrollToBottom();
            </script>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

# Initial render of chat messages
render_chat()

# -------------- Translate speech ---------------
def translate_speech(flow_id: str, message: str, language_to_speak: str) -> dict:
    """
    Translate the given message to the specified language using Langflow.

    :param flow_id: The ID of the Langflow flow.
    :param message: The message to translate.
    :param language_to_speak: The language to translate the message to.
    :return: A dictionary containing the translation and other metadata.
    """
    tweaks = {
        "TextInput-JKRiD": {
            "input_value": f"{language_to_speak}"
        }
    }

    api_key = None

    flow_runner = LangflowRunner(flow_id=flow_id, api_key=api_key, tweaks=tweaks)
    response_json = flow_runner.run_flow(message=message)
    
    results = flow_runner.extract_output_message(response_json)
    return results

def chat_message_write(role: str, content: str):
    """
    Write a chat message to the session state and re-render the chat.

    :param role: The role of the message sender (e.g., "user" or "assistant").
    :param content: The content of the message.
    """
    st.session_state.messages.append({"role": role, "content": content})
    render_chat()  # Re-render chat messages after adding a new message

# -------------- Call chat_and_speak based on input message ---------------
def chat_and_speak(in_message: str):
    """
    Handle chat input, translate it, and update the session state.

    :param in_message: The input message from the user.
    """
    chat_message_write("user", in_message)
    response = translate_speech(FLOW_ID or "", in_message, st.session_state.language)
    translation = response.get('translation', 'No translation found')
    st.session_state.detected_language = response.get('detected_language', 'No detected_language found')
    st.session_state.sentiment = response.get('sentiment', 'No sentiment found')
    st.session_state.explanation = response.get('explanation', 'No sentiment found')

    chat_message_write("assistant", translation)
    st.subheader("Note:")
    st.write(st.session_state.explanation)
    if voice_checkbox:
        elevenlabs_component(text=translation, voice_id=st.session_state.voice_id, model_id=st.session_state.model_id)

    add_detected_language.text(st.session_state.detected_language)
    add_sentiment.text(st.session_state.sentiment)

# -------------- Call transcribe_audio based on updated state ---------------
def transcribe_audio(transcriber: TranscribeAudio, is_recording: bool, language: str = ""):
    """
    Start or stop the transcription process based on the recording state.

    :param transcriber: The TranscribeAudio instance.
    :param language: The language to transcribe.
    :param is_recording: The recording state.
    """
    if is_recording:
        transcriber.start()
        logger.info("Transcribing in %s...", language)
    else:
        transcriber.stop()
        logger.info("Transcription stopped")

if voice_checkbox:
    language = st.session_state.language or ""
    transcribe_audio(st.session_state.transcriber, st.session_state.is_recording, language)

# Process audio if transcriber and audio data are available
if st.session_state.transcriber and st.session_state.audio_data:
    audio_message = st.session_state.transcriber.process_audio(st.session_state.audio_data)
    if audio_message:
        chat_and_speak(audio_message)

# -------------- Start the chat ---------------
if prompt := st.chat_input("Type your message here..."):
    if prompt:
        chat_and_speak(prompt)

if not st.session_state.history:
    INITIAL_BOT_MESSAGE = """
        Hi there, I'm Babbelfish.ai, 
        choose a language from the menu and type something to translate into any language.\n
    """
    st.session_state.history.append({"role": "assistant", "content": INITIAL_BOT_MESSAGE})
    chat_message_write("assistant", INITIAL_BOT_MESSAGE)
