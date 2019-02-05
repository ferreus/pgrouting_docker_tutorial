# Quick libpqxx introduction

## Installation

### Linux

	sudo apt install libpqxx-dev

### Windows

Go to: [https://github.com/jtv/libpqxx](https://github.com/jtv/libpqxx)
And follow build instructions.
Alternatively it might be available on `conan` or `vcpkg`.


## Simple example `test.cpp`

```c++
#include <iostream>
#include <pqxx/pqxx>
#include <vector>
#include <memory>
#include <sstream>


struct point {
    float lat;
    float lon;
};


int getNearestNode(std::shared_ptr<pqxx::connection> pConn, point p) {
    pqxx::work work(*pConn);
    auto result = work.prepared("nearest_node")(p.lat)(p.lon).exec();
    return std::stoi(result[0][0].c_str());
}

std::vector<point> findRoute(std::shared_ptr<pqxx::connection> pConn, int source, int dest) {
    std::vector<point> route;
    pqxx::work work(*pConn);
    std::ostringstream oss;

    oss << "select t.id,t.osm_id,t.lat,t.lon,tr.cost,tr.agg_cost from ways_vertices_pgr as t "
        << "INNER JOIN pgr_dijkstra('SELECT gid as id, source, target, cost_s as cost, reverse_cost_s as reverse_cost from ways',"
        << source << "," << dest
        << ", directed:=true) as tr ON t.id = tr.node";

    pqxx::result result = work.exec(oss.str());

    for (auto row: result) {
        point p;
        p.lat = std::stof(row[2].c_str());
        p.lon = std::stof(row[3].c_str());
        route.push_back(p);
    }

    return route;
}



int main(int argc, char* argv[]) {
    point src;
    point dst;
    if (argc != 5) {
        std::cerr << "Usage: " << argv[0] << "src_lat src_lon dst_lat dst_lon\n"
                  << "Example: " << argv[0] << " 35.014519 32.783076 34.959672 32.789795\n";

		return 1;
    } else {
        src.lat = std::stof(argv[1]);
        src.lon = std::stof(argv[2]);
        dst.lat = std::stof(argv[3]);
        dst.lon = std::stof(argv[4]);
    }
    try {
        auto pConn = std::make_shared<pqxx::connection>("user=user host=localhost dbname=city_routing password=user");
        std::cout << "Conntected to " << pConn->dbname() << "\n";
        std::cout << "Querying route from: [" << src.lat << ", " << src.lon << "] to [" << dst.lat << ", " << dst.lon << "]\n";
        pConn->prepare("nearest_node","select id,lat,lon from ways_vertices_pgr order by the_geom <-> ST_SetSRID(ST_Point($1,$2),4326) LIMIT 1");

        int nodeA = getNearestNode(pConn,src);
        int nodeB = getNearestNode(pConn,dst);
        auto route = findRoute(pConn,nodeA, nodeB);
        for (auto p: route) {
            std::cout << p.lat << ", " << p.lon << "\n";
        }
    } catch (const std::exception &e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```

### Building this example

#### Linux

g++ test.cpp -lpqxx -lpq

#### Windows

Start Visual Studio, Create New Project, Add Include, Lib directories, add linker flags,  ... .... ..
