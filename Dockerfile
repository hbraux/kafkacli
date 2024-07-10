FROM python:3.11.3-alpine

ARG registry
ENV registry=${registry}
LABEL description "Docker version of kafkacli"


COPY . /tmp/install
RUN python3 -m venv /venv && . /venv/bin/activate && cd /tmp/install && pip install .
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

