import openai
import pprint
from .logging_setup import setup_logger
from .exceptions import ChatAssistantError

class AssistantManager:
    def __init__(self, api_key):
        self.logger = setup_logger(__name__)

        if not api_key:
            self.logger.error("Error: No API key provided. Please provide an API key.")
            raise ChatAssistantError("No API key provided. Please provide an API key.")
        else:
            openai.api_key = api_key

        try: 
            self.assistants = self.get_assistants()
            self.active_assistant = None
        except Exception as e:
            self.logger.error(f"Error initializing assistant manager: {e}")
            raise ChatAssistantError(f"Error initializing assistant manager. Please check your OpenAI configuration.")

    def set_active_assistant(self, assistant):
        """
        Sets the active assistant.

        Args:
            assistant (dict): The assistant to set as active.
            set_active (bool): Whether to set the assistant as active or not.
        """
        self.logger.info(f"Setting assistant {assistant} as active")
        self.active_assistant = assistant

    def create_assistant(self, assistant):
        """
        Checks if an assistant exists, and creates one if it doesn't.

        Args:
            assistant (dict): A dictionary containing the assistant's name, description, model, tools, and instructions.
        """
        self.logger.info("Attempting to retrieve or create assistant")

        # Check if name, description, model, tools, and instructions were given
        required_keys = ['name', 'description', 'model', 'tools', 'instructions']

        for key in required_keys:
            if not assistant.get(key):
                self.logger.error(f"Error creating assistant: No {key} provided.")
                raise ChatAssistantError(f"No {key} provided for the assistant. Please provide a value for {key}.")

        try:
            # Try to get the assistant
            existing_assistant = self.get_assistant(assistant['name'])
            if existing_assistant:
                self.logger.info("Assistant with this name already exists")
                return existing_assistant
        except ChatAssistantError:
            # If the assistant doesn't exist, continue to create a new one
            pass

        self.logger.info("Attempting to create a new assistant")
        try: 
            new_assistant = openai.beta.assistants.create(
                name=assistant['name'],
                description=assistant['description'],
                model=assistant['model'],
                tools=assistant['tools'],
                instructions=assistant['instructions'],
            )
            self.logger.info("Assistant created successfully")
            return new_assistant
        except Exception as e:
            self.logger.error(f"Error creating assistant: {e}")
            raise ChatAssistantError(f"Error creating assistant. Please ensure the assistant information is correct.")


    def get_assistant(self, identifier, set_active=False):
        """
        Retrieves an assistant by ID or name.

        Args:
            identifier (str): The ID or name of the assistant to retrieve.
        """
        try:
            assistant = openai.beta.assistants.list(
                assistant_id=identifier
            )
            self.logger.info(f"Assistant retrieved successfully: {assistant}")
            if set_active:
                self.set_active_assistant(assistant)
            return assistant
        except Exception as e:
            self.logger.error(f"Error getting assistant: {e}")
            raise ChatAssistantError(f"Error getting assistant. Please ensure the identifier is correct.")

    def get_assistants(self):
        """
        Retrieves all assistants.
        """
        try:
            response = openai.beta.assistants.list()
            self.assistants = response.data
                            
            self.logger.info("Assistants retrieved successfully.")
            return self.assistants
        except Exception as e:
            self.logger.error(f"Error getting assistants: {e}")
            raise ChatAssistantError(f"Error getting assistants. Please check your OpenAI configuration.")

    def update_assistant(self, assistant):
        """
        Updates an assistant by ID or name.

        Args:
            identifier (str): The ID or name of the assistant to update.
            assistant (dict): A dictionary containing the assistant's name, description, model, tools, and instructions.
        """
        try: 
            old_assistant = self.get_assistant(assistant['name'])
            new_assistant = assistant
            # validate assistant information
            updated = openai.beta.assistants.update(
                assistant_id= old_assistant.id,
                name=new_assistant.get('name', old_assistant.name),
                description=new_assistant.get('description', old_assistant.description),
                model=new_assistant.get('model', old_assistant.model),
                tools=new_assistant.get('tools', old_assistant.tools),
                instructions=new_assistant.get('instructions', old_assistant.instructions),
            )

            # update returns modified assistant object. So check if the assistant is returned.
            if updated:
                self.logger.info(f"Updated assistant: {updated}")
                # update assistant in self.assistants
                self.assistants = self.get_assistants()
                return updated
        except Exception as e:
            self.logger.error(f"Error updating assistant: {e}")
            raise ChatAssistantError(f"Error updating assistant. Please ensure the information is correct.")

    def delete_assistant(self, identifier):
        """
        Deletes an assistant by ID or name.

        Args:
            identifier (str): The ID or name of the assistant to delete.
        """
        try: 
            assistant = self.get_assistant(identifier)
            deleted = openai.beta.assistants.delete(assistant_id=assistant.id)

            if deleted.deleted:
                self.logger.info(f"Deleted assiststant: {assistant}")
                return deleted
        except Exception as e:
            self.logger.error(f"Error deleting assistant: {e}")
            raise ChatAssistantError(f"Error deleting assistant. Please ensure the identifier is correct.")
