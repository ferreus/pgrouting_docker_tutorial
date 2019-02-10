FROM ubuntu:bionic

RUN apt-get update && apt-get install -y g++ make

ADD src /app/src
WORKDIR /app/src
RUN make && cp /app/src/server /app && rm -rf /app/src
ENTRYPOINT ["/bin/sh" ,"-c", "/app/server"]
