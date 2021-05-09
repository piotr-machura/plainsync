"""Confguration module.

Loads configuration from CLI arguments first and environment variables second.
Defines fallback options if no configuration is provided.
"""
import argparse
import logging
import os

_parser = argparse.ArgumentParser(description='Plainsync server executable.')
_parser.add_argument('--host', help='sets the hostname for TCP server')
_parser.add_argument('--port', type=int, help='sets the port number for TCP server')
_parser.add_argument('--database', help='sets the path to the sqlite database')
_parser.add_argument('--storage', help='sets the path to the storage directory')
_parser.add_argument('--loglevel', help='set the logging level (default INFO)')
_parser.add_argument('--logfile', help='set the log file (default STDOUT)')
_args = _parser.parse_args()

DEFAULT_HOST = 'localhost'
HOST = _args.host or os.getenv('PLAINSYNC_HOST') or DEFAULT_HOST

DEFAULT_PORT = 9999
PORT = _args.port or os.getenv('PLAINSYNC_PORT') or DEFAULT_PORT
PORT = int(PORT)

DEFAULT_STORAGE = os.getcwd() + os.pathsep + 'data'
STORAGE = _args.storage or os.getenv('PLAINSYNC_STORAGE') or DEFAULT_STORAGE

DEFAULT_DATABASE = STORAGE + os.pathsep + 'plainsyncdb.sqlite'
DATABASE = _args.database or os.getenv('PLAINSYNC_DATABASE') or DEFAULT_DATABASE

DEFAULT_LOGLEVEL = 'INFO'
LOGLEVEL = _args.loglevel or os.getenv('PLAINSYNC_LOGLEVEL') or DEFAULT_LOGLEVEL

DEFAULT_LOGFILE = None # STDOUT
LOGFILE = _args.logfile or os.getenv('PLAINSYNC_LOGFILE') or DEFAULT_LOGFILE

logging.basicConfig(
    format='[%(levelname)s] [%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=LOGLEVEL,
    filename=LOGFILE,
)
