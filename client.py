import time
import socket
from libcommon.request import *
from libcommon.response import *
from libcommon.message import MessageType

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 9999# The port used by the server

def recieve(sock):
    msgLen = int.from_bytes(sock.recv(8).strip(), byteorder='big')
    return sock.recv(msgLen)

def send(sock, request):
    sock.sendall(request.sendable())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    req = AuthRequest(user='user', passwd='456')
    # Send it to a server as JSON
    send(s, req)
    resp = AuthResponse.fromSendable(recieve(s))
    if resp.type == MessageType.ERR:
        print(resp.description)
        s.close()
        exit(1)
    # Save my ID for future connections
    myID = resp.userID
    # Request files owned and borrowed by the user
    print(myID)
    req = FileListRequest(myID)
    send(s, req)
    resp = FileListResponse.fromSendable(recieve(s))
    if resp.type == MessageType.ERR:
        print(resp.description)
        s.close()
        exit(1)
    files = resp.files
    # Pull the files owned/borrowed by the user
    for f in files:
        time.sleep(5)
        ownership = files[f]
        req = PullRequest(userID=myID, file=f)
        send(s, req)
        resp = PullResponse.fromSendable(recieve(s))
        if resp.type == MessageType.ERR:
            print(resp.description)
            s.close()
            exit(1)
        print(f'{f} (owner: {ownership})')
        print(resp.content)
    s.close()
