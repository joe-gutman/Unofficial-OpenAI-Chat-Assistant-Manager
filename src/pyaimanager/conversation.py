
import uuid
import datetime
from .utils.logging import logger
from .utils.exceptions import ChatAssistantError

class Conversation:
    def __init__(self, conversation):
        self.id = "conv_" + str(uuid.uuid4())
        self.title = conversation['title']
        self.description = conversation['description']
        self.created_at = datetime.datetime.now()
        self.__run = None
        self.__thread = None
        self.messages = []
        self.latest_response = None

    def set_thread(self, thread):
        self.__thread = thread

    def get_thread(self):
        return self.__thread
    
    def get_thread_id(self):
        return self.__thread['id']

    def set_run(self, run):
        self.__run = run
    
    def get_run(self):
        return self.__run
    
    def get_run_id(self):
        return self.__run['id']

    def get_message_count(self):
        return len(self.messages)
    
    def set_latest_response(self, response):
        self.latest_response = response

    def set_messages(self, messages):
        self.messages = messages

    def add_message(self, message):
        self.messages.append(message)

    def get_messages(self):
        return self.messages

    def get_messages_simple(self):
        messages = []
        for message in self.messages:
            messages.append(self._get_message_simple(message))
        return messages

    def _get_message_simple(self, message):
        print("simple message:", message)
        return {"role": message['role'], "text": message['content'][0]['text']['value']}
        
    
      
    