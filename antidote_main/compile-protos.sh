2
3
4
5
6
7
8
9
10
11
#!/usr/bin/env bash

# Ensure that the requisite protoc, protoc-gen-go, protoc-gen-go-grpc binaries are installed.

# This will complain about non-full paths:
protoc \
--go_out=Mgrpc/service_config/service_config.proto=/internal/proto/grpc_service_config:. \
--go-grpc_out=Mgrpc/service_config/service_config.proto=/internal/proto/grpc_service_config:. \
--go_opt=paths=source_relative \
--go-grpc_opt=paths=source_relative \
antidote/antidote.proto
