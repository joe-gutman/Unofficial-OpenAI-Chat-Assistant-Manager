import openai
import re
import time
from .logging_setup import setup_logger
from .exceptions import ChatAssistantError
from .assistant import Assistant

class AssistantManager:
    """
    AssistantManager handles interactions with OpenAI's Assistant API,
    providing functionalities to manage and utilize different assistants.
    """
    def __init__(self, api_key):
        self.logger = setup_logger(__name__)
        self.setup_api_key(api_key)
        self.assistants = []
        self.last_update = 0
        self.update_interval = 5 # minutes
        self._update_local_assistants()

    def setup_api_key(self, api_key):
        """
        Sets up the OpenAI API key.
        """
        if not api_key:
            self.logger.error("Error: No API key provided for AssistantManager.")
            raise ChatAssistantError("No API key provided. Please provide an API key.")
        else:
            openai.OpenAI(api_key)
            self.logger.info("OpenAI API key set successfully.")

    def _convert_to_assistant(self, openai_assistant):
        """
        Converts a an OpenAI assistant object to an Assistant object.

        Args:
            openai_assistant (object): The OpenAI assistant object to convert.

        Returns:
            assistant (object): The converted Assistant object.

        """
        self.logger.info(f"Converting assistant: {openai_assistant.name}")
        assistant = Assistant(openai_assistant)
        self.logger.info(f"Converted assistant: {assistant.name}")
        return assistant

    def _fetch_assistants_from_api(self):
        """
        Fetches the list of assistants from the API.

        Returns:
            assistants (list): The list of assistants fetched from the API.
        """
        try:
            response = openai.beta.assistants.list()
            self.logger.info("Assistants retrieved from API successfully.")
            return response.data
        except Exception as e:
            self.logger.error(f"Error fetching assistants from API: {e}")
            raise ChatAssistantError(f"Error fetching assistants from API. Please check your OpenAI configuration.")

    def _update_local_assistants(self):
        """
        Makes sure that the local list of assistants is up to date against the OpenAI API.

        Args:
            assistants_data (list): The list of assistants data to convert and update the local list with.
        """
        try:
            # Check if the local list of assistants needs to be updated
            if time.time() - self.last_update < self.update_interval * 60:
                self.logger.info("Local list of assistants is up to date.")
                return
            else: 
                self.last_update = time.time()
                self.logger.info("Updating local list of assistants.")
                openai_assistants = self._fetch_assistants_from_api()
                assistants = []
                # Check if the openai_assistant exists in the local list of assistants, and update it if it does
                for api_assistant in openai_assistants:
                    for local_assistant in self.assistants:
                        if local_assistant.id == api_assistant.id:
                            local_assistant.update(api_assistant)
                            assistants.append(local_assistant)
                            break
                    else:
                        assistants.append(self._convert_to_assistant(api_assistant))
                self.assistants = assistants
                self.logger.info("Local list of assistants updated successfully.")
        except Exception as e:
            self.logger.error(f"Error updating local list of assistants: {str(e)}")
            raise ChatAssistantError(f"Error updating local list of assistants: \n {str(e)}. \n Please check your OpenAI configuration or try again later.")

    def set_active_assistant(self, assistant):
        """
        Sets the active assistant.

        Args:
            assistant (object): The assistant to set as active.
        """
        self.active_assistant = assistant
        self.logger.info(f"Active assistant: {self.active_assistant.__dict__}")
        return self.active_assistant

    def get_active_assistant(self):
        """
        Gets the active assistant. 

        Returns:
            assistant (object): The active assistant.
        """
        self.logger.info("Attempting to get active assistant")
        try: 
            self.logger.info(f"Active assistant: {self.active_assistant.__dict__}")
            return self.active_assistant
        except Exception as e:
            self.logger.error("No active assistant.")
            return None
        

    def create_assistant(self, assistant):
        """
        Checks if an assistant exists, and creates one if it doesn't.

        Args:
            assistant (dict): A dictionary containing the assistant's name, description, model, tools, and instructions.
        """
        self.logger.info("Attempting to create assistant")

        # Check if name, description, model, and instructions were given
        required_keys = ['name', 'description', 'model', 'instructions']

        for key in required_keys:
            if not assistant.get(key):
                self.logger.error(f"Error creating assistant: No {key} provided.")
                raise ChatAssistantError(f"No {key} provided for the assistant. Please provide a value for {key}.")

        try:
            # Try to get the assistant
            existing_assistant = self.get_assistant_by_name(assistant['name'])
            if existing_assistant:
                self.logger.info("Assistant with this name already exists")
                return existing_assistant
        except ChatAssistantError:
            # If the assistant doesn't exist, continue to create a new one
            pass

        self.logger.info("Attempting to create a new assistant")
        try: 
            keys = ['name', 'description', 'model', 'instructions', 'tools', 'file_ids', 'metadata']
            create_args = {key: assistant[key] for key in keys if key in assistant}

            new_oai_assistant = openai.beta.assistants.create(
                **{key: assistant[key] for key in keys if key in assistant}
            )
            new_assistant = self._convert_to_assistant(new_oai_assistant)
            self.logger.info(f"Created Assistant: {type(new_assistant)} : {new_assistant.__dict__}")
            self._update_local_assistants()
            return new_assistant
        except Exception as e:
            self.logger.error(f"Error creating assistant: {str(e)}")
            raise ChatAssistantError(f"Error creating assistant: \n {str(e)} \n Please ensure the assistant information is correct.")

    def get_assistant_by_name(self, name):
        # Retry fetching the assistant a few times if _update_local_assistants was called recently
        if time.time() - self.last_update < 20:
            for _ in range(5):
                for assistant in self.assistants:
                    if assistant.name == name:
                        return assistant
                time.sleep(10)  # Wait for 2 seconds before retrying
                self._update_local_assistants()
        else:
            for assistant in self.assistants:
                if assistant.name == name:
                    return assistant
        return None

    def get_assistant_by_id(self, id):
        # Retry fetching the assistant a few times if _update_local_assistants was called recently
        if time.time() - self.last_update < 10:
            for _ in range(5):
                for assistant in self.assistants:
                    if assistant.id == id:
                        return assistant
                time.sleep(10)  # Wait for 2 seconds before retrying
                self._update_local_assistants()
        else:
            for assistant in self.assistants:
                if assistant.id == id:
                    return assistant
        return None

    def get_assistants(self):
        """
        Retrieves all assistants from the local list.

        Returns:
            assistants (list): A list of all assistant objects.
        """
        try:
            # Refresh the local list of assistants before fetching them
            self._update_local_assistants()
            self.logger.info("Assistants retrieved from local list successfully.")
            return self.assistants
        except Exception as e:
            self.logger.error(f"Error retrieving assistants: {e}")
            raise ChatAssistantError("Error retrieving assistants. Please check your OpenAI configuration.")

    def update_assistant(self, assistant, updated_info):
        """
        Updates an assistant by ID or name.

        Args:
            assistant (object): The assistant to update.
            updated_info (dict): A dictionary containing any attributes to update.
        """
        # compare attributes of assistant and updated_info to see if there are any attributes to update
        assistant_attributes = assistant.__dict__.keys()
        updated_info_keys = updated_info.keys()
        intersection = set(assistant_attributes).intersection(updated_info_keys)
        if not intersection:
            self.logger.error("No attributes to update.")
            raise ChatAssistantError("No attributes to update. Please provide attributes to update.")
        
        # update assistant
        try: 
            # validate assistant information
            updated_oai_assistant = openai.beta.assistants.update(
                assistant_id= assistant.id,
                name=updated_info.get('name', assistant.name),
                description=updated_info.get('description', assistant.description),
                model=updated_info.get('model', assistant.model),
                tools=updated_info.get('tools', assistant.tools),
                instructions=updated_info.get('instructions', assistant.instructions),
                file_ids=updated_info.get('file_ids', assistant.file_ids),
                metadata=updated_info.get('metadata', assistant.metadata),
            )

            # update assistant object using the Assistant's update method
            updated_assistant = assistant.update(updated_oai_assistant.__dict__)

            # update returns modified assistant object. So check if the assistant is returned.
            if updated_oai_assistant:
                self.logger.info(f"Updated assistant: {type(updated)} : {updated.__dict__}")
                # update assistant in self.assistants
                self.assistants = self.get_assistants()
                return updated_assistant
        except Exception as e:
            self.logger.error(f"Error updating assistant: {e}")
            raise ChatAssistantError(f"Error updating assistant. Please ensure the information is correct.")

    def delete_assistant(self, assistant_id):
        """
        Deletes an assistant by ID.

        Args:
            assistant_id (str): The ID of the assistant to delete.
        """
        try: 
            assistant = self.get_assistant_by_id(assistant_id)
            deleted = openai.beta.assistants.delete(assistant_id=assistant.id)

            if deleted.deleted:
                self.logger.info(f"Deleted assistant: {assistant.name}")
                self.assistants.remove(assistant)
                if self.active_assistant and self.active_assistant.id == assistant.id:
                    self.active_assistant = None
                return deleted
        except Exception as e:
            self.logger.error(f"Error deleting assistant: {e}")
            raise ChatAssistantError(f"Error deleting assistant. Please ensure the id is correct.")