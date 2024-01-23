import asyncio
from base_test import BaseTest

class TestCreateAssistant(BaseTest):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(super().setUp())
        
    async def test_create_assistant(self):
        # create assistant
        new_assistant = await self.manager.create_assistant(self.test_assistant)

        # check that the assistant was created correctly
        for key in self.test_assistant:
            if key in new_assistant.__dict__:
                self.assertEqual(getattr(new_assistant, key), self.test_assistant[key], f"The new assistant's {key} should match the test assistant's {key}.")

        # check that the assistant is in the assistant list
        self.assertIsNotNone(new_assistant, "The new assistant should not be None.")
        self.assertEqual(new_assistant.name, self.test_assistant['name'], f"The new assistant's name: {new_assistant.name}, should match the expected name: {self.test_assistant['name']}.")

        # delete assistant 
        deleted_assistant = await self.manager.delete_assistant(new_assistant.id)
        if deleted_assistant is None:
            self.fail("Assistant was not deleted.")
        else: 
            self.assertEqual(deleted_assistant['id'], new_assistant.id)

        # check if assistant is removed from the list
        local_assistant = await self.manager.get_assistant_by_id(deleted_assistant['id'])
        if local_assistant is not None:
            self.fail("Assistant was not removed from the list.")