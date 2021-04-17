"""Server executable module."""

import socketserver
import time

from protocol.request import Request, AuthRequest, FileListRequest, PullRequest
from protocol.response import AuthResponse, ErrResponse, FileListResponse, PullResponse
from protocol.message import MessageType
from protocol import transfer


class TCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    HOST = 'localhost'
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
    ACTIVE_USERIDS = {}

    def handle(self):
        while True:
            try:
                data = transfer.recieve(self.request)
            except ConnectionAbortedError:
                break
            print(f'{self.client_address[0]} wrote:')
            request = Request.fromJSON(data)
            print(request)
            response = ErrResponse(
                action='Connection',
                err=f'Unknown action: {request.type}',
            )
            if request.userID is None:
                response = ErrResponse(
                    action='Connection', err='authenticate first')
                if request.type == MessageType.AUTH:
                    # Try to atuhenticate
                    request = AuthRequest.fromJSON(data)
                    response = self.authenticate(request)
            else:
                if request.userID not in self.ACTIVE_USERIDS:
                    response = ErrResponse(
                        action='Connection',
                        err=f'Unknown userID: {request.userID}',
                    )
                elif request.type == MessageType.LIST_FILES:
                    request = FileListRequest.fromJSON(data)
                    response = self.listFiles(request)
                elif request.type == MessageType.PULL:
                    request = PullRequest.fromJSON(data)
                    response = self.pullFile(request)
                elif request.type == MessageType.PUSH:
                    # Same here but I'm lazy
                    pass
            print(response)
            transfer.send(self.request, response)
        print(f'Closed connection with {self.client_address[0]}')

    def authenticate(self, request):
        current_action = f'Authenticate {request.user}'
        if request.user in self.USERS and self.USERS[
                request.user] == request.passwd:
            # Hash of username, time and IP address
            ID = str(time.time()) + request.user + self.client_address[0]
            # Add our suer to the active sessions database
            self.ACTIVE_USERIDS.update({ID: request.user})
            return AuthResponse(
                userID=ID,
                user=request.user,
            )
        return ErrResponse(
            action=current_action,
            err='Wrong username or password',
        )

    def listFiles(self, request):
        username = self.ACTIVE_USERIDS[request.userID]
        filelist = dict()
        for f in self.FILES:
            if self.FILES[f]['owner'] == username:
                filelist[f] = username
            elif username in self.FILES[f]['users']:
                filelist[f] = self.FILES[f]['owner']
        return FileListResponse(filelist)

    def pullFile(self, request):
        current_action = f'Pull file {request.file}'
        # Database of files and users allowed to use them
        if request.file in self.FILES.keys() and (
                self.ACTIVE_USERIDS[request.userID]
                in self.FILES[request.file]['users']
                or self.ACTIVE_USERIDS[request.userID]
                == self.FILES[request.file]['owner']):
            return PullResponse(
                file=request.file,
                content=self.FILES[request.file]['content'],
            )
        return ErrResponse(
            action=current_action,
            err=
            f'User {self.ACTIVE_USERIDS[request.userID]} has no file {request.file}.'
        )


with socketserver.ThreadingTCPServer(
    (
        TCPHandler.HOST,
        TCPHandler.PORT,
    ),
        TCPHandler,
) as server:
    server.serve_forever()
