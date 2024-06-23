import os
import streamlit as st
from dotenv import load_dotenv
from babbelfish_flow import FlowRunner
from listen_and_convert import TranscribeAudio
from components.audio_component import audio_component
from components.elevenlabs_component import elevenlabs_component

# Load environment variables from .env file
load_dotenv()

FLOW_ID = os.getenv('FLOW_ID')
VOICE_ID = os.getenv('VOICE_ID')
MODEL_ID = os.getenv('MODEL_ID')
LANGUAGE_TO_SPEAK = os.getenv('LANGUAGE_TO_SPEAK')

# -------------- Streamlit app config ---------------
st.set_page_config(page_title="Babbelfish.ai", page_icon="🐠", layout="wide")
print("--- Streamlit start app ---\n\n")

# -------------- Initialize session state variables ---------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "transcriber" not in st.session_state:
    st.session_state.transcriber = TranscribeAudio()

if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

if "history" not in st.session_state:
    st.session_state.history = []

if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

if "detected_language" not in st.session_state:
    st.session_state.detected_language = None

if "sentiment" not in st.session_state:
    st.session_state.sentiment = None

# -------------- Define Layout ---------------
with st.sidebar:
    st.caption("🚀 A Streamlit translation chatbot powered by Langflow")
    st.image("./static/fish_ear.webp", use_column_width=True)

    language_options = ["English", "Brazilian Portuguese", "Finnish", "French", "Japanese", "Spanish", "Urdu", "Californian surfer", "Other"]
    selected_option = st.selectbox("Language to translate to", language_options)
    
    if selected_option == "Other":
        st.session_state.language = st.text_input("Please specify the language")
    else:
        st.session_state.language = selected_option

    st.text_input("Audio voice for speech (can be a name like 'Nicole' or a voice ID)", value=VOICE_ID, key="voice_id")
    st.selectbox("ElevenLabs.io model (turbo is faster, but less accurate)", [MODEL_ID, "eleven_turbo_v2"], key="model_id")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Detected Language")
        add_detected_langauge = st.text(st.session_state.detected_language if st.session_state.detected_language else "Not detected yet")
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

    # -------------- Render the audio component ---------------
    st.session_state.audio_data = audio_component(is_recording=st.session_state.is_recording)

# Fixed title
st.markdown('<div class="fixed-header"><h1>Babbelfish.ai 💬🐠💬</h1></div>', unsafe_allow_html=True)

# Scrollable container for chat messages
chat_placeholder = st.empty()

# -------------- Render chat messages ---------------
def render_chat():
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
def translate_speech(flow_id, message, language_to_speak):
    tweaks = {
        "Prompt-sXFMH": {},
        "GroqModel-eEwav": {
            "stream": True
        },
        "ChatOutput-ZggnW": {},
        "ChatInput-V3zKC": {
            "input_value": f"{message}"
        },
        "TextInput-zSj9q": {
            "input_value": f"{language_to_speak}"
        },
        "TextOutput-rRoEL": {},
        "Prompt-Fa0Cf": {},
        "OpenAIModel-lDBVs": {
            "stream": True
        },
        "Prompt-zX3NP": {},
        "TextOutput-mg3fX": {},
    }

    api_key = None

    flow_runner = FlowRunner(flow_id=flow_id, api_key=api_key, tweaks=tweaks)
    response_json = flow_runner.run_flow(message=message)
    #print(f"Response JSON: {response_json}")
    results = flow_runner.extract_output_message(response_json)
    result1 = results.get('result1', 'No result1 found')
    st.session_state.detected_language = results.get('result2', 'No result2 found')
    st.session_state.sentiment = results.get('result3', 'No result3 found')
    return result1


def chat_message_write(role, content):
    print(f"role: {role}, content: {content}")
    st.session_state.messages.append({"role": role, "content": content})
    render_chat()  # Re-render chat messages after adding a new message


# -------------- Call chat_and_speak based on input message ---------------
def chat_and_speak(in_message):
    chat_message_write("user", in_message)
    response = translate_speech(FLOW_ID, in_message, st.session_state.language)
    chat_message_write("assistant", response)
    elevenlabs_component(text=response, voice_id=st.session_state.voice_id, model_id=st.session_state.model_id)

    add_detected_langauge.text(st.session_state.detected_language)
    add_sentiment.text(st.session_state.sentiment)


# -------------- Call transcribe_audio based on updated state ---------------
def transcribe_audio(transcriber, language, is_recording):
    if is_recording:
        transcriber.start()
        print(f"Transcribing in {language}...")
    else:
        transcriber.stop()
        print("Transcription stopped")

transcribe_audio(st.session_state.transcriber, st.session_state.language, st.session_state.is_recording)

# Process audio if transcriber and audio data are available
if st.session_state.transcriber is not None and st.session_state.audio_data is not None:
    message = st.session_state.transcriber.process_audio(st.session_state.audio_data)
    if message is not None:
        chat_and_speak(message)


# -------------- Start the chat ---------------
if prompt := st.chat_input("Type your message here..."):
    if prompt:
        chat_and_speak(prompt)

if not st.session_state.history:
    initial_bot_message = """
        Hi there, I'm Babbelfish.ai, 
        choose a language from the menu and type something to translate into any language.\n
    """
    st.session_state.history.append({"role": "assistant", "content": initial_bot_message})
    chat_message_write("assistant", initial_bot_message)
