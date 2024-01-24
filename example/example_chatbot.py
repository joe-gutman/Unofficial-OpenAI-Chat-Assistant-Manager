from pyaimanager import AssistantManager
from dotenv import load_dotenv
import asyncio
import os
import sys

load_dotenv()

def quit():
    print("Chatbot: Goodbye!")
    sys.exit()

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
        self.assistant = None


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

    # So that we do not have to worry about the async nature of the chatbot, we can use this function to initialize the chatbot and start chatting with it.
    def start_chat(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.initialize())
        # Due to the async nature of the chatbot, we need to run it in a separate event loop. Response times may vary depending on the response speed of the OpenAI API.
        loop.run_until_complete(self.chat())
        loop.close()

# We can add custom tools to the chatbot to make it more useful. These tools can be used in the chatbot's instructions and then calls the quit() function.
tools = [{
    "type": "function",
    "function": {
        "name": "quit",
        "description": "End the chat",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}]

functions = {
    'quit': quit,
}

# Initialize a new chatbot
chatbot = Chatbot({
        "name": "Chatbot",
        "description": "A chatbot that can talk to you, and answer your questions.",
        "model": "gpt-4",
        "instructions": "You are a simple chatbot. You can answer questions and have a conversation with the user. You can also tell jokes and play games.",
        "tools": tools,
        "functions": functions
    })

# Start chatting with the chatbot, and pass in your OpenAI API key.
chatbot.start_chat()


