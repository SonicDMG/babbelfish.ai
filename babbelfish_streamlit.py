import os
import streamlit as st
from dotenv import load_dotenv
from babbelfish_flow import FlowRunner
from listen_and_convert import TranscribeAudio
from elevenlabs_component import elevenlabs_component

# Load environment variables from .env file
load_dotenv()

FLOW_ID = os.getenv('FLOW_ID')
VOICE_ID = os.getenv('VOICE_ID')
MODEL_ID = os.getenv('MODEL_ID')
#MODEL_ID = "eleven_turbo_v2"

# -------------- Streamlit app config ---------------

st.set_page_config(page_title="Babbelfish.ai", page_icon="🐠", layout="wide")

# -------------- Define session variables ---------------

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Type in text for translation"}]

if "transcriber" not in st.session_state:
    st.session_state.transcriber = None

# Initialize session state variables
if "recording" not in st.session_state:
    st.session_state.recording = False

# -------------- Define Layout ---------------

# Sidebar with fish logo, language input, and buttons
with st.sidebar:
    st.image("./static/fish_ear.webp", use_column_width=True)
    st.text_input("Language to translate to", key="language")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        add_transcription_start = st.button("Start voice translation")
    with col2:
        add_transcription_stop = st.button("Stop voice translation")

# Main section
with st.container():
    st.header(f"This page has run {st.session_state.counter} times.")
    st.title("Babbelfish.ai 💬🐠💬")
    st.caption("🚀 A Streamlit translation chatbot powered by Langflow")

# -------------- Translate speech ---------------

def translate_speech(flow_id, message, language_to_speak):
    """
    Main function to run the babbelfish flow and generate audio.

    :param flow_id: ID of the flow to run
    :param message: Message to send to the flow
    :param language_to_speak: The language to translate the message into
    """
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
        "Prompt-Fa0Cf": {}
    }

    api_key = None  # Replace with your API key if needed

    flow_runner = FlowRunner(flow_id=flow_id, api_key=api_key, tweaks=tweaks)
    response_json = flow_runner.run_flow(message=message)
    print(f"Response JSON: {response_json}")
    result = flow_runner.extract_output_message(response_json)
    return result

def transcribe_audio(transcriber, language_to_speak, start):
    if start:
        transcriber.start()
        print("Transcription started.")
        while True:
            latest_transcription = transcriber.get_transcription()
            if latest_transcription:
                chat_message_write("user", latest_transcription)
                translation = translate_speech(FLOW_ID, latest_transcription, language_to_speak)
                chat_message_write("assistant", translation)
                elevenlabs_component(text=translation, voice_id=VOICE_ID, model_id=MODEL_ID)
    else:
        transcriber.stop()

def chat_message_write(role, content):
    """
    Writes a message to the chat output.

    :param role: The role of the message sender (e.g., "assistant" or "user")
    :param content: The content of the message
    """
    st.session_state.messages.append({"role": role, "content": content})
    st.chat_message(role).write(content)

# -------------- Start the chat ---------------

# Chat input at the bottom
if prompt := st.chat_input(st.session_state.messages[0]['content']):
    print("prompt is True")
    chat_message_write("user", prompt)
    response = translate_speech(FLOW_ID, prompt, st.session_state.language)
    chat_message_write("assistant", response)
    elevenlabs_component(text=response, voice_id=VOICE_ID, model_id=MODEL_ID)

if add_transcription_start:
    st.session_state.transcriber = TranscribeAudio()
    print("Transcriber is instantiated")
    st.session_state.recording = True
    transcribe_audio(st.session_state.transcriber, st.session_state.language, True)

if add_transcription_stop:
    st.session_state.recording = False
    transcribe_audio(st.session_state.transcriber, st.session_state.language, False)
