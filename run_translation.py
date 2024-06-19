import os
from dotenv import load_dotenv
from babbelfish_flow import FlowRunner
from listen_and_convert import TranscribeAudio

# Load environment variables from .env file
load_dotenv()

XI_API_KEY = os.getenv('XI_API_KEY')  # Your API key for authentication
VOICE_ID = os.getenv('VOICE_ID')  # ID of the voice model to use

LANGUAGE_TO_SPEAK = os.getenv('LANGUAGE_TO_SPEAK')
FLOW_ID = os.getenv('FLOW_ID')
CHUNK_SIZE = os.getenv('CHUNK_SIZE')  # Size of chunks to read/write at a time

def main(flow_id, message, language_to_speak):
    """
    Main function to run the babbelfish flow and generate audio.

    :param flow_id: ID of the flow to run
    :param message: Message to send to the flow
    :param language_to_speak: The language to translate the message into
    :param chunk_size: Size of chunks to read/write at a time
    :param xi_api_key: API key for Eleven Labs
    :param voice_id: ID of the voice model to use
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
    print(result)

if __name__ == "__main__":
    transcriber = TranscribeAudio()

    print("Starting transcription...")
    transcriber.start()

    try:
        while True:
            latest_transcription = transcriber.get_transcription()
            if latest_transcription:
                print(f"Transcription: {latest_transcription} \n")
                main(FLOW_ID, latest_transcription, LANGUAGE_TO_SPEAK)
    except KeyboardInterrupt:
        transcriber.stop()
        print("Transcription stopped.")
