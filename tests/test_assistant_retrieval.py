import unittest
from base_test import BaseTest

"""
Tests the assistant retrieval which involves:
    getting all assistants
    getting one assistant by ID and name
"""


class TestGetAssistants(BaseTest):
    @unittest.skip("Skipping this test for now")
    def test_get_assistants(self):
        expected_attributes = ['id', 'created_at', 'name', 'description', 'model', 'instructions', 'tools', 'file_ids', 'metadata', 'conversations', 'active_conversation']

        # Get all assistants
        response = self.manager.get_assistants()

        self.assertIsInstance(response, list)
        for assistant in response:
            self.assertIsInstance(assistant, object)
            for attr in expected_attributes:
                self.assertTrue(hasattr(assistant, attr), f"Get Assistants Error: Assistant is missing attribute: {attr}")

        # Get assistant by ID
        assistant = self.manager.get_assistant_by_id(response[0].id)
        self.assertIsInstance(assistant, object)
        for attr in expected_attributes:
            self.assertTrue(hasattr(assistant, attr), f"Get Assistant Error: Assistant is missing attribute: {attr}")

        # Get assistant by name

        assistant = self.manager.get_assistant_by_name(response[0].name)
        self.assertIsInstance(assistant, object)
        for attr in expected_attributes:
            self.assertTrue(hasattr(assistant, attr), f"Get Assistant Error: Assistant is missing attribute: {attr}")