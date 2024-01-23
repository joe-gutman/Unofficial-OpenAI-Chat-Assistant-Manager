import time
from .utils.logging import logger
from .utils.exceptions import ChatAssistantError
from .assistant import Assistant
from .utils.http_requests import HTTPRequest

class AssistantManager:
    """
    AssistantManager handles interactions with OpenAI's Assistant API,
    providing functionalities to manage and utilize different assistants.
    """
    def __init__(self, api_key):

        self.__http = HTTPRequest(api_key)
        self.assistants = []
        self.active_assistant = None
        self.__time_between_updates = 5 # minutes
        self.__last_updated = 0

    @classmethod
    async def create(cls, api_key):
        instance = cls(api_key)
        await instance._update_local_assistants()
        return instance

    def _convert_to_assistant(self, openai_assistant):
        """
        Converts a an OpenAI assistant object to an Assistant object.

        Args:
            openai_assistant (object): The OpenAI assistant object to convert.

        Returns:
            assistant (object): The converted Assistant object.

        """
        # logger.info(f"Converting assistant: {openai_assistant['name']}")
        assistant = Assistant(openai_assistant, self.__http)
        
        logger.info(f"Converted assistant: {assistant.name}")
        return assistant

    async def _fetch_assistants_from_api(self):
        """
        Fetches the list of assistants from the API.

        Returns:
            assistants (list): The list of assistants fetched from the API.
        """
        try:
            response = await self.__http.request("get", "assistants")
            logger.info("Assistants retrieved from API successfully.")
            return response['data']
        except Exception as e:
            logger.error(f"Error fetching assistants from API: {e}")
            raise ChatAssistantError(f"Error fetching assistants from API. Please check your OpenAI configuration.")

    async def _update_local_assistants(self):
        """
        Fetches the list of assistants from the OpenAI API.

        Args:
            assistants_data (list): The list of assistants data to convert and update the local list with.
        """
        # Check if the local list of assistants needs to be updated
        if time.time() - self.__last_updated < self.__time_between_updates * 60:
            logger.info("Local list of assistants is up to date.")
            return self.assistants
        else:
            try:
                # logger.info("Fetching list of assistants.")
                openai_assistants = await self._fetch_assistants_from_api()
                assistants = []
                # Convert each API assistant to a local assistant
                for assistant in openai_assistants:
                    assistants.append(self._convert_to_assistant(assistant))
                self.assistants = assistants
                logger.info("List of assistants fetched successfully.")
                return self.assistants
            except Exception as e:
                logger.error(f"Error fetching list of assistants: {str(e)}")
                raise ChatAssistantError(f"Error fetching list of assistants: \n {str(e)}. \n Please check your OpenAI configuration or try again later.")

    def set_active_assistant(self, assistant):
        """
        Sets the active assistant.

        Args:
            assistant (object): The assistant to set as active.
        """
        self.active_assistant = assistant
        logger.info(f"Active assistant: {self.active_assistant.__dict__}")
        return self.active_assistant

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
        

    async def create_assistant(self, assistant):
        """
        Checks if an assistant exists, and creates one if it doesn't.

        Args:
            assistant (dict): A dictionary containing the assistant's name, description, model, tools, and instructions, and optionally file_ids and metadata.
        """
        logger.info("Attempting to create assistant")

        # Check if name, description, model, and instructions were given
        required_keys = ['name', 'description', 'model', 'instructions']

        for key in required_keys:
            if not assistant.get(key):
                logger.error(f"Error creating assistant: No {key} provided.")
                raise ChatAssistantError(f"No {key} provided for the assistant. Please provide a value for {key}.")

        try:
            # Check if an assistant with this name already exists
            existing_assistant = await self.get_assistant_by_name(assistant['name'])
            if existing_assistant:
                logger.info("Assistant with this name already exists")
                return existing_assistant
        except ChatAssistantError:
            # If the assistant doesn't exist, continue to create a new one
            pass

        # Create a new assistant
        try: 
            keys = ['name', 'description', 'model', 'instructions', 'tools', 'file_ids', 'metadata']
            create_args = {}
            for key in keys:
                if key in assistant:
                    create_args[key] = assistant[key]

            new_assistant = self._convert_to_assistant(await self.__http.request("post", "assistants", create_args))
            logger.info(f"Created Assistant: {new_assistant.__dict__}")
            return new_assistant
        except Exception as e:
            logger.error(f"Error creating assistant: {str(e)}")
            raise ChatAssistantError(f"Error creating assistant: \n {str(e)} \n Please ensure the assistant information is correct.")

    async def get_assistant_by_name(self, name):
        """
        Retrieves an assistant by name from the local list.

        Args:
            name (str): The name of the assistant to retrieve.

        Returns:
            assistant (object): The assistant object retrieved, or None if no assistant was found.
        """
        assistants = await self._update_local_assistants()
        for assistant in assistants:
            if assistant.name == name:
                return assistant
        return None

    async def get_assistant_by_id(self, id):
        """
        Retrieves an assistant by ID from the local list.

        Args:
            id (str): The ID of the assistant to retrieve.

        Returns:
            assistant (object): The assistant object retrieved, or None if no assistant was found.
        """
        assistants = await self._update_local_assistants()
        for assistant in assistants:
            if assistant.id == id:
                return assistant
        return None

    async def get_assistants(self):
        """
        Retrieves all assistants from the local list.

        Returns:
            assistants (list): A list of all assistant objects.
        """
        try:
            # Refresh the local list of assistants before fetching them
            assistants = await self._update_local_assistants()
            logger.info("Assistants retrieved from local list successfully.")
            return assistants
        except Exception as e:
            logger.error(f"Error retrieving assistants: {e}")
            raise ChatAssistantError("Error retrieving assistants. Please check your OpenAI configuration.")

    async def update_assistant(self, assistant, updated_info):
        """
        Updates an assistant by ID or name.

        Args:
            assistant (object): The assistant to update.
            updated_info (dict): A dictionary containing any attributes to update.
        """
        # compare attributes of assistant and updated_info to see if there are any attributes to update
        assistant_attributes = assistant.__dict__.keys()
        updated_info_keys = updated_info.keys()
        # the intersection of the two sets will be the attributes to update
        intersection = set(assistant_attributes).intersection(updated_info_keys)
        if not intersection:
            logger.error("No attributes to update.")
            raise ChatAssistantError("No attributes to update. Please provide attributes to update.")
        
        # update assistant
        try: 
            oai_updated_assistant = await self.__http.request("post", f"assistants/{assistant.id}", updated_info)
            updated_assistant = assistant.update(oai_updated_assistant)
            
            if oai_updated_assistant:
                return updated_assistant
        except Exception as e:
            logger.error(f"Error updating assistant: {e}")
            raise ChatAssistantError(f"Error updating assistant. Please ensure the information is correct.")

    async def delete_assistant(self, assistant_id):
        """
        Deletes an assistant by ID.

        Args:
            assistant_id (str): The ID of the assistant to delete.
        """
        try: 
            assistant = await self.get_assistant_by_id(assistant_id)
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