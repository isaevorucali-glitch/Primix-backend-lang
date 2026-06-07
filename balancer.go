package main

import (
    "fmt"
    "io"
    "log"
    "net/http"
    "net/http/httputil"
    "net/url"
    "sync"
    "time"
)

type Server struct {
    URL     *url.URL
    Alive   bool
    Weight  int
}

type Balancer struct {
    servers []*Server
    current int
    mu      sync.Mutex
}

func (b *Balancer) NextServer() *Server {
    b.mu.Lock()
    defer b.mu.Unlock()

    for i := 0; i < len(b.servers); i++ {
        b.current = (b.current + 1) % len(b.servers)
        if b.servers[b.current].Alive {
            return b.servers[b.current]
        }
    }
    return nil
}

func (b *Balancer) HealthCheck() {
    for {
        time.Sleep(5 * time.Second)
        for _, s := range b.servers {
            resp, err := http.Get(s.URL.String() + "/health")
            s.Alive = err == nil && resp.StatusCode == 200
            if resp != nil {
                resp.Body.Close()
            }
        }
    }
}

func (b *Balancer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    server := b.NextServer()
    if server == nil {
        http.Error(w, "No servers available", 503)
        return
    }

    proxy := httputil.NewSingleHostReverseProxy(server.URL)
    proxy.ErrorHandler = func(w http.ResponseWriter, r *http.Request, err error) {
        log.Printf("Server %s failed: %v", server.URL, err)
        server.Alive = false
        b.ServeHTTP(w, r)
    }
    proxy.ServeHTTP(w, r)
}

func main() {
    servers := []string{
        "http://localhost:5847",
        "http://localhost:5848",
        "http://localhost:5849",
        "http://localhost:5850",
        "http://localhost:5851",
    }

    balancer := &Balancer{}

    for _, s := range servers {
        url, err := url.Parse(s)
        if err != nil {
            log.Fatal(err)
        }
        balancer.servers = append(balancer.servers, &Server{
            URL:   url,
            Alive: true,
        })
    }

    go balancer.HealthCheck()

    fmt.Println("Primix Balancer on :8080")
    fmt.Println("Backends:", servers)
    http.ListenAndServe(":8080", balancer)
}