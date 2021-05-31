# Synchronous plain text editor
**WARNING:** there is **NO** safety measures in place. The data is transmitted as UTF-8 plain text, **including
passwords**. Please, don't use this.

## Server
The recommended way of setting up the server is using Docker. The image can be pulled from
[here](https://hub.docker.com/r/piotrmachura/plainsync-server).

Configuration is done throught command line options (see `python ps_server.py --help`) or environment variables. Keep in
mind that CLI options take presedence. The storage location direcotry will be automatically created if it does not
exist, other lcoations msut be available for the server to start.

Environment variables:
- `PLAINSYNC_HOST`: hostname for the server, default `localhost`
- `PLAINSYNC_PORT`: port number to use, default `9999`
- `PLAINSYNC_STORAGE`: location of the data storage, default `$PWD/data`
- `PLAINSYNC_DATABASE`: location fo the database, default `$PLAINSYNC_STORAGE/plainsync.sqlite`
- `PLAINSYNC_LOGLEVEL`: log level for the server, default `INFO`
- `PLAINSYNC_LOGFILE`: location of the log file, default `stdout`



