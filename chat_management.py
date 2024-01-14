# chat_management.py
import openai
from .logging_setup import setup_logger
from .exceptions import ChatRunError, ChatMessageError
from .assistant_management import AssistantManager

class ChatManager:
    def __init__(self, api_key, assistant):
        self.api_key = api_key
        self.assistant = assistant
        self.thread = openai.beta.threads.create

    def _run(self):
        """
        Checks if a run is active and creates a new one if not.
        """
        if not hasattr(self, "run") or self.run.status != "active":
            self._create_new_run()

    def _create_new_run(self):
        """
        Creates a new run, which is a single conversation thread with the assistant.
        """
        self.logger.info("Attempting to retrieve or create thread")
        # check if thread exists
        self.thread = openai.beta.threads.retrieve(
            thread_id=self.thread.id
        )
        self.logger.info("Thread retrievedsuccessfully")
        # create thread if it doesn't exist
        self.logger.info("Attempting tocreate a new thread")
        self.run = openai.beta.threads.runcreate(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions= self.assistantinstructions,
        )
        self.logger.info("Thread created successfully")

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