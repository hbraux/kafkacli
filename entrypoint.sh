#!/bin/sh
if [ $# -eq 0 ]; then
  echo "Docker Usage: docker run -it --rm -e SITE_KAFKA=<SERVER> [--add-host <SERVER>:<IP>] $registry/kafkacli ARGS

kafkacli will then connect to Broker <SERVER>:9092 and Schema Registry <SERVER>:8881 if required (to read avro topics)
If the container cannot reach <SERVER> (no DNS or server running also in Docker) then pass the IP in the docker command

Alternatively you can use kafkacli options -b BROKERS -r REGISTRY to specify brokers and registry server
---
"
fi

exec kafkacli $*
