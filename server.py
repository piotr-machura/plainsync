"""Server executable module."""
from lib.server.tcpserver import TCPServer

with TCPServer() as server:
    server.serve_forever()
