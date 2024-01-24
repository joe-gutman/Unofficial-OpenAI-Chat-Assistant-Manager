import time
from .utils.logging import logger
from .utils.exceptions import ChatAssistantError
from .assistant import Assistant
from .utils.http_requests import HTTPRequest

class AssistantManager:
    """
    AssistantManager handles interactions with OpenAI's Assistant API,
    providing functionalities to manage and utilize different assistants.

    Initialization Parameters:
        api_key (str): An Open API key for the Assistant API.
        assistant_params (dict): A dictionary of parameters to create a new assistant.

    Lets you create, update, and delete assistants, as well as set an active assistant to use for sending messages.
    """
    def __init__(self, api_key):

        self.__http = HTTPRequest(api_key)
        self.assistants = []
        self.active_assistant = None
        self.__time_between_updates = 5 # minutes
        self.__last_updated = 0

    @classmethod
    async def create(cls, api_key):
        """
        Creates an AssistantManager instance.

        Args:
            api_key (str): An OpenAI API key.
        """
        logger.debug("Creating AssistantManager instance")
        instance = cls(api_key)
        try:
            await instance.synchronize_assistants()
        except Exception as e:
            logger.error(f"Failed to update local assistants: {e}")
            raise
        logger.info("AssistantManager instance created")
        return instance
    
# ---------------------------------------------------------------------------- #
#                     Assistant Data Fetching and Updating                     #
# ---------------------------------------------------------------------------- #

    async def _fetch_assistants_from_api(self):
        """
        Fetches the list of assistants from the API.

        Returns:
            assistants (list): The list of assistants fetched from the API.
        """
        try:
            response = await self.__http.request("get", "assistants")
        except Exception as e:
            logger.error(f"Error fetching assistants from API: {e}")
            raise ChatAssistantError(f"Error fetching assistants from API. Please check your OpenAI configuration.")
        else:
            if 'data' in response:
                logger.info("Assistants retrieved from API successfully.")
                return response['data']
            else:
                logger.error("Unexpected response format from API.")
                raise ChatAssistantError("Unexpected response format from API.")
            
    def is_data_stale(self):
        """
        Checks if the local list of assistants is stale.

        Returns:
            stale (bool): True if the list of assistants is stale, False otherwise.
        """
        return time.time() - self.__last_updated > self.__time_between_updates * 60

    # Updates the local list of assistants but only if the data is stale
    async def synchronize_assistants(self):
        """
        Checks if the local list of assistants is stale, and if so, synchronizes it with the list from the OpenAI API.

        Returns:
            assistants (list): The synchronized list of local assistants.
        """
        if not self.is_data_stale():
            logger.debug("Data is not stale. No need to synchronize.")
            return self.assistants

        try:
            logger.debug("Fetching list of assistants from API.")
            openai_assistants = await self._fetch_assistants_from_api()
            for openai_assistant in openai_assistants:
                # Check if the assistant exists locally
                local_assistant = await self._check_existing_assistant(openai_assistant['id'])
                if local_assistant:
                    # Update the local assistant
                    local_assistant.update(openai_assistant)
                else:
                    # Add the new assistant to the local list
                    self.assistants.append(Assistant(openai_assistant, self.__http, openai_assistant.get('functions', {})))
            self.__last_updated = time.time()
            logger.info("Local list of assistants synchronized successfully.")
        except Exception as e:
            logger.error(f"Error synchronizing list of assistants: {str(e)}")
            raise ChatAssistantError(f"Error synchronizing list of assistants: \n {str(e)}. \n Please check your OpenAI configuration or try again later.")
        return self.assistants
    
# ---------------------------------------------------------------------------- #
#                      Active Assistant Getting and Setting                    #
# ---------------------------------------------------------------------------- #

    def get_active_assistant(self):
        """
        Gets the active assistant. 

        Returns:
            assistant (object): The active assistant.
        """
        logger.info("Attempting to get active assistant")
        try: 
            logger.info(f"Active assistant: {self.active_assistant.__dict__}")
            return self.active_assistant
        except Exception as e:
            logger.error("No active assistant.")
            return None
        
    def set_active_assistant(self, assistant):
        """
        Sets the active assistant.

        Args:
            assistant (object): The assistant to set as active.

        Returns:
            assistant (object): The active assistant.
        """
        if assistant in self.assistants:
            self.active_assistant = assistant
            logger.info(f"Active assistant set: {self.active_assistant.name}")
        else:
            logger.error(f"Assistant not found: {assistant.name}")
            raise AssistantManagerError("The provided assistant is not found in the list of assistants.")
        return self.active_assistant

        
