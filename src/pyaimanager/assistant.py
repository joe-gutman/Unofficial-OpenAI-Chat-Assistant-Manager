import openai
from .logging_setup import setup_logger
from .exceptions import ChatAssistantError

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

    def __init__(self, assistant_data):
        self.id = assistant_data.id
        self.name = assistant_data.name
        self.object = assistant_data.object
        self.created_at = assistant_data.created_at
        self.description = assistant_data.description
        self.model = assistant_data.model
        self.instructions = assistant_data.instructions
        self.tools = assistant_data.tools
        self.file_ids = assistant_data.file_ids
        self.metadata = assistant_data.metadata
        self.conversations = []
        self.active_conversation = None

    def update(self, new_data):
        """
        Updates the Assistant's attributes with new data.

        Args:
            new_data (dict or object): A dictionary or object of new data.
        """
        if not isinstance(new_data, dict):
            new_data = new_data.name

        for key, value in new_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        return self

    def _check_run(self, run_id):
        self.logger.info(f"Checking run status for run ID: {run_id}")
        try:
            run = openai.beta.threads.runretrieve(run_id)
            if run['status'] == 'completed':
                self.logger.info(f"Run status is completed for run ID: {run_id}")
                return True
            else:
                self.logger.info(f"Run status is not completed for run ID: {run_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error checking run status: {e}")
            raise ChatRunError(f"Error checking run status {e}. Please try again.")

    def _create_new_thread(self, title, description = None):
        """
        Creates a new thread for the assistant.

        Returns:
            The new thread.
        """

        self.logger.info(f"Creating new thread with title: {title} and description: {description}")
        try:
            new_thread = openai.beta.threads.create()
            self.logger.info(f"New thread created with ID: {new_thread.id}")
            return new_thread
        except Exception as e:
            self.logger.error(f"Error creating new thread: {e}")
            raise ChatRunError(f"Error creating new thread: {e}. Please check your setup and try again.")

    def _create_new_run(self, thread_id):
        try:
            run = openai.beta.threads.runcreate(
                thread_id=thread_id,
                assistant_id=self.info.id,
                instructions=self.info.instructions,
            )
            self.logger.info(f"New run created with thread ID: {thread_id}")
            return run
        except Exception as e:
            self.logger.error(f"Error creating new run: {e}")
            raise ChatRunError(f"Error creating new run: {e}")

    def start_new_conversation(self, title, description = None):
        """
        Starts a new conversation with the assistant.

        Args:
            title (str): The title of the conversation.
            (Optional) description (str): The description of the conversation. Default is None. 
        """
        try:
            new_thread = self._create_new_thread()
            new_run = self._create_new_run(new_thread.id)
            new_conversation = {
                "title": title,
                "description": description,
                "created_at": new_run.created_at,
                "thread": new_thread,
                "run": new_run
            }
            self.conversations.append(new_conversation)
            self.active_conversation = new_conversation
        except ChatRunError as e:
            self.logger.error(f"Error starting chat: {e}")
            raise ChatAssistantError(f"Error starting chat: {e}. Please check your setup and try again.")
    
    def send_message(self, message, conversation = None):
        """
        Sends a message to the assistant.

        Args:
            message (str): The message to send to the assistant.
            (Optional) conversation (object): The conversation to send the message to. Default is active conversation.
        """
        if conversation is None:
            conversation = self.active_conversation

        self.logger.info(f"Attempting to send message: {message}")
        try:
            self.message = openai.beta.threads.message.create(
                thread_id=conversation["run"].id,
                role="user",
                content=message
            )
            conversation["thread"].append({"role": "user", "content": message})
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise ChatMessageError(f"Error sending message: {e}. Please try again.")

    def get_messages(self, conversation = None):
        """
        Gets messages from a conversation.

        Args:
            (Optional) conversation (object): The conversation to get messages from. Default is active conversation.
        """
        if conversation is None:
            if self.active_conversation is None:
                self.logger.error("No given conversation or active conversation to get messages from.")
                raise ChatMessageError("No conversations to get messages from. Please set an active conversation or start a new conversation.")
            conversation = self.active_conversation

        self.logger.info(f"Attempting to get messages from conversation: {conversation}")
        try:
            messages = openai.beta.threads.message.list(
                thread_id=conversation["run"].id
            )
            conversation["thread"].extend(messages.data)
            self.logger.info(f"Messages retrieved successfully from conversation: {conversation}")
            return messages
        except Exception as e:
            self.logger.error(f"Error getting messages: {e}")
            raise ChatMessageError(f"Error getting messages: {e}. Please try again.")
