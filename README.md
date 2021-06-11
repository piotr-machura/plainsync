# Synchronous plain text editor
**WARNING:** there is **NO** safety measures in place. Data is transmitted as UTF-8 plain text, **including
passwords**. Please, don't use this.

## Plainsync server
The recommended way of setting up the server is using Docker. The image can be built and run  by running `docker-compose
up -d` in the project's root.

### Configuration
Configuration is done through command line options (see `python ps_server.py --help`) or environment variables. Keep in
mind that CLI options take precedence. The storage location directory will be automatically created if it does not
exist, other locations must be available for the server to start.

Environment variables:
- `PLAINSYNC_HOST`: host name for the server, default `localhost`
- `PLAINSYNC_PORT`: port number to use, default `9999`
- `PLAINSYNC_STORAGE`: location of the data storage, default `$PWD/data`
- `PLAINSYNC_DATABASE`: location of the database, default `$PLAINSYNC_STORAGE/plainsync.sqlite`
- `PLAINSYNC_LOGLEVEL`: log level for the server, default `INFO`
- `PLAINSYNC_LOGFILE`: location of the log file, default `stdout`

### Server operation
The server is built using the `socketserver` module from Python's standard library. The server listens on specified
socket and relegates new connections to instances of `TCPHandler` class, which establish sessions and handle further
request.

Every connection is expected to first provide an `AuthRequest`, which is then verified and, upon success, given a
session ID. The handler then proceeds to answer to incoming requests and ends the session after the connection is
aborted, or the incoming message cannot be parsed.

Information about available users, their files and file shares is stored in an sqlite database, which is accessed by the
`TCPHandler` using an instance of `DatabaseManager`. New users must be manually added to the database, for example using
the sqlite command line client.

## Plainsync client

## Protocol details
The protocol makes use of Python's ability to deconstruct objects into dictionaries, which can then be serialized into
JSON strings and sent via a TCP connection.

Each functionality has its own `Request` object, with the server's `Response` type specified in its docstring. Messages
are sent over TCP with a 2-byte **proto-header**, which specifies the length of it's message in bytes. The entire
payload is as follows:
```none
           JSON message encoded with UTF-8
            │
            ▼
┌─────────┬───────────────────────────────────────────┐
│ ███████ │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒│
└─────────┴───────────────────────────────────────────┘
   ▲
   │
   │
  Message length as 16-bit unsigned integer in "big indian" byteorder
```

The messages can be sent using helper functions found within the `common/transfer.py` module.
