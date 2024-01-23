import os
import unittest
from pyaimanager import AssistantManager
from pyaimanager.utils.exceptions import ChatAssistantError
from dotenv import load_dotenv

class BaseTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv(override=True)
        print('Setting up test...')

    async def setUp(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key is None:
            self.fail("OPENAI_API_KEY environment variable not set")
        self.manager = await AssistantManager.create(api_key)
        self.test_assistant = {
            "name": "Test Assistant",
            "description": "Test assistant for testing pyaimanager",
            "model": "gpt-3.5-turbo",
            "instructions": "You are a basic test assistant. You exist to test pyaimanager, a Python wrapper for the OpenAI Assistant API.",
        }

    async def tearDown(self):
        # Delete the assistant if it exists
        assistant = await self.manager.get_assistant_by_name("Test Assistant")
        if assistant is not None:
            await self.manager.delete_assistant(assistant.id)