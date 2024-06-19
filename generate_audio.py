from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream

class GenerateAudio:
    """
    A class to generate audio using the ElevenLabs Text-to-Speech API.
    
    Attributes:
        chunk_size (int): Size of chunks to read/write at a time.
        input_text (str): The text to be converted to speech.
        xi_api_key (str): API key for Eleven Labs.
        voice_id (str): ID of the voice model to use.
    """

    def __init__(self,
                 chunk_size: int,
                 input_text: str,
                 xi_api_key: str,
                 voice_id: str):
        """
        Initialize the GenerateAudio class with the necessary parameters.

        :param chunk_size: Size of chunks to read/write at a time.
        :param input_text: The text to be converted to speech.
        :param xi_api_key: API key for Eleven Labs.
        :param voice_id: ID of the voice model to use.
        """
        self.chunk_size = chunk_size
        self.input_text = input_text
        self.xi_api_key = xi_api_key
        self.voice_id = voice_id

    def get_audio_with_api(self):
        """
        Generate audio from the input text using the ElevenLabs 
        Text-to-Speech API and stream it directly to speakers.
        """
        client = ElevenLabs(
              api_key=self.xi_api_key # Defaults to ELEVEN_API_KEY
            )
        audio_stream = client.generate(
            text=self.input_text,
            voice=self.voice_id,
            model="eleven_multilingual_v2",
            stream=True
        )
        stream(audio_stream)
        print("Audio stream played successfully.\n")
