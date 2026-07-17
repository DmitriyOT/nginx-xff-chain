# Nginx Proxy Chain + X-Forwarded-For

[Русская версия](README.ru.md)

A learning lab: a chain of three nginx reverse proxies in front of a Python application. It demonstrates how to correctly build the `X-Forwarded-For` header as a request passes through multiple proxies, and how to protect against clients spoofing this header.

## Purpose of the Lab

When a request passes through several proxies, the application must see the full chain of IP addresses: the real client IP and the addresses of all intermediate proxies. At the same time, the client must not be able to "slip" an arbitrary IP at the start of the chain — the `X-Forwarded-For` header is only accepted from trusted proxies.

## Traffic Flow

Direct access (any of the three nginx instances):

```
client → nginxN → app
```

Chain (the `/chain` endpoint on any nginx):

```
client → nginx1 → nginx2 → nginx3 → app
```

- `nginx1` — `172.30.0.11` (exposed on port `8081`)
- `nginx2` — `172.30.0.12` (exposed on port `8082`)
- `nginx3` — `172.30.0.13` (exposed on port `8083`)
- `app` — `172.30.0.20` (exposed on port `8084`), a simple Python HTTP server that returns the received `X-Forwarded-For` header

## Protection Against X-Forwarded-For Spoofing

A client can send a request with the header `X-Forwarded-For: 1.2.3.4` to hide their real address. On each nginx this is cut off using the `map $remote_addr` directive:

- if the request comes **from a trusted address** (one of the proxies or the application on the `172.30.0.0/24` subnet) — the received `X-Forwarded-For` is used as the base;
- if the request comes **from anyone else** (directly from the client) — the received header is discarded, and the real client IP (`$remote_addr`) becomes the base.

Then a second `map` appends the address of the current proxy to the base. As a result, the forged header is removed at the very first nginx, and the application always receives a correct chain starting with the real client IP, for example:

```
X-Forwarded-For: 172.30.0.1, 172.30.0.11, 172.30.0.12, 172.30.0.13
```

where `172.30.0.1` is the Docker gateway address, i.e. the real client address.

## Stack

- Docker Compose
- nginx (alpine) — reverse proxy
- Python 3 (alpine) — test application built on the standard library (`http.server`)

## Project Structure

```
├── app/
│   └── app.py              # application that returns X-Forwarded-For
├── nginx/
│   ├── nginx1.conf         # first proxy config (port 8081)
│   ├── nginx2.conf         # second proxy config (port 8082)
│   └── nginx3.conf         # third proxy config (port 8083)
├── docker-compose.yml      # orchestration: 4 containers, network 172.30.0.0/24
└── Протокол.md             # test protocol with curl examples
```

## Quick Start

```bash
docker compose up --build
```

Verify it works:

```bash
curl http://localhost:8081/        # via a single proxy
curl http://localhost:8081/chain   # via the whole chain
curl -H "X-Forwarded-For: 1.2.3.4" http://localhost:8081/chain  # spoofing attempt
```

Stop the lab:

```bash
docker compose down
```

## Testing

The full test protocol with `curl` commands and expected results is in the file [Протокол.md](Протокол.md).
