import os
from dotenv import load_dotenv

import streamlit as st
from babbelfish_flow import FlowRunner
from listen_and_convert import TranscribeAudio
from elevenlabs_component import elevenlabs_component

# Load environment variables from .env file
load_dotenv()

FLOW_ID = os.getenv('FLOW_ID')

# -------------- Streamlit app config ---------------

st.set_page_config(page_title="Babbelfish.ai", page_icon="🐠")

# -------------- Define session variables ---------------

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Type in text for translation"}]

if "transcriber" not in st.session_state:
    st.session_state.transcriber = None

# -------------- Define Layout ---------------

st.header(f"This page has run {st.session_state.counter} times.")
st.title("Babbelfish.ai 💬🐠💬")
st.caption("🚀 A Streamlit translation chatbot powered by Langflow")

st.image("./static/fish_ear.webp")

st.sidebar.button("Run it again")
st.sidebar.text_input("Language to translate to", key="language")
add_transcrption_start = st.sidebar.button("Start voice translation")
add_transcrption_stop = st.sidebar.button("Stop voice translation")

# -------------- Translate speech ---------------

def translate_speech(flow_id, message, language_to_speak):
    """
    Main function to run the babbelfish flow and generate audio.

    :param flow_id: ID of the flow to run
    :param message: Message to send to the flow
    :param language_to_speak: The language to translate the message into
    """
    tweaks = {
        "Prompt-y2nny": {},
        "OpenAIModel-l5fMw": {},
        "ChatOutput-qXbZT": {},
        "ChatInput-wvbiq": {
            "input_value": f"{message}"
        },
        "TextInput-zSj9q": {
            "input_value": f"{language_to_speak}"
        }
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
                elevenlabs_component(text=translation)
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
if prompt := st.chat_input(st.session_state.messages[0]['content']):
    print("prompt is True")
    chat_message_write("user", prompt)
    response = translate_speech(FLOW_ID, prompt, st.session_state.language)
    chat_message_write("assistant", response)
    elevenlabs_component(text=response)

if add_transcrption_start:
    st.session_state.transcriber = TranscribeAudio()
    print("Transcriber is instantiated")
    transcribe_audio(st.session_state.transcriber, st.session_state.language, True)

if add_transcrption_stop:
    transcribe_audio(st.session_state.transcriber, st.session_state.language, False)

