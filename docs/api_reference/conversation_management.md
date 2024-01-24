# Chat Management API Reference

This document provides detailed information about the `ChatManager` class in PyAIManager.

## Class: ChatManager

The `ChatManager` class is used to manage chat threads with an assistant in PyAIManager.

### Method: `__init__(self, api_key: str, assistant: dict) -> None`

Initializes a new instance of the `ChatManager` class.

#### Parameters

- `api_key` (str): The API key for OpenAI.
- `assistant` (dict): The assistant to chat with. This should be a dictionary containing the assistant's ID and name.

#### Example

```python
chat = ChatManager(api_key="your_api_key", assistant={"id": "assistant_id", "name": "assistant_name"})
```

### Method: `send_message(self, message: str) -> None`

Sends a message to the chat thread.

#### Parameters

- `message` (str): The content of the message to send.

#### Example

```python
chat.send_message(message="Hello, assistant!")
```

### Method: `get_messages(self) -> dict`

Checks if the run is completed, and if it is, returns the entire chat thread. A completed run means that the assistant has responded to the most recent message in the thread.

#### Example

```python
messages = chat.get_messages()
```