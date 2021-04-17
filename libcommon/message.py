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
    UNAUTH = 'UNAUTH'
    AUTH = 'AUTH'
    PUSH = 'PUSH'
    PULL = 'PULL'


class Message():
    """Message class built from a dictionary.

    Turned from/into a JSON string when transmitted over TCP as means of
    client-server communication.

    Items:
        'type' - MessageType enum specifying the type of message.
        'content' - string specifying message contents.
    """
    def __init__(self, msgType=MessageType.NONE, content=''):
        super().__init__()
        self.type = msgType
        self.content = content

    def __str__(self):
        return str(self.__dict__)

    def toJSON(self):
        """Converts the message to a JSON string ready for shipment.

        Returns:
            A viable JSON string obtained from the message.
        """

        return json.dumps( self.__dict__)

    @classmethod
    def fromJSON(cls, jsonStr):
        """Recreates the Message form a JSON string.

        Returns:
            A new Message object created form the JSON string.
        """
        # Load the json string into a Python dict
        jsonDict = json.loads(jsonStr)
        # Convert the message type to enum
        new = cls()
        # Copy all other keys 'as-is'
        for key, value in jsonDict.items():
            setattr(new, key, value)
        new.type = MessageType[jsonDict['type']]
        return new
