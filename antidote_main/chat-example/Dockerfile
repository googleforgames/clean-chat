FROM scratch

LABEL maintainer "tdg@google.com"

ADD ca-certificates.crt /etc/ssl/certs/
ADD static /static/
ADD antidote-chat /

EXPOSE 8000/tcp

ENTRYPOINT ["/antidote-chat"]
