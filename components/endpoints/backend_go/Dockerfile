FROM golang:1.17-stretch AS build

WORKDIR /app/
COPY main.go go.* /app/
RUN CGO_ENABLED=0 go build -o /app/main

FROM scratch
COPY --from=build /app/main /app/main

EXPOSE 8080

ENTRYPOINT ["/app/main"]