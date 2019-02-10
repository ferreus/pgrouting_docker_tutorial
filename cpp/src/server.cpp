#include <iomanip>
#include <ctime>
#include <chrono>
#include <iostream>
#include "httplib.h"
#include "json.hpp"

using json = nlohmann::json;

std::string get_date_string(std::chrono::system_clock::time_point t) {
    char some_buffer[256] = {0};
    auto as_time_t = std::chrono::system_clock::to_time_t(t);
    struct tm tm;
    if (::gmtime_r(&as_time_t, &tm))
        if (std::strftime(some_buffer, sizeof(some_buffer), "%F %T", &tm))
        return std::string{some_buffer};
    throw std::runtime_error("Failed to get current date as string");
}

int main()
{
    using namespace httplib;
    Server server;

    server.Get("/hello", [](const Request &req, Response &res) {
        res.set_content("Hello World!\n", "test/plain");
    });

    server.Get(R"(/numbers/(\d+))", [&](const Request &req, Response &res) {
        auto numbers = req.matches[1];
        res.set_content(numbers, "text/plain");
    });

    server.Get("/status", [](const Request &req, Response &res) {
        json j;
        j["version"] = "1.0";
        j["name"] = "C++ Rest Service";
        j["port"] = 1234;
        auto out = j.dump(4);
        res.set_content(out, "application/json");
    });

    server.set_logger([](const Request &req, const Response &res) {
        std::cout << get_date_string(std::chrono::system_clock::now()) << ":    [" << req.method << "]: " << req.path
                  << " : " << res.status << "\n";
    });

    std::cout << "Starting server on 0.0.0.0, port: 1234...\n";
    server.listen("0.0.0.0", 1234);
    return 0;
}
