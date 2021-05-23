FROM alpine

ARG registry
ENV registry=${registry}
LABEL description "Docker version of kafkacli"

RUN apk add --no-cache python3 \
    && python3 -m ensurepip \
    && ln -fs /usr/bin/pip3 /usr/bin/pip \
    && ln -fs /usr/bin/python3 /usr/bin/python

RUN pip3 install --no-cache-dir requests pygments avro-python3 kafka-python

COPY . /tmp/install
RUN cd /tmp/install && python3 setup.py install && rm -fr *
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

