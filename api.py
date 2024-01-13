import openai
import logging
from .config import get_api_key

class ChatRunError(Exception):
    pass

class ChatMessageError(Exception):
    pass

class ChatAPIError(Exception):
    pass

class ChatAssistantError(Exception):
    pass

class Chat:
    def __init__(self, api_key, assistant):
        """
        Creates a new chat instance.

        Args:
            api_key (str): The OpenAI API key.
            assistant (dict): A dictionary containing the assistant's name, description, model, tools, and instructions.
        """

        self.api_key = get_api_key() 
        self.assistant = assistant
        self.thread = openai.beta.threads.create

        # check if api key was given
        if self.api_key == None:
            self.logger.error("No API key provided")
            raise ChatAPIError("No API key provided. Please provide a valid OpenAI API key."

)

        if self.assistant == None:
            raise ChatAssistantError("No assistant provided. Please provide an assistant dictionary with the following keys: ['name', 'description', 'model', 'tools', 'instructions'].")

        openai.api_key = self.api_key

        # Create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

        # Create a file handler
        file_handler = logging.FileHandler('chat.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def _run(self):
        """
        Checks if a run is active and creates a new one if not.
        """
        if not hasattr(self, "run") or self.run.status != "active":
            self._create_new_run()

    def _create_new_run(self):
        def _create_new_run(self):
            """
            Creates a new run, which is a single conversation thread with the assistant.
            """
            self.logger.info("Attempting to retrieve or create thread")
            # check if thread exists
            self.thread = openai.beta.threads.retrieve(
                thread_id=self.thread.id
            )
            self.logger.info("Thread retrieved successfully")
            # create thread if it doesn't exist
            self.logger.info("Attempting to create a new thread")
            self.run = openai.beta.threads.run.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions= self.assistant.instructions,
            )
            self.logger.info("Thread created successfully")

    def create_assistant(self, assistant):
        """
        Checks if an assistant exists, and creates one if it doesn't.

        Args:
            assistant (dict): A dictionary containing the assistant's name, description, model, tools, and instructions.
        """
        self.logger.info("Attempting to retrieve or create assistant")
        try:
            # check if assistant exists
            try:
                self.assistant = openai.beta.assistants.retrieve(
                    assistant_id=assistant.id
                )
                self.logger.info("Assistant retrieved successfully")
            except Exception as e:
                self.logger.info("Assistant does not exist")
                try: 
                    self._create_new_assistant(assistant)
                except Exception as e:
                    self.logger.error(f"Error creating assistant: {e}")
                    raise ChatAssistantError(f"Error creating assistant: {e}. Please ensure the assistant information is correct.")

    def _create_new_assistant(self, assistant):
        """
        Creates a new assistant.

        Args:
            assistant (dict): A dictionary containing the assistant's name, description, model, tools, and instructions.
        """
        self.logger.info("Verifying assistant information is valid")
        # check if name, description, model, tools, and instructions were given
        required_keys = ['name', 'description', 'model', 'tools', 'instructions']

        for key in required_keys:
            if not assistant.get(key):
                self.logger.error(f"Error creating assistant: No {key} provided.")
                raise ChatAssistantError(f"No {key} provided for the assistant. Please provide a value for {key}.")

        self.logger.info("Attempting to create a new assistant")
        try: 
            self.assistant = openai.beta.assistants.create(
                name=assistant.name,
                description=assistant.description,
                model=assistant.model,
                tools=assistant.tools,
                instructions=assistant.instructions,
            )
            self.logger.info("Assistant created successfully")
        except Exception as e:
            self.logger.error(f"Error creating assistant: {e}")
            raise ChatAssistantError(f"Error creating assistant. Please ensure the assistant information is correct.")



    def send_message(self, message):
        """
        Sends a message to the chat thread.

        Args:
            message (str): The content of the message to send.
        """
        self.logger.info(f"Attempting to send message: {message}")

        try:
            self._run()
        except Exception as e:
            self.logger.error(f"Error initiating chat: {e}")
            raise ChatRunError(f"Error initiating chat: {e}. Please check your setup and try again.")
            
        else:
            try:
                self.message = openai.beta.threads.message.create(
                    thread_id=self.thread.id,
                    role="user",
                    content=message
                )
                self.logger.info(f"Message sent successfully: {message}")
            except Exception as e: 
                self.logger.error(f"Error sending message: {e}")
                raise ChatMessageError(f"Error sending message: {e}. Please check the message content and try again.")



    def get_messages(self):
        """
        Checks if the run is completed, and if it is, returns the entire chat thread. A completed run means that the assistant has responded to the most recent message in the thread.
        """
        self.logger.info("Attempting to get messages")
        if not self.check_run():
            return {"success": False, "message": "The new response is not ready yet."}
        else:
            try:
                self.messages = openai.beta.threads.messages.list(
                    thread_id=self.thread.id,
                    run_id=self.run.id,
                )
                self.logger.info(f"Getting messages: {self.messages}")
                return {"success": True, "messages": self.messages}
            except Exception as e:
                self.logger.error(f"Error getting messages: {e}")
                raise ChatMessageError(f"Error getting messages: {e} Please ensure correct information was provided and try again later.")

    def _check_run(self):
        """
        Checks if the current run is completed. A run is a single conversation thread with the assistant with with the most recent message being the one that is being responded to.
        """
        self.logger.info("Checking if run is completed")
        try:
            if hasattr(self, "run"):
                if self.run.status == "completed":
                    return True
                else:
                    return False
        except Exception as e:
            self.logger.error(f"Error checking run status: {e}")
            raise ChatRunError(f"An error occurred while checking the run status: {e}. Please try again.")