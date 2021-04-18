FROM python:3.10-rc-alpine

COPY . /plainsync
EXPOSE 9999
VOLUME ["/plainsync/data/server"]

CMD ["/usr/local/bin/python3","/plainsync/server.py"]
