"""TCP server module.
"""
import os
import logging
from socketserver import ThreadingTCPServer
from server import handler


class TCPServer(ThreadingTCPServer):
    """TCP server class".
    """
    DEFAULT_HOST = '0.0.0.0'
    DEFAULT_PORT = 9999

    def __init__(self):
        host = os.getenv('PLAINSYNC_HOST') or self.DEFAULT_HOST
        port = os.getenv('PLAINSYNC_PORT') or self.DEFAULT_PORT
        super().__init__((host, port), handler.TCPHandler)
        logging.info('Started plainsync server on %s:%s', host, port)
