""""""
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

class FlowRunner:
    """A class to handle running the babblefish flow and extracting responses."""

    BASE_API_URL = os.getenv('BASE_API_URL')

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
        self.tweaks = tweaks or {
            "Prompt-y2nny": {},
            "OpenAIModel-l5fMw": {},
            "ChatOutput-qXbZT": {},
            "ChatInput-KxmWA": {},
            "TextInput-XprTX": {}
        }

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
        api_url = f"{self.BASE_API_URL}/{self.flow_id}"

        payload = {
            "input_value": message,
            "output_type": output_type,
            "input_type": input_type,
        }
        if self.tweaks:
            payload["tweaks"] = self.tweaks

        headers = {"x-api-key": self.api_key} if self.api_key else None

        # Send POST request to the flow API
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()

    def extract_output_message(self, response_json: Dict[str, Any]) -> str:
        """
        Extract the output message from the flow response JSON.

        :param response_json: The JSON response from the flow.
        :return: The output message.
        """
        outputs = response_json.get('outputs', 'No output message found')
        if outputs == 'No output message found':
            return outputs

        # Extract the first nested output
        first_output = outputs[0].get('outputs', [])
        if not first_output:
            return 'No nested output found'

        # Extract the result from the first nested output
        results = first_output[0].get('results', {}).get('result', 'No result found')
        return results
