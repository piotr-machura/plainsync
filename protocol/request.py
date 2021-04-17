"""Request module.

Contains the `Request` classes sent by client to a server.
"""
from .message import Message, MessageType


class Request(Message):
    """Base request class.

    Used by the client to request response from a server.

    Items:
        userID: unique userID recognized by the server.
    """
    def __init__(self, userID=None, **kwargs):
        super().__init__(**kwargs)
        self.userID = userID


class AuthRequest(Request):
    """Authentication request class.

    Used by client to communicate the authentication credentials. `userID` is
    presumed to be `None` (the client is not authenticated).

    Items:
        user: username of the authenticating user.
        passwd: password of the authenticating user.
    """
    def __init__(self, user=None, passwd=None):
        super().__init__(
            userID=None,
            msgType=MessageType.AUTH,
        )
        self.user = user
        self.passwd = passwd


class PushRequest(Request):
    """Request to push local changes to the server.

    Items:
        userID: the ID of the user requesting file push.
        file: the file to be updated.
        content: the contents to update the file with.
    """
    def __init__(self, userID=None, file=None, content=''):
        super().__init__(
            userID=userID,
            msgType=MessageType.PUSH,
        )
        self.content=content
        self.file = file


class PullRequest(Request):
    """Request to pull changes from the server.

    Items:
        file: the file to be pulled.
    """
    def __init__(self, userID=None, file=None):
        super().__init__(
            userID=userID,
            msgType=MessageType.PULL,
        )
        self.file = file

class FileListRequest(Request):
    """Request listing files accessible by the current user.

    Simple wrapper for the regular Request with an approprieate message type.
    """
    def __init__(self, userID=None):
        super().__init__(
            userID=userID,
            msgType=MessageType.LIST_FILES,
        )
