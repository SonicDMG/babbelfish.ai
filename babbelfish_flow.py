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
            "Prompt-sXFMH": {},
            "GroqModel-eEwav": {},
            "TextInput-zSj9q": {},
            "ChatOutput-ZggnW": {},
            "ChatInput-V3zKC": {},
            "TextOutput-rRoEL": {},
            "Prompt-Fa0Cf": {},
            "OpenAIModel-lDBVs": {},
            "Prompt-zX3NP": {},
            "TextOutput-mg3fX": {},
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
        print(f"API URL: {api_url}")

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

    def extract_output_message(self, response_json: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract the output messages from the flow response JSON and combine them into a single results object.

        :param response_json: The JSON response from the flow.
        :return: A dictionary containing the extracted results.
        """
        outputs = response_json.get('outputs', 'No output message found')
        if outputs == 'No output message found':
            return {'error': outputs}

        # Extract the first nested output
        first_output = outputs[0].get('outputs', [])
        if not first_output:
            return {'error': 'No nested output found'}

        # Extract the result from the first nested output
        result1 = first_output[0].get('results', {}).get('result', 'No result found')

        # Extract the result from the second nested output
        if len(first_output) > 1:
            result2 = first_output[1].get('results', {}).get('result', 'No result found')
        else:
            result2 = 'Second nested output not found'

        # Extract the result from the third nested output
        if len(first_output) > 2:
            result3 = first_output[2].get('results', {}).get('result', 'No result found')
        else:
            result3 = 'Third nested output not found'

        results = {
            'result1': result1,
            'result2': result2,
            'result3': result3
        }
        return results

