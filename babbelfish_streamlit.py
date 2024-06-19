import os
from dotenv import load_dotenv

import websocket
from websocket_server import WebSocketServer
#from streamlit_autorefresh import st_autorefresh
from babbelfish_flow import FlowRunner
from listen_and_convert import TranscribeAudio
import streamlit as st

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

# Initialize the session state for the text area
if 'websocket_text' not in st.session_state:
    st.session_state.websocket_text = ""

# -------------- Define Layout ---------------

st.header(f"This page has run {st.session_state.counter} times.")
st.title("Babbelfish.ai 💬🐠💬")
st.caption("🚀 A Streamlit translation chatbot powered by Langflow")

st.image("./static/fish_ear.webp")

st.sidebar.button("Run it again")
st.sidebar.text_input("Language to translate to", key="language")
add_transcrption_start = st.sidebar.button("Start transcription")
add_transcrption_stop = st.sidebar.button("Stop transcription")

# Create a text area in the sidebar with the initial text from the session state
add_websocket_text = st.sidebar.text_area("Websocket response", st.session_state.websocket_text)

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
                chat_message_write(
                    "assistant", 
                    translate_speech(FLOW_ID, latest_transcription, language_to_speak)
                )
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

if add_transcrption_start:
    st.session_state.transcriber = TranscribeAudio()
    print("Transcriber is instantiated")
    transcribe_audio(st.session_state.transcriber, st.session_state.language, True)

if add_transcrption_stop:
    transcribe_audio(st.session_state.transcriber, st.session_state.language, False)


# Auto-refresh the Streamlit app every few seconds
#st_autorefresh(interval=3000)  # Refresh every 3 seconds

# Function to initialize and start the WebSocket server
def init_websocket_server():
    if 'websocket_server' not in st.session_state:
        st.session_state.websocket_server = WebSocketServer(host="127.0.0.1", port=8000)
        st.session_state.server_thread = st.session_state.websocket_server.run_in_thread()

# Initialize the WebSocket server
init_websocket_server()

def on_message(ws, message):
    print(f"Received message: {message}")
    # Display the data
    st.session_state.websocket_text = message
    #st.sidebar.text_area("Websocket response", st.session_state.websocket_text)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket connection opened")
    ws.send("Hello from client!")

def run_websocket_client():
    websocket_url = "ws://localhost:8000/ws"
    ws = websocket.WebSocketApp(
        websocket_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

if __name__ == "__main__":
    run_websocket_client()


