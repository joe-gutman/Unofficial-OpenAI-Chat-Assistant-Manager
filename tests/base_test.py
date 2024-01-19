import os
import unittest
from pyaimanager import AssistantManager
from pyaimanager.exceptions import ChatAssistantError
from dotenv import load_dotenv

class BaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv(override=True)
        print('Setting up test...')

    def setUp(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key is None:
            self.fail("OPENAI_API_KEY environment variable not set")
        self.manager = AssistantManager(api_key)

    def tearDown(self):
        # Delete the assistant if it exists
        assistant = self.manager.get_assistant_by_name("Test Assistant")
        if assistant is not None:
            self.manager.delete_assistant(assistant.id)