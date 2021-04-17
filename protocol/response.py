"""Response module.

Contains the `Response` classes sent by server to the client
"""
from .message import Message, MessageType


class Response(Message):
    """Base response class.

    Extended by other classes to include additional data.

    Args:
        description: string describing the response contents.
    """
    def __init__(self, description='', **kwargs):
        super().__init__(**kwargs)
        self.description=description

class OkResponse(Response):
    """OK response class.

    Used by the server to communicate a succesfull outcome of an action which
    does not require any data to be sent from the server.

    Args:
        action: string describing the succesfull action.
    """
    def __init__(self, action=''):
        super().__init__(
            msgType=MessageType.OK,
            description=f'Action: {action} :: Success.',
        )

class PullResponse(Response):
    """Pull response class.

    Used by the server to send file contents to the client after a pull
    request.

    Args:
        content: contents of the specified file.
    """
    def __init__(self, file='', content=''):
        super().__init__(
            msgType=MessageType.PULL,
            description=f'Sending file contents: {file}',
        )
        self.content = content


class AuthResponse(Response):
    """Authentication response class.

    Issued after succesfull authentication.

    Args:
        user: the just authenticated user.

    Items:
        userID: a generated ID of the user authenticating him in this session.
    """
    def __init__(self, userID=None, user=''):
        super().__init__(
            msgType=MessageType.AUTH,
            description=f'Authenticated :: {user}',
        )
        self.userID=userID

class FileListResponse(Response):
    """Response with file names owned by the user.

    Args:
        user: the user for which the file list has been sent.

    Items:
        filelist: a list of files accessible to the user as a dictionary of
                  (filename, owner) pairs.
    """
    def __init__(self, files=None, user=''):
        super().__init__(
            msgType=MessageType.LIST_FILES,
            description=f'Sending file list: {user}',
        )
        self.files = files
        if self.files is None:
            self.files = dict()

class ErrResponse(Response):
    """ Error response class.

    Used by the server to communicate errors.

    Args:
        action: string descibing the action in which the error ocured.
        err: error description with optional stack trace.
    """
    def __init__(self, err=''):
        super().__init__(
            msgType=MessageType.ERR,
            description=f'Error: {err}.',
        )
