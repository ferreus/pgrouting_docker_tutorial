# Creating Docker images with `Dockerfile`s

If Docker image is a cake, then Dockerfile is definetly the recipe. It contains specific instructions for how to create a Docker image.

We will start with something very simple.

We will create simple C++ REST service, and create a docker image for this service.

Let's first start with our C++ REST service.

Now, to simplify code, we will rely on two `header-only` C++ libraries:

1. [nlohman/json](https://github.com/nlohmann/json) - Work with JSON in C++ with ease
2. [cpp-httplib](https://github.com/yhirose/cpp-httplib) - Work with HTTP request, write Clients / Servers like in any modern language. 

This are simple header only libraries, meaning that everything you need to do, to use them, is just `#include` them in your project, for simplicity sakes, i've just put the header files inside [/cpp/src](/cpp/src) directory.

So our C++ Source directory contents (Relevant for this exercise) is:

    httplib.h
    json.hpp
    simple.cpp


Now, let's create a simple C++ code.
Please note, this is not `production` quality code, do not put this in production.

This server lacks logs, error checks and other production quality features.

```C++
#include "httplib.h"
#include "json.hpp"

int main(void)
{
    using namespace httplib;
    using json = nlohmann::json;

    Server svr;

    //Here we declare what is callend an endpoint
    //Every time, someone will request a resource from us with
    // /api/v1/version address, our lambda function will be called.
    svr.Get("/api/v1/version", [](const Request& req, Response& res) {

        //We do nothing special here, just prepare our json string and return it
        json j;
        j["name"] = "C++ Rest Service";
        j["version"] = "1.0";
        j["debug"] = true;

        //j.dump(4) will returns a json string, formated with 4 spaces.
        res.set_content(j.dump(4), "application/json");
    });

    //our server will listen on any IP, and port: 1234
    svr.listen("0.0.0.0", 1234);
}            
```

Compiling it on Linux is pretty simple, assuming you have g++ installed: (sudo apt install g++)

    g++ -std=c++11 simple.cpp -lpthread


Start with:

    ./a.out

Now in another terminal, try the following:

    curl -v http://localhost:1234/api/v1/version

You should see:

    * Trying 127.0.0.1...
    * TCP_NODELAY set
    * Connected to localhost (127.0.0.1) port 1234 (#0)
    > GET /api/v1/version HTTP/1.1
    > Host: localhost:1234
    > User-Agent: curl/7.58.0
    > Accept: */*
    > 
    < HTTP/1.1 200 OK
    < Content-Length: 75
    < Content-Type: application/json
    < 
    {
        "debug": true,
        "name": "C++ Rest Service",
        "version": "1.0"
    * Connection #0 to host localhost left intact
    }

Voila, your created your first C++ REST Service.
Wasn't that tought was it?

## Dockerfile

Now we want to create our docker image, and for that we need a recipe:

Let's think what we need in our container:
1. Some linux container, let's say `ubuntu`, and we probably want 18.04 also known as bionic (code name)
2. Our server code: `simple.cpp`, `json.hpp` and `httplib.h`
3. `g++` to compile our server code

Let's write it down and save it in as `Dockerfile.simple`

Our directory structure looks like:

    .
    ├── Dockerfile.simple
    └── src
        ├── httplib.h
        ├── json.hpp
        └── simple.cpp


```Dockerfile
FROM ubuntu:bionic

#Install g++
RUN apt update && apt install g++
ADD src /app/src
WORKDIR /app/src
RUN g++ -o /app/server -std=c++11 simple.cpp -lpthread
WORKDIR /app
# We do not wish to keep the source inside container
# Later we will learn that we can use what is called a 'builder' container
# That will let us keep building and running completely separated
# Which will remove g++ from the final docker image, as it is not needed for *running*
# For now, a simple rm -rf /app/src will do
RUN rm -rf /app/src

# This is our entry point, the main function if you like
# When the docker starts, it will start the server
ENTRYPOINT ["/bin/sh", "-c", "/app/server"]
```

Now that we have our recipe we can cook it. 

    docker build -t my_simple_server -f Dockerfile.simple .

Here we tell docker to build a docker image named my_simple_server using recipe from Dockerfile.simple and use current directory as working directory (The directory where we placed our files)

If successfull, running `docker images` will show you your freshly built image.

    $ docker images
    my_simple_server         latest                 1bcf5ed0fdc2        5 minutes ago       263MB


And now we can run our docker image, and test it:

    docker run -d --name simple_server -p 1234:1234 my_simple_server
    
Docker will print the id of newly started container, you can check that it's running with `docker ps`

Now, let's test it:

    curl -v http://localhost:1234/api/v1/version


## Congratulations
You've created your first Docker image
Proceed to [next section](/python/README.md)