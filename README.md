# OpenAI Chat Assistant Library (Unofficial) :robot:

> :warning: **IMPORTANT:** This library is **currently under development** and is **NOT ready for use in production**. More detailed information will be added prior to the stable release.

This is an unofficial library that I've put together to make it easier to interact with the Beta OpenAI Assistant API. While it's not officially supported by OpenAI, it's built following the official OpenAI documentation. I've found it useful and I hope you will too!



## Features

- Connects to the OpenAI API using your API key
- Manages assistants and chat threads
- Sends and receives messages for assistant chat threads
- Handles errors related to the API, chat, and assistant
- Logs info about the chat process to the console and a file named `chat.log`

## Usage

> :warning: **IMPORTANT:** The usage instructions below are **subject to change** as this library is currently under development. They may not be accurate.


```python
# First, import the necessary modules:
from assistant_management import AssistantManager
from chat_management import ChatManager

# Then, create a new assistant manager and chat manager with your OpenAI API key:
assistant_manager = AssistantManager(api_key="your-api-key")
chat_manager = ChatManager(api_key="your-api-key")

# You can create an assistant with the `create_assistant` method:
assistant = assistant_manager.create_assistant(
    name="Program Teacher",
    description="A helpful programming assistant",
    model="gpt-4-1106-preview",
    tools=[{"type":"code_interpreter"}],
    instructions="This assistant can answer questions about programming."
)

# And send a message with the `send_message` method:
chat_manager.send_message(assistant.id, "Hello, assistant!")

# And retrieve the response with the `get_messages` method:
messages = chat_manager.get_messages(assistant.id)
```

## :loudspeaker: Important Note on Message Retrieval

> :exclamation: **Please note that the OpenAI API doesn't currently support streaming, so you'll need to manually call `get_messages` periodically to check for new responses. This is known as polling. OpenAI plans to add support for streaming in the near future to simplify this process. Once streaming is supported by the OpenAI API, it will be incorporated into this library as well.**

## Error Handling

The library includes custom exceptions for handling errors related to the chat run, chat messages, the OpenAI API, and the chat assistant. These exceptions are `ChatRunError`, `ChatMessageError`, `ChatAPIError`, and `ChatAssistantError`, respectively.

##  Logging

The library includes a logger that logs information about the chat process, including any errors that occur. The log messages are written to the console and a log file named `chat.log`.

## Documentation

For more information on how to use this project, see the [documentation](docs/).

## Disclaimer

Remember, this is an unofficial library and it's not supported by OpenAI. I've put it together to help make interacting with the OpenAI Assistant API easier. If you find any issues or have any improvements, feel free to contribute!
