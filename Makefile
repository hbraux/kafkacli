PYTHON = python3
PREFIX = $$HOME/.local
VERSION = $(shell sed -z -E "s/.*__version__ = '(.+)'.*/\1/g" kafkacli/version.py)
# assuming Registry repository name is same as Gitlab 
DOCKER_REGISTRY = $(shell git config --get remote.origin.url | sed -E 's~.*:(.*+)/.*~\1~')
TEST_TOPIC ?= testtopic

.DEFAULT_GOAL := help
.PHONY: build

export SITE_KAFKA ?= $(shell uname -n)
# export DOCKER_HOSTIP = $(shell docker network inspect bridge | sed -n 's/.*Gateway": "\(.*\)"/\1/p')


help:
	@echo $$(fgrep -h "## " $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/^\([a-z][a-z_\-]*\): ##/\\nmake \\\e[1;34m\1\\\e[0m\t:/g')


code: ## check python code style (pep8)
	pycodestyle kafkacli
	pycodestyle tests

install: ## install module
	$(PYTHON) setup.py install

develop: ## install module in development mode
	@mkdir -p $(PREFIX)
	@rm -fr	$(PREFIX)/lib/python3.6/site-packages/kafkacli
	$(PYTHON) setup.py develop --prefix $(PREFIX)

start: ## start local Kafka cluster and create test data
	docker-compose up -d
	sleep 10
	docker exec broker kafka-topics --zookeeper zookeeper:2181 --create --topic $(TEST_TOPIC) --partitions 1 --replication-factor 1

stop: ## stop Confluent cluster
	docker-compose down
	docker system prune -f
	docker volume prune -f

createtopic:
	kafka-topics --zookeeper localhost:2181 --create --topic $(TEST_TOPIC) --partitions 1 --replication-factor 1

test: ## run unit tests
	PYTHONDONTWRITEBYTECODE=1 pytest -v .

test-ci: ## run unit tests as CI (within a Docker image)
	docker build -t kafkacli_ci --build-arg CONFLUENT_MIRROR=$${HTTP_MIRROR:-http://packages.confluent.io} --network=host -f Dockerfile.test .
	docker run -t --rm -v $(CURDIR):/work -w /work kafkacli_ci run make createtopic test 

build: ## build Docker image 
	docker build --build-arg registry=$(DOCKER_REGISTRY) -t $(DOCKER_REGISTRY)/kafkacli:$(VERSION) -t $(DOCKER_REGISTRY)/kafkacli .
	docker run -it --rm $(DOCKER_REGISTRY)/kafkacli

publish: ## publish Docker image 
	docker push $(DOCKER_REGISTRY)/kafkacli:$(VERSION)
	docker push $(DOCKER_REGISTRY)/kafkacli


