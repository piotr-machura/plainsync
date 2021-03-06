"""Response module.

Contains the `Response` classes sent by the server to a client.
"""
import json
from common.message import Message, MessageType


class Response(Message):
    """Base response class.

    Used by the server to respond to client requests.

    Items:
        description: string describing the response contents.
    """
    def __init__(self, description='', **kwargs):
        super().__init__(**kwargs)
        self.description=description

class OkResponse(Response):
    """OK response class.

    Used by the server to communicate a succesfull outcome of an action which
    does not require any additional data.

    Args:
        action: string describing the succesfull action.
    """
    def __init__(self, action=None):
        super().__init__(
            msgType=MessageType.OK,
            description=f'Action: {action} :: Success.',
        )

class PullResponse(Response):
    """Pull response class.

    Used by the server to send file contents to the client in response to a
    pull request.

    Args:
        content: contents of the specified file.
    """
    def __init__(self, fileID=None, content=None):
        super().__init__(
            msgType=MessageType.PULL,
            description=f'Sending file contents: {fileID}',
        )
        self.content = content

    def __str__(self):
        dictionary = self.__dict__.copy()
        del dictionary['content']
        return json.dumps(dictionary)



class AuthResponse(Response):
    """Authentication response class.

    Used by the server to communicate succesfull authentication.

    Args:
        user: the just authenticated user.

    Items:
        userID: a generated ID of the user authenticating him in this session.
    """
    def __init__(self, sessionID=None, user=''):
        super().__init__(
            msgType=MessageType.AUTH,
            description=f'Authenticated :: {user}',
        )
        self.sessionID=sessionID

class FileListResponse(Response):
    """Response with file names owned by the user.

    Args:
        user: the user for which the file list has been sent.

    Items:
        filelist: a list of files accessible to the user as a dictionary of
            (file ID, (info)) pairs, where the ID is the unique ID assigned to
            every file and info is a dicitonary that contains information about
            the owner, file name, last edited date and last edited user.
    """
    def __init__(self, files=None, user=None):
        super().__init__(
            msgType=MessageType.LIST_FILES,
            description=f'Sending file list: {user}',
        )
        self.files = files
        if self.files is None:
            self.files = dict()

    def __str__(self):
        dictionary = self.__dict__.copy()
        del dictionary['files']
        return json.dumps(dictionary)


class ErrResponse(Response):
    """ Error response class.

    Used by the server to communicate when an error has occured during the
    processing of a request.

    Args:
        err: error description with optional stack trace.
    """
    def __init__(self, err=None):
        super().__init__(
            msgType=MessageType.ERR,
            description=f'Error: {err}.',
        )
