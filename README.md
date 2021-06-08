# Synchronous plain text editor
**WARNING:** there is **NO** safety measures in place. The data is transmitted as UTF-8 plain text, **including
passwords**. Please, don't use this.

## Server
The recommended way of setting up the server is using Docker. The image can be built and run  by running `docker-compose
up -d` in the project's root.

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



