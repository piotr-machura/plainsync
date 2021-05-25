"""Request module.

Contains the `Request` classes sent by the client to a server.
"""
import json
from common.message import Message, MessageType


class Request(Message):
    """Base request class.

    Used by the client to request response from a server.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AuthRequest(Request):
    """Authentication request class.

    Used by the client to communicate the authentication credentials. The server
    responds with an `AuthResponse` containing the assigned session ID or
    `ErrResponse`.

    Items:
        user: username of the authenticating user.
        passwd: password of the authenticating user.
    """
    def __init__(self, user=None, passwd=None):
        super().__init__(msgType=MessageType.AUTH, )
        self.user = user
        self.passwd = passwd


class PushRequest(Request):
    """Push request class.

    Used by the client to push local changes to the server. The server responds
    with `OkResponse` if everything went fine or `ErrResponse`.

    Items:
        fileID: the ID of file to be updated.
        content: the contents to update the file with.
    """
    def __init__(self, fileID=None, content=''):
        super().__init__(msgType=MessageType.PUSH, )
        self.content = content
        self.fileID = fileID

    def __str__(self):
        dictionary = self.__dict__.copy()
        del dictionary['content']
        return json.dumps(dictionary)



class PullRequest(Request):
    """Pull request class.

    Used by the client to to pull changes from the server. The server responds
    with `PullResponse` containing the file contents or `ErrResponse`.

    Items:
        fileID: the ID of the file to be pulled.
    """
    def __init__(self, fileID=None):
        super().__init__(msgType=MessageType.PULL, )
        self.fileID = fileID


class FileListRequest(Request):
    """File list request class.

    Used by the client to request listing files the user has access to. The
    server responds with `FileListResponse`, containing a dictionary of (file
    ID, (info)) pairs, where the ID is the unique ID assigned to every file and
    info is a dicitonary that contains information about the owner, file name,
    last edited date and last edited user.
    """
    def __init__(self):
        super().__init__(msgType=MessageType.LIST_FILES)

class NewFileRequest(Request):
    """New file request class.

    Used by the client to request creating a new file for the given user. The
    server responds with `OkResponse` if the action was successful or
    `ErrResponse`.
    """
    def __init__(self, fileName=None):
        super().__init__(msgType=MessageType.NEW_FILE)
        self.fileName = fileName
