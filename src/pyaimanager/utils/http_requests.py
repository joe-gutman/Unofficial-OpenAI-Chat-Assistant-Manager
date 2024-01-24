import aiohttp
import json
# import logger
from .logging import logger

import logging

class HTTPRequest:
    def __init__(self, api_key):
        """
        Initialize a new HTTPRequest instance.

        Args:
            api_key (str): The API key to use for requests.
        """
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/"
        self.logger = logging.getLogger(__name__)

    async def request(self, request_type, endpoint, data=None):
        """
        Send an HTTP request.

        Args:
            request_type (str): The type of the request ('get', 'post', 'put', 'delete').
            endpoint (str): The endpoint to send the request to.
            data (dict, optional): The data to send with the request.

        Returns:
            dict: The response from the server.
        """
        url = self.base_url + endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "assistants=v1",
        } 

        session = aiohttp.ClientSession()
        self.logger.debug(f"Sending {request_type} request to {url} with data {data}")
        if request_type.lower() == 'get':
            response = await session.get(url, headers=headers)
        elif request_type.lower() == 'post':
            response = await session.post(url, headers=headers, data=json.dumps(data))
        elif request_type.lower() == 'put':
            response = await session.put(url, headers=headers, data=json.dumps(data))
        elif request_type.lower() == 'delete':
            response = await session.delete(url, headers=headers)
        else:
            session.close()
            raise ValueError("Invalid request type")

        result = await self._handle_response(response)
        await session.close()
        return result

    async def _handle_response(self, response):
        """
        Handle the response from an HTTP request.

        Args:
            response (aiohttp.ClientResponse): The response to handle.

        Returns:
            dict: The parsed JSON response.
        """
        if not 200 <= response.status < 300:
            self.logger.error(f"HTTP request failed with status code {response.status}, response: {await response.text()}")
            raise Exception(f"HTTP request failed with status code {response.status}, response: {await response.text()}")

        return await response.json()