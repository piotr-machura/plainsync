"""Server executable module."""
from server.tcpserver import TCPServer

with TCPServer() as server:
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        server.shutdown()
