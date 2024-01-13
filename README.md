# OpenAI Chat Assistant Library (Unofficial)

This is an unofficial library that I've put together to make it easier to interact with the Beta OpenAI Assistant API. While it's not officially supported by OpenAI, it's built following the official OpenAI documentation. I've found it useful and I hope you will too!


## Features

- Connects to the OpenAI API using your API key
- Lets you create chat threads and assistants
- Sends and receives messages from the chat thread
- Handles errors related to the API, chat, and assistant
- Logs info about the chat process to the console and a file named `chat.log`

## Usage

First, import the library:

```python
from chat import Chat
```

Then, create a new chat instance with your OpenAI API key and assistant details:

```python
chat = Chat(api_key="your-api-key", assistant={"name": "assistant-name", "description": "assistant-description", "model": "assistant-model", "tools": "assistant-tools", "instructions": "assistant-instructions"})
```

You can send a message with the `send_message` method:

```python
chat.send_message("Hello, assistant!")
```

And retrieve the response with the `get_messages` method:

```python
messages = chat.get_messages()
```

Please note that the OpenAI API doesn't currently support streaming, so you'll need to manually call `get_messages` periodically to check for new responses. This is known as polling. OpenAI plans to add support for streaming in the near future to simplify this process. Once streaming is supported by the OpenAI API, it will be incorporated into this library as well.


## Error Handling

The library includes custom exceptions for handling errors related to the chat run, chat messages, the OpenAI API, and the chat assistant. These exceptions are `ChatRunError`, `ChatMessageError`, `ChatAPIError`, and `ChatAssistantError`, respectively.

## Logging

The library includes a logger that logs information about the chat process, including any errors that occur. The log messages are written to the console and a log file named `chat.log`.

<br>

## Disclaimer
Remember, this is an unofficial library and it's not supported by OpenAI. I've put it together to help make interacting with the OpenAI Assistant API easier. If you find any issues or have any improvements, feel free to contribute!