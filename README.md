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
