#!/usr/bin/env make -f

# Constants:
BINARY=antidote-stt-demo

# Targets:
all : binary 
binary : $(BINARY)

# Target definitions:
clean :
	rm -f $(BINARY)

$(BINARY) : export CGO_ENABLED=0
$(BINARY) :
	go build -ldflags "-s -w" -o $(BINARY) $(BINARY).go
	upx $(BINARY)