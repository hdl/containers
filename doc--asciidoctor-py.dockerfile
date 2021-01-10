# syntax=docker/dockerfile:experimental

FROM asciidoctor/docker-asciidoctor

RUN apk add -U --no-cache graphviz py3-pip \
 && ln -s /usr/bin/python3 /usr/bin/python

RUN --mount=type=bind,src=./,target=/tmp/containers/ \
 ls -la /tmp/containers/ && pip3 install -r /tmp/containers/doc/requirements.txt
