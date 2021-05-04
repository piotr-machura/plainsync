"""TCP handler module.

Contains the handler and associated functions.
"""
import time
import hashlib
from socketserver import BaseRequestHandler
from logging import info, warning

from common.request import Request, AuthRequest, FileListRequest, PullRequest
from common.response import AuthResponse, ErrResponse, FileListResponse, PullResponse
from common.message import MessageType
from common import transfer


class TCPHandler(BaseRequestHandler):
    """
    The TCP request handler class.

    This is instantiated once per connection to the server and handles the
    communication with the client.
    """
    # A wannabe SQL database
    USERS = {'user': '456', 'billy': '123'}
    FILES = {
        'a.txt': {
            'owner': 'user',
            'users': {'billy'},
            'content': 'conent of file a.txt',
        },
        'b.txt': {
            'owner': 'billy',
            'users': {},
            'content': 'file\nb.txt\n more content',
        },
        'c.txt': {
            'owner': 'user',
            'users': {},
            'content': 'conent of\nfile c.txt\n more contentss',
        },
    }

    def __init__(self, *args, **kwargs):
        self.sessionID = None
        self.username = None
        super().__init__(*args, **kwargs)

    def setup(self):
        # Try and authenticate
        try:
            data = transfer.recieve(self.request)
        except ConnectionAbortedError:
            return
        authRequest = AuthRequest.fromJSON(data)
        if authRequest.type == MessageType.AUTH:
            # Atuhenticate
            user = authRequest.user
            passwd = authRequest.passwd
            if user in self.USERS and self.USERS[user] == passwd:
                # Save the username and the session ID hash
                toHash = str(time.time()) + user + self.client_address[0]
                self.sessionID = hashlib.sha1(toHash.encode('utf-8')).hexdigest()
                self.username = user
                response = AuthResponse(
                    sessionID=self.sessionID,
                    user=user,
                )
            else:
                response = ErrResponse(err='Invalid username or password')
            transfer.send(self.request, response)
        else:
            transfer.send(
                self.request,
                ErrResponse(err='Unauthenticated'),
            )


    def handle(self):

        if self.sessionID is None:
            warning('Unable to authenticate %s', self.client_address[0])
            return

        info('New session %s of user %s', self.sessionID, self.username)
        # Handle incoming requests

        while True:
            try:
                data = transfer.recieve(self.request)
            except ConnectionAbortedError:
                # The connection has been closed
                break
            request = Request.fromJSON(data)
            if request.type == MessageType.LIST_FILES:
                request = FileListRequest.fromJSON(data)
                response = self.listFiles()
            elif request.type == MessageType.PULL:
                request = PullRequest.fromJSON(data)
                response = self.pullFile(request)
            elif request.type == MessageType.PUSH:
                # Same here but I'm lazy
                raise NotImplementedError
            else:
                response = ErrResponse(err=f'Unknown action: {request.type}')
            info(
                'Session %s of user %s: Request:%s Response:%s',
                self.sessionID,
                self.username,
                request,
                response,
            )
            transfer.send(self.request, response)
        info('Closed session %s of user %s', self.sessionID, self.username)

    def listFiles(self):
        filelist = dict()
        for f in self.FILES:
            if self.FILES[f]['owner'] == self.username:
                filelist[f] = self.username
            elif self.username in self.FILES[f]['users']:
                filelist[f] = self.FILES[f]['owner']
        return FileListResponse(filelist)

    def pullFile(self, request):
        # Database of files and users allowed to use them
        if request.file in self.FILES.keys() and (
                self.username in self.FILES[request.file]['users']
                or self.username == self.FILES[request.file]['owner']):
            return PullResponse(
                file=request.file,
                content=self.FILES[request.file]['content'],
            )
        return ErrResponse(
            err=f'User {self.username} has no file {request.file}')
