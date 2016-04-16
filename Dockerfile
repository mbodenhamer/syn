FROM mbodenhamer/python-dev:latest
COPY dev/dist-test /usr/local/bin/
COPY dev/test-dist /usr/local/bin/
