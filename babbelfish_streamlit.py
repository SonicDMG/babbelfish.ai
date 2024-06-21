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
LANGUAGE_TO_SPEAK = os.getenv('LANGUAGE_TO_SPEAK')

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

# Initialize session state variables for chat history and conversation history
if "history" not in st.session_state:
    st.session_state.history = []

# -------------- Define Layout ---------------

# Sidebar with fish logo, language input, and buttons
with st.sidebar:
    st.caption("🚀 A Streamlit translation chatbot powered by Langflow")
    st.image("./static/fish_ear.webp", use_column_width=True)

    # List of options for the dropdown
    language_options = ["English", "Brazilian Portuguese", "Finnish", "French", "Japanese", "Spanish", "Urdu", "Californian surfer", "Other"]

    # Create a selectbox for language selection
    selected_option = st.selectbox("Language to translate to", language_options)
    
    # Show text input if "Other" is selected
    if selected_option == "Other":
        st.session_state.language = st.text_input("Please specify the language")
    else:
        st.session_state.language = selected_option

    st.text_input("Audio voice for speech (can be a name like 'Nicole' or a voice ID)", value=VOICE_ID, key="voice_id")
    st.selectbox("ElevenLabs.io model (turbo is faster, but less accurate)", [MODEL_ID, "eleven_turbo_v2"], key="model_id")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        add_transcription_start = st.button("Start voice translation")
    with col2:
        add_transcription_stop = st.button("Stop voice translation")

# Fixed title
st.markdown('<div class="fixed-header"><h1>Babbelfish.ai 💬🐠💬</h1></div>', unsafe_allow_html=True)

# Scrollable container for chat messages
chat_placeholder = st.empty()  # Placeholder for chat messages

def render_chat():
    with chat_placeholder.container():
        st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            st.chat_message(message['role']).write(message['content'])
        
        # Inject JavaScript to scroll to the bottom of the chat container
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
                elevenlabs_component(text=translation, voice_id=st.session_state.voice_id, model_id=st.session_state.model_id)
    else:
        transcriber.stop()

def chat_message_write(role, content):
    """
    Writes a message to the chat output.

    :param role: The role of the message sender (e.g., "assistant" or "user")
    :param content: The content of the message
    """
    st.session_state.messages.append({"role": role, "content": content})
    render_chat()  # Re-render chat messages after adding a new message

# -------------- Start the chat ---------------

# Chat input at the bottom
if prompt := st.chat_input("Type your message here..."):
    if prompt:
        print("prompt is True")
        chat_message_write("user", prompt)
        response = translate_speech(FLOW_ID, prompt, st.session_state.language)
        chat_message_write("assistant", response)
        elevenlabs_component(text=response, voice_id=st.session_state.voice_id, model_id=st.session_state.model_id)

if add_transcription_start:
    st.session_state.transcriber = TranscribeAudio()
    print("Transcriber is instantiated")
    st.session_state.recording = True
    transcribe_audio(st.session_state.transcriber, st.session_state.language, True)

if add_transcription_stop:
    st.session_state.recording = False
    transcribe_audio(st.session_state.transcriber, st.session_state.language, False)

if not st.session_state.history:
    initial_bot_message = "Hi there, I'm Babbelfish.ai, type something to translate into any language.\n"
    st.session_state.history.append({"role": "assistant", "content": initial_bot_message})
    chat_message_write("assistant", initial_bot_message)
