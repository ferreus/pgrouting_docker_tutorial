# Creating Docker images with `Dockerfile`s

If Docker image is a cake, then Dockerfile is definetly the recipe. It contains specific instructions how to create a Docker image.

We will start with something very simple.

We will create simple C++ REST service, and create a docker image for this service.

Let's first start with our C++ REST service.

Now, to simplify code, we rely on two `header-only` C++ libraries:

1. [nlohman/json](https://github.com/nlohmann/json) - Work with JSON in C++ with ease
2. [cpp-httplib](https://github.com/yhirose/cpp-httplib) - Work with HTTP request, write Clients / Servers like in any modern language. 

This are simple header only libraries, meaning that everything you need to do, to use them, is just `#include` them in your project, for simplicity sakes, i've just put the header files inside [/cpp/src](/cpp/src) directory.

So our C++ Source directory contents:

    httplib.h
    json.hpp
    server.cpp


Now, let's create a simple C++ code.
Please note, this is not `production` quality code, do not put this in production.

```C++
#include "httplib.h"
#include "json.hpp"

int main(void)
{
    using namespace httplib;
    using json = nlohmann::json;

    Server svr;

    svr.Get("/api/v1/version", [](const Request& req, Response& res) {
        json j;
        j["name"] = "C++ Rest Service";
        j["version"] = "1.0";
        j["debug"] = true;
        res.set_content(j.dump(4), "application/json");
    });

    svr.listen("localhost", 1234);
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

Voila, your created C++ REST Service.

In next commit, we will put it inside Docker image.