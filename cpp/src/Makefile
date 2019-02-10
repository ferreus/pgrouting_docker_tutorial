server: server.o
	g++ -std=c++11 -o server server.o -lpthread

server.o: server.cpp
	g++ -std=c++11 -c server.cpp


clean:
	-rm ./server
	-rm ./*.o
