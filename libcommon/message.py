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
        return json.dumps(self.__dict__)

    def sendable(self):
        """Converts the message to a JSON UTF-8 bytestring ready for shipment.

        Returns:
            Bytes object where the first 8 bits represent length of the UTF-8
            encoded message as uint64 in byteorder 'big' of, after which the
            message as UTF-8 encoded JSON bytes object follows.
        """
        byteStr = str(self).encode('utf-8')
        return len(byteStr).to_bytes(8, byteorder='big', signed=False)+byteStr

    @classmethod
    def fromSendable(cls, jsonBytes):
        """Recreates the Message form a UTF-8 JSON byte string.

        **Warning:** in order for this to work ALL classes extending Message
        must have a default empty constructor.

        Returns:
            A new Message object created form the JSON byte string.
        """
        # Load the json string into a Python dict
        jsonDict = json.loads(jsonBytes.decode('utf-8'))
        new = cls()
        # Copy all keys into attributes
        for key, value in jsonDict.items():
            setattr(new, key, value)
        # Turn type into enum from JSON's string
        new.type = MessageType[jsonDict['type']]
        return new
