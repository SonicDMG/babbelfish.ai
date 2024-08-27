import os

from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()


def test_langflow_server():
    """
    GIVEN the path to a local LangFlow server
    IF a live request is made to the server
    THEN the server is alive and returns 200 
    """
    # Get a url on the LangFlow server
    api_base = os.getenv("BASE_API_URL") 
    flow_id = os.getenv("FLOW_ID")
    api_url = f"{api_base}/{flow_id}"    

    # Make a GET request, confirm reqsult
    req = requests.get(api_url)
    assert req.status_code == 200
