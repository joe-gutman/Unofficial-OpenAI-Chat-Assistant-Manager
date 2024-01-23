import asyncio
from base_test import BaseTest
from pyaimanager.utils.exceptions import ChatAssistantError
from pyaimanager.conversation import Conversation

class TestConversation(BaseTest):
    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(super().setUp())

    async def test_conversation(self):
        self.assistant = await self.manager.create_assistant(self.test_assistant)
        self.conversation = await self.assistant.create_conversation("Test Conversation", "This is a test conversation")

        self.assertIsNotNone(self.conversation)
        self.assertIsInstance(self.conversation, Conversation)

        # Check that the conversation was created correctly
        self.assertEqual(self.conversation.title, "Test Conversation")
        self.assertEqual(self.conversation.description, "This is a test conversation")

        # Check that the conversation is in the assistant's conversation list
        message = "Hello, how are you?"
        await self.assistant.send_message(message, self.conversation)
        self.assertEqual(self.conversation.get_messages_simple()[-1]['text'], message)

        # Check that the conversation was removed from the assistant's conversation list
        await self.assistant.delete_conversation(self.conversation.id)
        await super().tearDown()