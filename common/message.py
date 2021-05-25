"""Message module.

A message is the basic object transferred over TCP as plain text as means of
client-server communication.
"""
from enum import Enum
import json


class MessageType(str, Enum):
    """Message type enum.

    Indicates the type of transmitted message.
    """
    NONE = 'NONE'
    OK = 'OK'
    ERR = 'ERR'
    AUTH = 'AUTH'
    PUSH = 'PUSH'
    PULL = 'PULL'
    LIST_FILES = 'LIST_FILES'
    NEW_FILE = 'NEW_FILE'


class Message():
    """Message class.

    Turned from/into a JSON string when transmitted over TCP as means of
    client-server communication.

    Items:
       type: MessageType enum specifying the type of message.
    """
    def __init__(self, msgType=MessageType.NONE):
        super().__init__()
        self.type = msgType

    def __str__(self):
        return self.toJSON()

    def toJSON(self):
        """Converts the message to a JSON string.

        Returns:
            A valid JSON string representation of the message.
        """
        return json.dumps(self.__dict__)

    @classmethod
    def fromJSON(cls, jsonStr):
        """Recreates the Message form a UTF-8 JSON byte string.

        **Warning:** in order for this to work ALL classes extending Message
        must have a default empty constructor.

        Args:
            jsonStr: valid JSON string obtained  with Message.toJSON.

        Returns:
            A new Message object created form the JSON byte string.
        """
        # Load the json string into a Python dict
        jsonDict = json.loads(jsonStr)
        new = cls()
        # Copy all keys into attributes
        for key, value in jsonDict.items():
            setattr(new, key, value)
        # Turn type into enum from JSON's string
        new.type = MessageType[jsonDict['type']]
        return new
