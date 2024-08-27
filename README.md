# babbelfish.ai

## Overview
Babbelfish.ai is a Streamlit-based translation chatbot powered by Langflow. It allows users to translate text and speech into various languages, detect the language of the input, analyze sentiment, and provide explanations. The application also supports voice translation using ElevenLabs.io.

![Babbelfish demo gif](https://raw.githubusercontent.com/SonicDMG/babbelfish.ai/main/static/babbelfish.gif)

## Features
- **Text Translation**: Translate text into multiple languages.
- **Voice Translation**: Translate spoken words into different languages.
- **Language Detection**: Automatically detect the language of the input text.
- **Sentiment Analysis**: Analyze the sentiment of the input text.
- **Explanations**: Provide explanations for the detected sentiment.
- **Voice Output**: Use ElevenLabs.io for voice synthesis of the translated text.

## Installation

### Prerequisites
- Python 3.11 or higher
- Streamlit
- Langflow
- ElevenLabs.io API key
- `coloredlogs` package

### Steps
1. Clone the repository:
	```sh
	git clone https://github.com/yourusername/babbelfish.ai.git
	cd babbelfish.ai
	```

2. Run `install.sh` to
- Create a `.env` file in the root directory (a copy of the `.env.example` file)
- Install the required python packages
- Install the required npm packages

## Usage
1. Run `run.sh` to launch the Streamlit application:

2. Open your web browser and navigate to `http://localhost:8501`.

3. Use the sidebar to select the language you want to translate to and configure other settings.

4. Type your message in the chat input or use the voice translation feature.

## Langflow
In order to fully run Babbelfish.ai, you will need to host Langflow. [Langflow](https://langflow.org) is a free, open source tool that allows you visually build Generative AI workflows. Once you have Langflow installed, download the included [Babbelfish.ai.json](https://github.com/SonicDMG/babbelfish.ai/blob/main/Babbelfish.ai.json) file and upload it in your Langflow instance.


## Logging
The application uses `coloredlogs` for logging. Logs are displayed in the terminal with different colors based on the log level.

## File Structure
- `babbelfish.py`: Main application file.
- `babbelfish_flow.py`: Contains the LangflowRunner class for interacting with Langflow.
- `listen_and_convert.py`: Contains the TranscribeAudio class for handling audio transcription.
- `components/`: Contains Streamlit components for audio and ElevenLabs integration.
- `static/`: Contains static assets like images.

## Known problems
### MacOS / FLAC
If you get this error from the `streamlit` app while running on the Mac:
```
Traceback (most recent call last):
  File "/Users/xxx/.pyenv/versions/3.12.0/envs/babelfish/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/Users/xxx/.pyenv/versions/3.12.0/envs/babelfish/lib/python3.12/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "/Users/xxx/workspace/datastax/babbelfish.ai/babbelfish.py", line 209, in <module>
    audio_message = st.session_state.transcriber.process_audio(st.session_state.audio_data, st.session_state.speaking_language)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/xxx/workspace/datastax/babbelfish.ai/listen_and_convert.py", line 109, in process_audio
    result = self.recognize_speech_from_mic_as_bytes(audio_data, speaking_language)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/xxx/workspace/datastax/babbelfish.ai/listen_and_convert.py", line 88, in recognize_speech_from_mic_as_bytes
    transcription = self.recognizer.recognize_google(audio, language=speaking_language)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/xxx/.pyenv/versions/3.12.0/envs/babelfish/lib/python3.12/site-packages/speech_recognition/__init__.py", line 826, in recognize_google
    flac_data = audio_data.get_flac_data(
                ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/xxx/.pyenv/versions/3.12.0/envs/babelfish/lib/python3.12/site-packages/speech_recognition/__init__.py", line 445, in get_flac_data
    flac_converter = get_flac_converter()
                     ^^^^^^^^^^^^^^^^^^^^
  File "/Users/xxx/.pyenv/versions/3.12.0/envs/babelfish/lib/python3.12/site-packages/speech_recognition/__init__.py", line 1196, in get_flac_converter
    raise OSError("FLAC conversion utility not available - consider installing the FLAC command line application by running `apt-get install flac` or your operating system's equivalent")
OSError: FLAC conversion utility not available - consider installing the FLAC command line application by running `apt-get install flac` or your operating system's equivalent

```

then you may not have `FLAC` installed on your computer. Try:

```
brew install flac
```

or [any of the solutions described here](https://stackoverflow.com/questions/49737909/flac-conversion-utility-not-available-consider-installing-the-flac-command-lin).


## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgements
- [Streamlit](https://streamlit.io/)
- [Langflow](https://langflow.io/)
- [ElevenLabs](https://elevenlabs.io/)
- [coloredlogs](https://coloredlogs.readthedocs.io/)

## Contact
For any questions or suggestions, please open an issue or contact the repository owner.
