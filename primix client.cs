using System;
using System.Net.Sockets;
using System.Text;

public class PrimixClient
{
    private string key, host;
    private int port;

    public PrimixClient(string key, string host = "localhost", int port = 5847)
    {
        this.key = key;
        this.host = host;
        this.port = port;
    }

    public string Call(string path)
    {
        using var client = new TcpClient(host, port);
        var stream = client.GetStream();
        var request = $"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n";
        var data = Encoding.UTF8.GetBytes(request);
        stream.Write(data, 0, data.Length);

        var buffer = new byte[4096];
        var bytes = stream.Read(buffer, 0, buffer.Length);
        var response = Encoding.UTF8.GetString(buffer, 0, bytes);
        var pos = response.IndexOf("\r\n\r\n");
        return pos >= 0 ? response.Substring(pos + 4) : response;
    }
}