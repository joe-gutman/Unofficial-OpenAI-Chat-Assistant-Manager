import asyncio
from base_test import BaseTest
from pyaimanager.utils.exceptions import ChatAssistantError

class TestAssistantLifecycle(BaseTest):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(super().setUp())

    async def test_assistant_lifecycle(self):
        # Create assistant
        new_assistant = await self.manager.create_assistant(self.test_assistant)
        self.assertEqual(new_assistant.name, self.test_assistant['name'])

        # Update assistant
        updated_info = {'name': 'Updated Assistant'}
        updated_assistant = await self.manager.update_assistant(new_assistant, updated_info)
        self.assertEqual(updated_assistant.name, updated_info['name'])

        # Delete updated assistant
        deleted_assistant = await self.manager.delete_assistant(updated_assistant.id)
        if deleted_assistant is None:
            self.fail("Assistant was not deleted.")
        else: 
            self.assertEqual(deleted_assistant['id'], updated_assistant.id)
        
        # Check if assistant is removed from the list
        local_assistant = await self.manager.get_assistant_by_id(deleted_assistant['id'])
        if local_assistant is not None:
            self.fail("Assistant was not removed from the list.")