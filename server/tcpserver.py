"""TCP server module.
"""
from logging import info
from socketserver import ThreadingTCPServer
from server import handler
from server import config


class TCPServer(ThreadingTCPServer):
    """TCP server class.

    Listens on the socket defined in config.HOST and config.PORT, handling
    the requests with handler.TCPHandler.
    """
    def __init__(self):
        super().__init__((config.HOST, config.PORT), handler.TCPHandler)
        info('Created plainsync server on %s:%s', config.HOST, config.PORT)

    def serve_forever(self, poll_interval=0.5):
        info('Started plainsync server on %s:%s', config.HOST, config.PORT)
        super().serve_forever(poll_interval)

    def server_close(self):
        info('Shut down plainsync server on %s:%s', config.HOST, config.PORT)
