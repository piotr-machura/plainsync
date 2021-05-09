"""Client executable module."""

import time
import socket

from common.request import AuthRequest, FileListRequest, PullRequest, PushRequest
from common.response import AuthResponse, FileListResponse, PullResponse, OkResponse
from common.message import MessageType
from common import transfer

HOST = '127.0.0.1'    # The server's hostname or IP address
PORT = 9999    # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    req = AuthRequest(user='billy', passwd='123')
    # Send it to a server as JSON
    transfer.send(s, req)
    resp = AuthResponse.fromJSON(transfer.recieve(s))
    if resp.type == MessageType.ERR:
        print(resp.description)
        s.close()
        exit(1)
    # Save my ID for future connections
    myID = resp.sessionID
    # Request files owned and borrowed by the user
    print(myID)
    req = FileListRequest()
    transfer.send(s, req)
    resp = FileListResponse.fromJSON(transfer.recieve(s))
    if resp.type == MessageType.ERR:
        print(resp.description)
        s.close()
        exit(1)
    files = resp.files
    # Pull the files owned/borrowed by the user
    for f in files:
        time.sleep(2)
        ownership = files[f]
        req = PullRequest(file=f)
        transfer.send(s, req)
        resp = PullResponse.fromJSON(transfer.recieve(s))
        if resp.type == MessageType.ERR:
            print(resp.description)
            s.close()
            exit(1)
        print(f'{f} (owner: {ownership})')
        print(resp.content)