# ---------------------------------------------------------------------------- #
#                       Assistant Validation and Creation                      #
# ---------------------------------------------------------------------------- #

    def validate_assistant(self, assistant):
        """
        Validates the assistant dictionary.

        Args:
            assistant (dict): A dictionary containing the assistant's name, description, model, tools, and instructions, and optionally file_ids and metadata.

        Raises:
            ChatAssistantError: If a required key is missing from the assistant dictionary.
        """
        required_keys = ['name', 'description', 'model', 'instructions']

        for key in required_keys:
            if not assistant.get(key):
                logger.error(f"Error validating assistant: No {key} provided.")
                raise ChatAssistantError(f"No {key} provided for the assistant. Please provide a value for {key}.")

    async def create_assistant(self, assistant):
        """
        Checks if an assistant exists, and creates one if it doesn't.

        Args:
            assistant (dict): A dictionary containing the assistant's name, description, model, tools, and instructions, and optionally file_ids and metadata.
        """
        logger.info("Attempting to create assistant")

        # Validate the assistant
        self.validate_assistant(assistant)

        # Check if an assistant with this name already exists
        existing_assistant = await self._check_existing_assistant(assistant['name'])
        if existing_assistant:
            return existing_assistant

        # Create a new assistant
        return await self._create_new_assistant(assistant)

    async def _check_existing_assistant(self, id):
        for assistant in self.assistants:
            if assistant.id == id:
                return assistant
        return None
    async def _create_new_assistant(self, assistant):
        try: 
            # Filter assistant dict to only include keys expected by OpenAI API
            openai_keys = ['name', 'description', 'model', 'instructions', 'tools', 'file_ids', 'metadata']
            openai_args = {key: assistant[key] for key in openai_keys if key in assistant}

            # Create new assistant
            openai_assistant = await self.__http.request("post", "assistants", openai_args)
            combined_assistant = {**assistant, **openai_assistant}  # Combine dictionaries, giving priority to openai_assistant
            new_assistant = Assistant(combined_assistant, self.__http)
            logger.info(f"Created Assistant: {new_assistant.name}")
            return new_assistant
        except Exception as e:
            logger.error(f"Error creating assistant: {str(e)}")
            raise ChatAssistantError(f"Error creating assistant: \n {str(e)} \n Please ensure the assistant information is correct.")
        
# ---------------------------------------------------------------------------- #
#                          Assistant Retrieval Methods                         #
# ---------------------------------------------------------------------------- #

    async def get_assistant_by_name(self, name):
        """
        Retrieves an assistant by name from the local list.

        Args:
            name (str): The name of the assistant to retrieve.

        Returns:
            assistant (object): The assistant object retrieved, or None if no assistant was found.
        """
        await self.synchronize_assistants()
        assistant = next((assistant for assistant in self.assistants if assistant.name == name), None)
        return assistant

    async def get_assistant_by_id(self, id):
        """
        Retrieves an assistant by ID from the local list.

        Args:
            id (str): The ID of the assistant to retrieve.

        Returns:
            assistant (object): The assistant object retrieved, or None if no assistant was found.
        """
        await self.synchronize_assistants()
        assistant = next((assistant for assistant in self.assistants if assistant.id == id), None)
        return assistant
    
    async def get_assistants(self):
        """
        Retrieves all assistants from the local list, first updating the list if necessary.

        Returns:
            assistants (list): A list of all assistant objects.
        """
        try:
            # Refresh the local list of assistants before fetching them
            await self.synchronize_assistants()
            logger.info("Assistants retrieved from local list successfully.")
            return self.assistants
        except Exception as e:
            logger.error(f"Error retrieving assistants: {e}")
            raise ChatAssistantError("Error retrieving assistants. Please check your OpenAI configuration.")
        
# ---------------------------------------------------------------------------- #
#                            Assistant Modification                            #
# ---------------------------------------------------------------------------- #


    async def update_assistant(self, assistant, updated_info):
        """
        Updates an assistant by ID or name.

        Args:
            assistant (object): The assistant to update.
            updated_info (dict): A dictionary containing any attributes to update.
        """
        # Check if there are any attributes to update
        if not any(key in assistant.__dict__ for key in updated_info):
            logger.error("No attributes to update.")
            raise ChatAssistantError("No attributes to update. Please provide attributes to update.")
        
        # Update assistant
        try: 
            oai_updated_assistant = await self.__http.request("post", f"assistants/{assistant.id}", updated_info)
            updated_assistant = assistant.update(oai_updated_assistant)
            
            if oai_updated_assistant:
                return updated_assistant
        except Exception as e:
            logger.error(f"Error updating assistant: {e}")
            raise ChatAssistantError(f"Error updating assistant. Please ensure the information is correct.")
        
# ---------------------------------------------------------------------------- #
#                              Assistant Deletion                              #
# ---------------------------------------------------------------------------- #

    async def delete_assistant(self, assistant_id):
        """
        Deletes an assistant by ID.

        Args:
            assistant_id (str): The ID of the assistant to delete.

        Returns:
            (dict):
                deleted (bool): True if the assistant was deleted, False otherwise.
                id (str): The ID of the assistant that was to be deleted.
        """
        try: 
            assistant = await self.get_assistant_by_id(assistant_id)
            if not assistant:
                logger.info(f"No assistant found with ID: {assistant_id}. Assuming it's already deleted.")
                return {
                    "deleted": True,
                    "id": assistant_id
                }

            deleted = await self.__http.request("delete", f"assistants/{assistant_id}")

            if deleted['deleted']:
                logger.info(f"Deleted assistant: {assistant.name}")
                self.assistants.remove(assistant)
                if self.active_assistant and self.active_assistant.id == assistant.id:
                    self.active_assistant = None
                return {
                    "deleted": True,
                    "id": assistant.id
                }
        except Exception as e:
            logger.error(f"Error deleting assistant: {e}")
            raise ChatAssistantError(f"Error deleting assistant. Please ensure the id is correct.")