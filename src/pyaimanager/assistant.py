import asyncio
import json
from .utils.logging import logger
from .utils.exceptions import ChatAssistantError, ChatMessageError, ChatConversationError, ChatRunError
from .conversation import Conversation

class Assistant:
    """
    A class used to represent an assistant.

    Attributes:
        id (str): The ID of the assistant.
        name (str): The name of the assistant.
        description (str): The description of the assistant.
        model (str): The model of the assistant.
        instructions (str): The instructions of the assistant.
        tools (str): The tools of the assistant.
        file_ids (str): The file IDs of the assistant.
        metadata (str): The metadata of the assistant.
        conversations (list): The conversations of the assistant, it contains the following:
            title (str): The title of the conversation.
            description (str): The description of the conversation.
            thrad (object): The thread of the conversation.
            run (object): The run of the conversation.
        active_conversation (object): The active conversation of the assistant.

        example of what conversation object looks like:
            {
            "title": "Test Conversation",
            "description": "This is a test conversation",
            "thread": [
                    {
                        "role": "user",
                        "content": "Hello"
                    },
                    {
                        "role": "assistant",
                        "content": "Hi there!"
                    }
                ],
            "run": {
                "id": "run_abc123",
                "object": "thread.run",
                "created_at": 1699063290,
                "assistant_id": "asst_abc123",
                "thread_id": "thread_abc123",
                "status": "queued",
                "started_at": 1699063290,
                "expires_at": null,
                "cancelled_at": null,
                "failed_at": null,
                "completed_at": 1699063291,
                "last_error": null,
                "model": "gpt-4",
                "instructions": null,
                "tools": [
                    {
                        "type": "code_interpreter"
                    }
                ],
                "file_ids": [
                    "file-abc123",
                    "file-abc456"
                ],
                "metadata": {}
                }
            }

        See OpenAI's documentation at https://platform.openai.com/docs/introduction for more information.
    """

    def __init__(self, assistant, http_request_handler):
        self.__http = http_request_handler
        self.__update_interval = 5

        self.id = assistant['id']
        self.name = assistant['name']
        self.object = assistant['object']
        self.created_at = assistant['created_at']
        self.description = assistant['description']
        self.model = assistant['model']
        self.instructions = assistant['instructions']
        self.tools = assistant.get('tools', None)
        self.file_ids = assistant.get('file_ids', None)
        self.metadata = assistant.get('metadata', None)
        self.functions = assistant.get('functions', None)
        self.conversations = assistant.get('conversations', [])
        self.active_conversation = assistant.get('active_conversation', None)

    def update(self, new_parameters):
        """
        Updates the Assistant's attributes with new data.

        Args:
            new_parameters (dict): A dictionary of parameters to update the Assistant with.
        """
        # Update the Assistant's attributes with the new parameters
        for key, value in new_parameters.items():
            if hasattr(self, key):
                setattr(self, key, value)
        logger.info(f"Updated Assistant; id: {self.id}, name: {self.name}")
        
        return self
    
    def use_function(self, function_name, *args, **kwargs):
        if function_name in self.functions:
            return self.functions[function_name](*args, **kwargs)
        else:
            raise Exception(f"Function {function_name} not found")


    async def _get_message_response(self, conversation):
        """
        Waits for a run to complete and then returns the response.

        Args:
            conversation (object): The conversation to get the run status from.

        Returns:
            dict: The response from the completed run.
        """
        logger.info(f"Waiting for run completion for run ID: {conversation.get_run_id()}")
        while True:
            try:
                run = await self._get_run_status(conversation)
                
                if run['status'] == 'requires_action':
                    await self._handle_required_action(run, conversation)

                elif run['status'] == 'completed':
                    return await self._handle_completed_run(run, conversation)

                else:
                    logger.info(f"Run not completed yet for run ID: {run['id']}")
                    await asyncio.sleep(self.__update_interval)
            except Exception as e:
                logger.error(f"Error waiting for run completion: {e}")
                raise ChatRunError(f"Error waiting for run completion: {e}. Please try again.")

    async def _get_run_status(self, conversation):
        run_id = conversation.get_run_id()
        thread_id = conversation.get_thread_id()
        return await self.__http.request("get", f"threads/{thread_id}/runs/{run_id}")

    async def _handle_required_action(self, run, conversation):
        tool_outputs = []
        for tool_call in run['required_action']['submit_tool_outputs']['tool_calls']:
            function_name = tool_call['function']['name']
            function_args = json.loads(tool_call['function']['arguments'])
            function_output = self.use_function(function_name, **function_args)
            tool_outputs.append({
                "tool_call_id": tool_call['id'],
                "output": function_output,
            })

        run_id = conversation.get_run_id()
        thread_id = conversation.get_thread_id()
        await self.__http.request(
            "post", 
            f"threads/{thread_id}/runs/{run_id}/submit_tool_outputs",
            json={"tool_outputs": tool_outputs})

    async def _handle_completed_run(self, run, conversation):
        logger.info(f"Run completed for run ID: {run['id']}")
        thread_id = conversation.get_thread_id()
        thread = await self.__http.request("get", f"threads/{thread_id}")
        conversation.set_thread(thread)
        conversation.set_run(run)
        messages = await self.__http.request("get", f"threads/{thread_id}/messages")
        conversation.set_messages(messages['data'])
        conversation.set_latest_response(conversation.get_messages()[0])

        logger.info(f"Messages: {conversation.get_messages()}")
        logger.info(f"Response: {conversation.latest_response}")

        return conversation.latest_response

    async def _create_new_thread(self, message):
        """
        Creates a new thread for the assistant.

        Args:
            message (str): The message to send to the assistant.

        Returns:
            The new thread.
        """
        try:
            new_thread = await self.__http.request("post", "threads", { "messages":[{ "role": "user", "content": message }] })
            logger.info(f"New thread created with ID: {new_thread['id']}")
            return new_thread
        except Exception as e:
            logger.error(f"Error creating new thread: {e}, for message: {message}")
            raise ChatRunError(f"Error creating new thread: {e}, for message: {message}. Please check your setup and try again.")

    async def _create_new_run(self, thread_id):
        try:
            run = await self.__http.request(
                "post", 
                f"threads/{thread_id}/runs", 
                {"assistant_id": self.id}
            )
            logger.info(f"New run created with thread ID: {thread_id}")
            return run
        except Exception as e:
            logger.error(f"Error creating new run: {e}")
            raise ChatRunError(f"Error creating new run: {e}")

    async def create_conversation(self, title, description = None):
        """
        Starts a new conversation with the assistant.

        Args:
            title (str): The title of the conversation.
            (Optional) description (str): The description of the conversation. Default is None. 
        """
        try:
            new_conversation = Conversation({
                "title": title,
                "description": description,
            })
            self.conversations.append(new_conversation)
            self.active_conversation = new_conversation
            return new_conversation
        except ChatRunError as e:
            logger.error(f"Error starting chat: {e}")
            raise ChatAssistantError(f"Error starting chat: {e}. Please check your setup and try again.")
        
    def set_active_conversation(self, conversation):
        self.active_conversation = conversation

    async def send_message(self, message, conversation=None):
        """
        Sends a message to the assistant and periodically retrieves the Run object to update the status.

        Args:
            message (str): The message to send to the assistant.
            (Optional) conversation (object): The conversation to send the message to. Default is active conversation.
        """
        # If no conversation is provided and there's no active conversation, create a new one
        if conversation is None and self.active_conversation is None:
            conversation = await self.create_conversation("New Conversation")
            self.set_active_conversation(conversation)

        # If a conversation is provided but there's no active conversation, set the provided one as active
        elif conversation is not None and self.active_conversation is None:
            self.set_active_conversation(conversation)

        # If no conversation is provided but there's an active one, use the active one
        elif conversation is None and self.active_conversation is not None:
            conversation = self.active_conversation

        # The rest of your code...

        try:
            logger.info(f"Active conversation: {self.active_conversation.__dict__}")
            if self.active_conversation.get_message_count() == 0:
                # create new thread with initial message
                self.active_conversation.set_thread(await self._create_new_thread(message))
            else:
                # Create the new message
                logger.info(f"Sending message: {message}")
                await self.__http.request("post", f"threads/{self.active_conversation.get_thread_id()}/messages", {
                    "role": "user",
                    "content": message
                })

                # Update the thread
                thread = await self.__http.request("get", f"threads/{self.active_conversation.get_thread_id()}")
                self.active_conversation.set_thread(thread)
                logger.info(f"Thread updated: {self.active_conversation.get_thread()}")

            # Create a new run
            conversation.set_run(await self._create_new_run(self.active_conversation.get_thread_id()))


            logger.info(f"Message sent successfully: {message}")
            response = await self._get_message_response(conversation)        
            self.active_conversation.set_thread(await self.__http.request("get", f"threads/{self.active_conversation.get_thread_id()}"))

            return response

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise ChatMessageError(f"Error sending message: {e}. Please try again.")

    async def get_messages(self, conversation = None):
        """
        Gets messages from a conversation.

        Args:
            (Optional) conversation (object): The conversation to get messages from. Default is active conversation.
        """
        if conversation is None:
            if self.active_conversation is None:
                logger.error("No given conversation or active conversation to get messages from.")
                raise ChatMessageError("No conversations to get messages from. Please set an active conversation or start a new conversation.")
            conversation = self.active_conversation

        logger.info(f"Attempting to get messages from conversation: {conversation}")
        try:
            messages = await self.__http.request("get", f"threads/{conversation.thread.id}/messages")
            conversation["thread"].extend(messages.data)
            logger.info(f"Messages retrieved successfully from conversation: {conversation}")
            return messages
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            raise ChatMessageError(f"Error getting messages: {e}. Please try again.")
        
    async def delete_conversation(self, conversation_id):
        """
        Deletes a conversation.

        Args:
            conversation_id (str): The ID of the conversation to delete.
        """
        try:
            if self.active_conversation.id == conversation_id:
                conversation = self.active_conversation
                self.active_conversation = None
            else:
                for conversation in self.conversations:
                    if conversation.id == conversation_id:
                        conversation = conversation
            logger.info(f"Found conversation: {conversation.__dict__} to delete.")
            logger.info(f"Thread to Delete: {conversation.get_thread_id()}")
            deleted = await self.__http.request("delete", f"threads/{conversation.get_thread()['id']}")
            if deleted['deleted'] == True:
                self.conversations.remove(conversation)
                logger.info(f"Conversation with ID {conversation_id} deleted successfully.")
            return {
                "deleted": deleted['deleted'],
                "conversation": conversation.id
            }
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            raise ChatConversationError(f"Error deleting conversation: {e}. Please try again.")
