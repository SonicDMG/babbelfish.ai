"""A class to handle running the babblefish.ai Langflow GenAI workflow and extracting responses."""
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import requests
import coloredlogs

# Load environment variables from .env file
load_dotenv()
BASE_API_URL = os.getenv('BASE_API_URL')

if not BASE_API_URL:
    raise EnvironmentError("BASE_API_URL environment variable not set")

# Configure logging
logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO', logger=logger, fmt='%(levelname)s %(message)s')

class LangflowRunner:
    """A class to handle running the babblefish flow and extracting responses."""

    def __init__(self,
                 flow_id: str,
                 api_key: Optional[str] = None,
                 tweaks: Optional[Dict[str, Any]] = None):
        """
        Initialize the FlowRunner with the necessary parameters.

        :param flow_id: The ID of the flow to run.
        :param api_key: Optional API key for authentication.
        :param tweaks: Optional dictionary for custom tweaks to the flow.
        """
        self.flow_id = flow_id
        self.api_key = api_key
        self.tweaks = tweaks

    def run_flow(self,
                 message: str,
                 output_type: str = "chat",
                 input_type: str = "chat") -> Dict[str, Any]:
        """
        Run a flow with a given message and optional tweaks.

        :param message: The message to send to the flow.
        :param output_type: The type of output expected (default is "chat").
        :param input_type: The type of input provided (default is "chat").
        :return: The JSON response from the flow.
        """
        api_url = f"{BASE_API_URL}/{self.flow_id}"
        logger.info("API URL: %s", api_url)

        payload = {
            "input_value": message,
            "output_type": output_type,
            "input_type": input_type,
        }
        if self.tweaks:
            payload["tweaks"] = self.tweaks  # type: ignore

        headers = {"x-api-key": self.api_key} if self.api_key else None

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=20)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            logger.error("Request failed: %s", e)
            raise

    def extract_output_message(self, response_json: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract the output messages from the flow response JSON and combine them into a single results object.

        :param response_json: The JSON response from the flow.
        :return: A dictionary containing the extracted results.
        """
        outputs = response_json.get('outputs', [])
        if not outputs:
            return {
                'translation': 'N/A',
                'explanation': 'N/A',
                'detected_language': 'N/A',
                'sentiment': 'N/A'
            }

        # Initialize default values
        translation = 'N/A'
        explanation = 'N/A'
        detected_language = 'N/A'
        sentiment_output = 'N/A'

        # Iterate through the outputs to find the relevant components
        for output in outputs[0].get('outputs', []):
            component_display_name = output.get('component_display_name', '')
            message_text = output.get('results', {}).get('message', {}).get('text', 'N/A')

            if component_display_name == 'Translation':
                translation = message_text
            elif component_display_name == 'Explanation':
                explanation = message_text
            elif component_display_name == 'Detected Language':
                detected_language = message_text
            elif component_display_name == 'Sentiment':
                sentiment_output = message_text

        # Log the extracted information
        logger.info("Translation: %s", translation)
        logger.info("Detected Language: %s\n", detected_language)

        results = {
            'translation': translation,
            'explanation': explanation,
            'detected_language': detected_language,
            'sentiment': sentiment_output
        }
        return results
    