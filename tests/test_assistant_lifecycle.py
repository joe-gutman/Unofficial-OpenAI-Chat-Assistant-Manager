import unittest
import pyaimanager
from base_test import BaseTest

'''
Tests the assistant lifecycle which involves:
    creating
    setting as active
    deleting
'''

class TestAssistantLifecycle(BaseTest):
    def test_create_set_delete_assistant(self):
        # Create assistant
        assistant_params = {
            "name": "Test Assistant",
            "description": "This is a test assistant",
            "model": "gpt-3.5-turbo",
            "instructions": "You are a basic test assistant, here to test the assistant lifecycle. Which is to create, set as active, and delete.",
        }

        # Create assistant
        assistant=self.manager.create_assistant(assistant_params)
        all_assistants = self.manager.get_assistants()
        for asst in all_assistants:
            print(asst.name)

        # Check if assistant exists by name and id
        self.assertIsNotNone(self.manager.get_assistant_by_name(assistant.name))
        self.assertIsNotNone(self.manager.get_assistant_by_id(assistant.id))

        # Set assistant as the active assistant
        active_assistant = self.manager.set_active_assistant(assistant)
        self.assertEqual(assistant.id, active_assistant.id)

        # Delete the active assistant
        deleted_assistant = self.manager.delete_assistant(assistant.id)

        # Try to get the assistant by name and id, should return None
        self.assertEqual(self.manager.get_assistant_by_id(assistant.id), None)
        self.assertEqual(self.manager.get_assistant_by_name(assistant.name), None)


        # Check if the active_assistant has been removed or is still the active assistant
        active_assistant = self.manager.get_active_assistant()
        self.assertEqual(active_assistant, None)