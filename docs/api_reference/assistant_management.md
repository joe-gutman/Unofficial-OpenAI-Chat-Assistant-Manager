# Assistant Management API Reference

This document provides detailed information about the `AssistantManager` class in PyAIManager.

## Class: AssistantManager

The `AssistantManager` class is used to manage assistants in PyAIManager.

### Method: `__init__(self, api_key: str) -> None`

Initializes a new instance of the `AssistantManager` class.

#### Parameters

- `api_key` (str): The API key for OpenAI.

#### Example

```python
manager = AssistantManager(api_key="your_api_key")
```

### Method: `set_active_assistant(self, assistant: dict) -> None`

Sets the active assistant. The active assistant is the one that will be used for all subsequent operations.

#### Parameters

- `assistant` (dict): The assistant to set as active. This should be a dictionary containing the assistant's ID and name.

#### Example

```python
manager.set_active_assistant(assistant={"id": "assistant_id", "name": "assistant_name"})
```

### Method: `create_assistant(self, assistant: dict) -> dict`

Checks if an assistant exists, and creates one if it doesn't. Returns the newly created assistant.

#### Parameters

- `assistant` (dict): A dictionary containing the assistant's name, description, model, tools, and instructions.

#### Example

```python
new_assistant = manager.create_assistant(assistant={"name": "assistant_name", "description": "assistant_description", "model": "assistant_model", "tools": ["tool1", "tool2"], "instructions": "assistant_instructions"})
```

### Method: `get_assistant(self, identifier: str, set_active: bool = False) -> dict`

Retrieves an assistant by ID or name. If `set_active` is `True`, the retrieved assistant will be set as the active assistant.

#### Parameters

- `identifier` (str): The ID or name of the assistant to retrieve.
- `set_active` (bool, optional): Whether to set the retrieved assistant as active. Defaults to False.

#### Example

```python
assistant = manager.get_assistant(identifier="assistant_id", set_active=True)
```

### Method: `get_assistants(self) -> list`

Retrieves all assistants. Returns a list of dictionaries, each representing an assistant.

#### Example

```python
assistants = manager.get_assistants()
```

### Method: `update_assistant(self, assistant: dict) -> dict`

Updates an assistant by ID or name. Returns the updated assistant.

#### Parameters

- `assistant` (dict): A dictionary containing the assistant's name, description, model, tools, and instructions.

#### Example

```python
updated_assistant = manager.update_assistant(assistant={
    "name":"Data visualizer",
    "description":"You are great at creating beautiful data visualizations. You analyze data present in .csv files, understand trends, and come up with data visualizations relevant to those trends. You also share a brief text summary of the trends observed.",
    "model":"gpt-4-1106-preview",
    "tools":[{"type": "code_interpreter"}]
    })
```

### Method: `delete_assistant(self, identifier: str) -> dict`

Deletes an assistant by ID or name. Returns the deleted assistant.

#### Parameters

- `identifier` (str): The ID or name of the assistant to delete.

#### Example

```python
deleted_assistant = manager.delete_assistant(identifier="assistant_id")
```