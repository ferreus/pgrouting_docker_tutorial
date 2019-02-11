# Python query server for pgRouting

In this section we will see, how we can put our python server inside docker image, and let our two docker containers talk with each other.

First let's create our `Dockerfile`

```Dockerfile
FROM ubuntu:bionic

ADD server.py /app/server.py
ADD pip-requirements.txt /app/pip-requirements.txt

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install -r /app/pip-requirements.txt

WORKDIR /app
ENTRYPOINT ["/bin/sh" ,"-c", "python3 /app/server.py"]
```

We use ubuntu 18.04 (bionic) as our base image
We add our server.py code, and pip-requirements.txt that holds a list of all python modules required to run our server.
We created this file by running from our python `virtual environment`

    pip freeze > pip-requirements.txt

Now, on Ubuntu there is a known bug, that will add a wrong entry to the pip-requirements.txt file.

The line will look like:

    pkg-resources==0.0.0

If you have this line, in your pip-requirements.txt file, just remove it.

Now we ready to build our image

    docker build -t query_server .

Build docker image, name it query_server, use Dockerfile from current directory, and use current directory as working directory.

If successful you should see your query_server image in `docker images` output.

Now we have our docker image for our python server, let's create docker image for our pgRouting docker container.
Proceed to [next section](/docs/pgrouting_dockerfile.md)