#!/bin/bash

function _zookeeper {
  cfgfile=$CONFLUENT_HOME/etc/kafka/zookeeper.properties
  # default heap is 512
  case "$JVM_PROFILE" in
    min) export KAFKA_HEAP_OPTS="-Xmx64M -Xms64M";;
    low) export KAFKA_HEAP_OPTS="-Xmx256M -Xms256M";;
  esac
  if [[ $1 == -daemon ]]; then
    zookeeper-server-start -daemon $cfgfile
  else
    exec zookeeper-server-start $cfgfile
  fi
}

function _broker {
  cfgfile=$CONFLUENT_HOME/etc/kafka/server.properties
  sed -i 's~^log.dirs=.*~log.dirs=/data~' $cfgfile

  # use the host ip as default a
  if [[ -n $KAFKA_ADVERTISED_LISTENERS ]]; then
    hostip=$(/sbin/ip route|awk '/default/ { print $3 }')  
    KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://$hostip:9092
  fi
  sed -i "s~^.*advertised.listeners=.*~$KAFKA_ADVERTISED_LISTENERS~" $cfgfile
  # default heap is 1024M
  case "$JVM_PROFILE" in
    min) export KAFKA_HEAP_OPTS="-Xmx256M -Xms256M";;
    low) export KAFKA_HEAP_OPTS="-Xmx512M -Xms512M";;
  esac
  if [[ $1 == -daemon ]]; then
    kafka-server-start -daemon $cfgfile
  else
    exec kafka-server-start $cfgfile
  fi
}

function _registry {
  cfgfile=$CONFLUENT_HOME/etc/schema-registry/schema-registry.properties
  sed -i "s~^.*listeners=.*~listeners=http://0.0.0.0:${REGISTRY_PORT}~" $cfgfile

  # default heap is 512M
  case "$JVM_PROFILE" in
    min) export SCHEMA_REGISTRY_HEAP_OPTS="-Xmx256M -Xms256M";;
    low) export SCHEMA_REGISTRY_HEAP_OPTS="-Xmx512M -Xms512M";;
  esac

  if [[ $1 == -daemon ]]; then
    schema-registry-start -daemon $cfgfile
    while ! nc -z localhost ${REGISTRY_PORT};  do sleep 1; done
  else
    exec schema-registry-start $cfgfile
  fi
}

function _start {
  _zookeeper -daemon
  # wait for ZK to start
  while ! nc -z localhost 2181;  do sleep 1; done
  _broker -daemon
  while ! nc -z localhost 9092;  do sleep 1; done
  # registry is started last
  _registry "$1"
}



case $1 in
  zookeeper) _zookeeper;;
  broker)    _broker;;
  registry)  _registry;;
  start)     _start;;
  run)      _start -daemon; shift; exec $@;;
  *)     exec $@;;
esac

