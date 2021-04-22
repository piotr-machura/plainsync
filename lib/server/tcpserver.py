"""TCP server module.
"""
import socketserver
from lib.server import handler

class TCPServer(socketserver.ThreadingTCPServer):
    """TCP server class".
    """
    HOST = '0.0.0.0'
    PORT = 9999

    def __init__(self):
        super().__init__((self.HOST, self.PORT), handler.TCPHandler)
