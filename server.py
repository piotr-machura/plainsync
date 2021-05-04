"""Server executable module."""
from server.tcpserver import TCPServer

with TCPServer() as server:
    server.serve_forever()
