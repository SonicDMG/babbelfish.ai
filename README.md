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

2. Create a `.env` file in the root directory by copying the `.env.example` file and updating the environment variables:
    ```sh
    cp .env.example .env
    ```
    
3. Install the required packages:
	```sh
	pip install -r requirements.txt && cd components && npm install --prefix elevenlabs_component/frontend && npm run build --prefix elevenlabs_component/frontend && npm install --prefix audio_component/frontend && npm run build --prefix audio_component/frontend
	```

## Usage
1. Run the Streamlit application:
	```sh
	streamlit run babbelfish.py
	```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Use the sidebar to select the language you want to translate to and configure other settings.

4. Type your message in the chat input or use the voice translation feature.

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
