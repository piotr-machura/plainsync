"""Server executable module."""
import os
import logging
from server.tcpserver import TCPServer

logging.basicConfig(
    format='[%(levelname)s] [%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=os.getenv('PLAINSYNC_LOGLEVEL') or 'INFO',
    filename=os.getenv('PLAINSYNC_LOGFILE'),
)
with TCPServer() as server:
    server.serve_forever()
