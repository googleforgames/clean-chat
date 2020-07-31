#!/usr/bin/env make -f

# Constants:
BINARY=antidote-chat
REPO=gcr.io/antidote-playground/antidote-chat:v1

# Targets:
all : binary container
phony : container
binary : $(BINARY)
container : binary

# Target definitions:
clean :
	rm -f $(BINARY)

$(BINARY) : export CGO_ENABLED=0
$(BINARY) :
	go build -ldflags "-s -w" -o $(BINARY) $(BINARY).go
	upx $(BINARY)

container : 
	docker build . -t $(REPO) 
	docker push $(REPO)

