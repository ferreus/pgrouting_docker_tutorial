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
