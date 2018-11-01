.PHONY: help run test artifact deploy

default: help

GIT_SHA = $(shell git rev-parse HEAD)
DOCKER_REPOTAG = $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(GIT_SHA)

help: ## Show this help
	@echo "Database Stream Service"
	@echo "======================"
	@echo
	@echo "An python app that connects to a database's binlog"
	@echo "to stream events."
	@echo
	@fgrep -h " ## " $(MAKEFILE_LIST) | fgrep -v fgrep | sed -Ee 's/([a-z.]*):[^#]*##(.*)/\1##\2/' | column -t -s "##"

run: ## Run the application locally
	@docker-compose up --build --detach cache
	@docker-compose up --abort-on-container-exit --build service

db:
	@docker-compose up --build --detach db

queue:
	@docker-compose up --build --detach queue

test: ## Run the application's test suite
	@docker-compose -f docker-compose.ci.yml build test
	@docker-compose -f docker-compose.ci.yml run --rm test

artifact: ## Build a container and push to the configured registry
	docker build -t $(DOCKER_REPOTAG) .
	docker push $(DOCKER_REPOTAG)

deploy: ## Deploy the application to Marathon
	export DOCKER_REPOTAG=$(DOCKER_REPOTAG); \
	export GIT_SHA=$(GIT_SHA); \
	docker-compose -f docker-compose.ci.yml run --rm shpkpr
