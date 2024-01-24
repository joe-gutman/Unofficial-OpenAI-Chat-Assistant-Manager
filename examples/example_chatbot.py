# Import necessary modules
import asyncio
import os
# import .env file
from dotenv import load_dotenv
load_dotenv()

# import the AssistantManager class
from pyaimanager import AssistantManager

# import tools
# from example_tools import tools, functions
from example_tools import tools, functions


# Create a new chatbot class
class Chatbot:
    """
    A simple chatbot that can talk to you, and answer your questions.

    Initialization Parameters:
        api_key (str): An Open API key for the Assistant API.
        assistant_params (dict): A dictionary of parameters to create a new assistant.
    """
    def __init__(self, assistant_params):
        # Create a new assistant manager
        self.assistant_params = assistant_params
        # Initialize the assistant variable
        self.assistant = None

    # Due to the async nature of the chatbot, we need to initialize the assistant in an async function.
    # When you create the AssistantManager don't forget to pass in your OpenAI API key.
    async def initialize(self):
        self.assistant = await AssistantManager(os.getenv("OPENAI_API_KEY")).create_assistant(self.assistant_params)

    def get_user_input(self):
        return input("USER: ")
    
    # Creates a input/response loop that allows the user to chat with the chatbot until they exit.
    async def chat(self):
        while True:
            message = self.get_user_input()

            response = await self.assistant.send_message(message)
            print("\n" + self.assistant.name.upper() + ":", response['content'][0]['text']['value'], "\n")

    # The main function that starts the chatbot, handling the async event loop.
    def start_chat(self):
        # Create a new event loop
        loop = asyncio.get_event_loop()
        # Call the async initialize function
        loop.run_until_complete(self.initialize())
        # Due to the async nature of the chatbot, we need to run it in a separate event loop. 
        # Response times may vary depending on the response speed of the OpenAI API.
        loop.run_until_complete(self.chat())
        loop.close()


# Initialize a new chatbot, including the tools and functions from the example_tools.py file.
chatbot = Chatbot({
        "name": "Chatbot",
        "description": "A chatbot that can talk to you, and answer your questions.",
        "model": "gpt-4",
        "instructions": "You are a simple chatbot. You can answer questions and have a conversation with the user. You can also tell jokes and play games.",
        "tools": tools,
        "functions": functions
    })

# Start the chatbot
chatbot.start_chat()


