import aiohttp
import json
# import logger
from .logging import logger

class HTTPRequest:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/"

    async def request(self, request_type, endpoint, data=None):
        url = self.base_url + endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "assistants=v1",
        }

        session = aiohttp.ClientSession()
        if request_type.lower() == 'get':
            response = await session.get(url, headers=headers)
        elif request_type.lower() == 'post':
            print("DATA:",data)
            response = await session.post(url, headers=headers, data=json.dumps(data))
        elif request_type.lower() == 'put':
            print("DATA:",data)
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
        if not 200 <= response.status < 300:
            raise Exception(f"HTTP request failed with status code {response.status}, response: {await response.text()}")

        return await response.json()