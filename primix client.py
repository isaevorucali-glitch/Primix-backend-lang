import socket
import json

class PrimixClient:
    def __init__(self, key, host='localhost', port=5847):
        self.key = key
        self.host = host
        self.port = port

    def call(self, path):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        request = f"GET {path} HTTP/1.1\r\nHost: {self.host}\r\n\r\n"
        sock.send(request.encode())
        response = sock.recv(4096).decode()
        sock.close()
        return response.split('\r\n\r\n')[1] if '\r\n\r\n' in response else response

    def send(self, path, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        body = json.dumps(data)
        request = f"POST {path} HTTP/1.1\r\nHost: {self.host}\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        sock.send(request.encode())
        response = sock.recv(4096).decode()
        sock.close()
        return response.split('\r\n\r\n')[1] if '\r\n\r\n' in response else response

# Пример использования
client = PrimixClient("xK9mF2wQ7vL4pR1nT8yU5bN3hJ6cA0dG")
print(client.call("/hello"))
print(client.send("/save", {"name": "Test"}))