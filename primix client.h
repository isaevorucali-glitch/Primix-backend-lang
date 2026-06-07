#ifndef PRIMIX_CLIENT_H
#define PRIMIX_CLIENT_H

#include <string>
#include <winsock2.h>
#pragma comment(lib, "ws2_32.lib")

class PrimixClient {
public:
    PrimixClient(const std::string& key, const std::string& host = "localhost", int port = 5847)
        : key_(key), host_(host), port_(port) {
        WSAStartup(MAKEWORD(2, 2), &wsa_);
    }

    ~PrimixClient() {
        WSACleanup();
    }

    std::string call(const std::string& path) {
        SOCKET sock = socket(AF_INET, SOCK_STREAM, 0);
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port_);
        addr.sin_addr.s_addr = inet_addr(host_.c_str());

        connect(sock, (sockaddr*)&addr, sizeof(addr));

        std::string req = "GET " + path + " HTTP/1.1\r\nHost: " + host_ + "\r\n\r\n";
        send(sock, req.c_str(), req.size(), 0);

        char buf[4096] = {};
        recv(sock, buf, 4096, 0);
        closesocket(sock);

        std::string response(buf);
        size_t pos = response.find("\r\n\r\n");
        return pos != std::string::npos ? response.substr(pos + 4) : response;
    }

private:
    std::string key_, host_;
    int port_;
    WSADATA wsa_;
};
#endif