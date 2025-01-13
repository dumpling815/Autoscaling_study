FROM ubuntu:latest
WORKDIR /app
RUN apt-get update && apt-get install -y net-tools && apt-get clean