import requests
import json

class HTTPRequest:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/"

    def request(self, request_type, endpoint, data=None):
        url = self.base_url + endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        if request_type.lower() == "get":
            response = requests.get(url, headers=headers)
        elif request_type.lower() == "post":
            response = requests.post(url, headers=headers, data=json.dumps(data))
        elif request_type.lower() == "put":
            response = requests.put(url, headers=headers, data=json.dumps(data))
        elif request_type.lower() == "delete":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError("Invalid request type")

        if not 200 <= response.status_code < 300:
            raise Exception(f"HTTP request failed with status code {response.status_code}, response: {response.text}")
            
        return response.json()