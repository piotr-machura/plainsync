"""Server executable module."""

import socketserver
import time
import hashlib

from lib.request import Request, AuthRequest, FileListRequest, PullRequest
from lib.response import AuthResponse, ErrResponse, FileListResponse, PullResponse
from lib.message import MessageType
from lib import transfer
from lib import server


class TCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    HOST = '0.0.0.0'
    PORT = 9999
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

    def handle(self):
        # Try and authenticate
        try:
            data = transfer.recieve(self.request)
        except ConnectionAbortedError:
            return
        authRequest = AuthRequest.fromJSON(data)
        if authRequest.type == MessageType.AUTH:
            # Atuhenticate
            response = self.authenticate(authRequest)
            transfer.send(self.request, response)
        else:
            transfer.send(
                self.request,
                ErrResponse(err='Unauthenticated'),
            )

        if self.sessionID is None:
            print(
                '--------------\n' +
                f'Unable to authenticate {self.client_address[0]}')
            return

        # The connection has been established
        print(
            '--------------\n' +
            f'New session {self.sessionID} of user {self.username}')
        while True:
            try:
                data = transfer.recieve(self.request)
            except ConnectionAbortedError:
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
                pass
            else:
                response = ErrResponse(err=f'Unknown action: {request.type}')
            print(
                '--------------\n' +
                f'Session {self.sessionID} of user {self.username}:\n' +
                f'Request: {request}\n' + f'Response: {response}')
            transfer.send(self.request, response)
        print(
            '--------------\n' +
            f'Closed session {self.sessionID} of user {self.username}')

    def authenticate(self, request):
        if request.user in self.USERS and self.USERS[
                request.user] == request.passwd:
            # Save the username and the session ID hash
            toHash = str(time.time()) + request.user + self.client_address[0]
            self.sessionID = hashlib.sha1(toHash.encode('utf-8')).hexdigest()
            self.username = request.user
            return AuthResponse(
                userID=self.sessionID,
                user=request.user,
            )
        return ErrResponse(err='Invalid username or password')

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


with socketserver.ThreadingTCPServer(
    (
        TCPHandler.HOST,
        TCPHandler.PORT,
    ),
        TCPHandler,
) as server:
    server.serve_forever()
