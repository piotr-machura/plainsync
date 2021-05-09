FROM python:3.10-rc-alpine

COPY . /plainsync
EXPOSE 9999
VOLUME ["/plainsync/data"]

ENV PYTHONUNBUFFERED=1
ENV PLAINSYNC_HOST=0.0.0.0
ENV PLAINSYNC_STORAGE=/plainsync/data

CMD ["/usr/local/bin/python3","/plainsync/ps_server.py"]
