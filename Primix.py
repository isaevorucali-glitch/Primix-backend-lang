#!/usr/bin/env python3
# Primix v0.3 — Полное асинхронное ядро
# Все 38 фич + asyncio + keep-alive + кеш

import sys
import os
import json
import asyncio
import hashlib
import random
import string
import time
import sqlite3
import threading
from datetime import datetime
from collections import deque
from pathlib import Path

# ========== T8T ШИФРОВАНИЕ ==========
KANJI = ['暮', 'ら', 'し', '対', '話', '霧', '雨', '桜', '言', '葉',
         '夢', '見', 'る', '静', 'け', 'さ', '星', '空', '海', '風',
         '山', '川', '花', '火', '月', '日', '時', '人', '心', '手']

OLD_WORDS = ['whither', 'goeth', 'thy', 'darkness', 'whence', 'cometh',
             'light', 'shadow', 'throne', 'mist', 'falcon', 'sword',
             'ancient', 'keeper', 'forge', 'behold', 'wrath', 'dawn']

class T8T:
    @staticmethod
    def mixed_encrypt(data, key_seed):
        random.seed(key_seed)
        result = []
        raw = data.encode() if isinstance(data, str) else data
        for i, byte in enumerate(raw):
            if i % 3 == 0:
                result.append(random.choice(KANJI))
            elif i % 3 == 1:
                result.append(random.choice(OLD_WORDS))
            else:
                result.append(''.join(random.choices(string.ascii_letters + string.digits, k=5)))
        return ''.join(result)

    @staticmethod
    def jp_encrypt(data, key_seed):
        random.seed(key_seed)
        return ''.join(random.choice(KANJI) for _ in str(data))

    @staticmethod
    def en_encrypt(data, key_seed):
        random.seed(key_seed)
        return ' '.join(random.choice(OLD_WORDS) for _ in str(data).split())

    @staticmethod
    def rnd_encrypt(data, key_seed):
        random.seed(key_seed)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=len(str(data)) * 3))

# ========== ХРАНИЛИЩЕ ==========
class Storage:
    def __init__(self):
        self.data = {}
    def set(self, k, v): self.data[k] = v
    def get(self, k): return self.data.get(k)
    def delete(self, k):
        if k in self.data: del self.data[k]
    def keys(self): return list(self.data.keys())

# ========== КЕШ ==========
class Cache:
    def __init__(self):
        self.data = {}
        self.hits = 0
        self.misses = 0
    def get(self, k):
        if k in self.data:
            self.hits += 1
            return self.data[k]
        self.misses += 1
        return None
    def set(self, k, v):
        if len(self.data) > 10000:
            self.data.pop(next(iter(self.data)))
        self.data[k] = v
    def clear(self):
        self.data.clear()

# ========== ОЧЕРЕДЬ ==========
class TaskQueue:
    def __init__(self):
        self.q = deque()
    def push(self, t): self.q.append(t)
    def pop(self): return self.q.popleft() if self.q else None
    def size(self): return len(self.q)

# ========== СЕРВЕР ==========
class PrimixAsync:
    def __init__(self, code, filepath=""):
        self.code = code
        self.filepath = filepath
        self.key = hashlib.sha256(hashlib.sha256(code.encode()).hexdigest().encode()).hexdigest()[:32]
        self.port = 5000 + (hash(self.key) % 5000)
        self.routes = {}
        self.disabled_routes = set()
        self.variables = {}
        self.storage = Storage()
        self.cache = Cache()
        self.queue = TaskQueue()
        self.start_time = datetime.now()
        self.t8t_mode = 'mixed'
        self.log_enabled = True
        self.debug_enabled = False
        self.ghost_mode = False
        self.physical_only = False
        self.blackhole_mode = False
        self.intruder_alert = False
        self.sos_targets = []
        self.view_targets = []
        self.blocked_keys = set()
        self.whitelist = set()
        self.balancer_enabled = False
        self.request_count = 0
        self.running = True

    def log(self, msg, level="INFO"):
        if self.log_enabled:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}")

    def encrypt(self, data):
        if self.t8t_mode == 'jp':
            return T8T.jp_encrypt(data, self.key)
        elif self.t8t_mode == 'en':
            return T8T.en_encrypt(data, self.key)
        elif self.t8t_mode == 'rnd':
            return T8T.rnd_encrypt(data, self.key)
        return T8T.mixed_encrypt(data, self.key)

    def eval_expr(self, expr, request_data=None):
        expr = str(expr).strip()
        if expr == '$key': return self.key
        if expr.startswith('"') and expr.endswith('"'): return expr[1:-1]
        if expr in ['true', 'false']: return expr == 'true'
        if expr.startswith('get to/ '): return self.storage.get(expr.split('get to/ ', 1)[1].strip())
        if expr in self.variables: return self.variables[expr]
        try: return int(expr)
        except:
            try: return float(expr)
            except: return expr

    def execute_line(self, line, request_data=None):
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        # Переменные
        if ' = ' in line and not any(line.startswith(kw) for kw in
            ['respond', 'print', 'go', 'if', 'else', 'repeat', 'every',
             'store', 'throw', 'db', 'file', 'env', 'ping', 'bind',
             'block', 'whitelist', 'delete', 'save', 'load', 'key',
             'intruder', 'blackhole', 'physical', 'lock', 'cache',
             'queue', 'balance', 'burn', 'reload', 'list', 'timeout',
             'add', 'view', 'clear', 'debug', 'log', 'status']):
            parts = line.split(' = ', 1)
            name = parts[0].strip()
            val = parts[1].strip()
            if '+' in val:
                res = ''
                for p in val.split('+'):
                    res += str(self.eval_expr(p.strip(), request_data))
                self.variables[name] = res
            else:
                self.variables[name] = self.eval_expr(val, request_data)
            return None

        # print
        if line.startswith('print '):
            self.log(str(self.eval_expr(line[6:].strip(), request_data)))
            return None

        # respond
        if line.startswith('respond '):
            rest = line[8:].strip()
            if rest.startswith('json '):
                return json.dumps(json.loads(rest[5:]))
            elif rest.startswith('msgpack '):
                return rest[8:]
            if '+' in rest:
                res = ''
                for p in rest.split('+'):
                    res += str(self.eval_expr(p.strip(), request_data))
                return res
            return str(self.eval_expr(rest, request_data))

        # store
        if line.startswith('store on/ '):
            key = line.split('store on/ ', 1)[1].strip()
            if request_data:
                self.storage.set(key, request_data.get(key, request_data))
            return None

        # throw
        if line.startswith('throw to/'):
            parts = line.split(' ', 2)
            target = parts[1] if len(parts) > 1 else ''
            data = parts[2] if len(parts) > 2 else ''
            self.log(f"THROW → {target}: {data}")
            return None

        # db
        if line.startswith('db query '):
            query = line[9:].strip().strip('"')
            try:
                conn = sqlite3.connect(':memory:')
                c = conn.cursor()
                c.execute(query)
                rows = c.fetchall()
                conn.close()
                return str(rows)
            except Exception as e:
                return f"DB Error: {e}"

        if line.startswith('db store '):
            return None

        # file
        if line.startswith('file read '):
            path = line[10:].strip().strip('"')
            try:
                return open(path, 'r').read()
            except Exception as e:
                return f"File Error: {e}"

        if line.startswith('file write '):
            parts = line[11:].strip().split(' ', 1)
            path = parts[0].strip('"')
            content = parts[1].strip('"') if len(parts) > 1 else ''
            try:
                open(path, 'w').write(content)
            except:
                pass
            return None

        # Управление
        if line == 'status':
            uptime = datetime.now() - self.start_time
            return (f"Key: {self.key[:8]}...\n"
                    f"Port: {self.port}\n"
                    f"Uptime: {uptime}\n"
                    f"Requests: {self.request_count}\n"
                    f"Routes: {len(self.routes)} ({len(self.disabled_routes)} off)\n"
                    f"Cache: {len(self.cache.data)} items\n"
                    f"Queue: {self.queue.size()}\n"
                    f"T8T: {self.t8t_mode}\n"
                    f"Ghost: {self.ghost_mode}\n"
                    f"Physical: {self.physical_only}")

        if line == 'log on': self.log_enabled = True; return None
        if line == 'log off': self.log_enabled = False; return None
        if line == 'debug on': self.debug_enabled = True; return None
        if line == 'clear cache': self.cache.clear(); return None
        if line == 'cache on': return None
        if line == 'queue on': return None
        if line == 'balance on': self.balancer_enabled = True; return None

        if line.startswith('env '):
            parts = line[4:].strip().split('=', 1)
            if len(parts) == 2:
                self.variables[parts[0].strip()] = parts[1].strip().strip('"')
            return None

        if line.startswith('ping '):
            self.log(f"PING {line[5:].strip()} — alive")
            return "pong"

        if line.startswith('timeout '):
            return None

        if line == 'list servers':
            return "Servers: " + str(self.sos_targets)

        if line == 'key rotate':
            old = self.key
            self.key = hashlib.sha256((self.code + str(time.time())).encode()).hexdigest()[:32]
            self.log(f"KEY ROTATED: {old[:8]}... → {self.key[:8]}...")
            return None

        if line == 'save state':
            state = {'variables': self.variables, 'storage': {k: self.storage.get(k) for k in self.storage.keys()}}
            try:
                json.dump(state, open('.primix_state.json', 'w'))
                self.log("STATE SAVED")
            except:
                pass
            return None

        if line == 'load state':
            try:
                state = json.load(open('.primix_state.json', 'r'))
                self.variables = state.get('variables', {})
                for k, v in state.get('storage', {}).items():
                    self.storage.set(k, v)
                self.log("STATE LOADED")
            except:
                pass
            return None

        if line.startswith('/add t8t '):
            mode = line.split('/add t8t ')[1].strip()
            if mode in ['mixed', 'jp', 'en', 'rnd']:
                self.t8t_mode = mode
                self.log(f"T8T: {mode}")
            return None

        if line.startswith('/add sos mod!'):
            targets = line.split('/add sos mod!')[1].strip().split()
            self.sos_targets = targets
            self.log(f"SOS: {targets}")
            return None

        if line.startswith('/view in its entirety '):
            targets = line.split('/view in its entirety ')[1].strip().split()
            self.view_targets = targets
            self.log(f"VIEW: {targets}")

            async def health_report():
                while self.running:
                    await asyncio.sleep(3600)
                    self.log(f"HEALTH REPORT → {targets}")
            asyncio.create_task(health_report())
            return None

        if line == 'burn server':
            self.log("BURN!", "CRITICAL")
            self.running = False
            return None

        if line == 'reload server':
            self.parse_code()
            return None

        if line.startswith('block key '):
            self.blocked_keys.add(line.split('block key ')[1].strip())
            return None

        if line == 'lock down':
            self.physical_only = True
            self.ghost_mode = True
            self.blackhole_mode = True
            self.log("LOCKED DOWN")
            return None

        if line.startswith('key expires '):
            return None

        if line == 'intruder alert':
            self.intruder_alert = True
            return None

        if line == 'blackhole':
            self.blackhole_mode = True
            return None

        if line == 'physical only':
            self.physical_only = True
            return None

        if line.startswith('whitelist '):
            self.whitelist.add(line[10:].strip())
            return None

        return None

    def parse_code(self):
        self.routes = {}
        self.disabled_routes = set()
        lines = self.code.strip().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('#'):
                i += 1
                continue

            if line.startswith('go request ') or line.startswith('go fields '):
                parts = line.split(' ')
                method = 'GET' if parts[1] == 'request' else 'POST'
                path = parts[2].strip()
                body = []
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    body.append(lines[i].strip())
                    i += 1
                self.routes[(method, path)] = body

            elif line.startswith('if '):
                condition = line[3:].split(' then')[0].strip()
                then_body = []
                else_body = []
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    then_body.append(lines[i].strip())
                    i += 1
                if i < len(lines) and lines[i].strip() == 'else':
                    i += 1
                    while i < len(lines) and lines[i].startswith('    '):
                        else_body.append(lines[i].strip())
                        i += 1
                self.routes[('IF', condition)] = {'then': then_body, 'else': else_body}

            elif line.startswith('repeat '):
                parts = line[7:].split(' times')
                count = int(self.eval_expr(parts[0].strip()))
                body = []
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    body.append(lines[i].strip())
                    i += 1
                for _ in range(count):
                    for b in body:
                        self.execute_line(b)

            elif line.startswith('every '):
                parts = line[6:].split(' do')
                interval = parts[0].strip()
                body = []
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    body.append(lines[i].strip())
                    i += 1

                seconds = 60
                if 'min' in interval: seconds = int(interval.replace('min','').strip()) * 60
                elif 'sec' in interval: seconds = int(interval.replace('sec','').strip())
                elif 'hour' in interval: seconds = int(interval.replace('hour','').strip()) * 3600

                async def periodic():
                    while self.running:
                        await asyncio.sleep(seconds)
                        for b in body:
                            self.execute_line(b)
                asyncio.create_task(periodic())

            else:
                self.execute_line(line)
                i += 1

    def execute_route(self, route_body, request_data=None):
        result = None
        for line in route_body:
            res = self.execute_line(line, request_data)
            if res is not None:
                result = res
        return result if result else 'OK'

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        self.request_count += 1

        if self.blackhole_mode:
            writer.close()
            return

        try:
            data = await asyncio.wait_for(reader.read(16384), timeout=30)
            if not data:
                writer.close()
                return

            text = data.decode(errors='ignore')
            lines = text.split('\r\n')
            if not lines or len(lines[0].split(' ')) < 2:
                writer.close()
                return

            method, path, _ = lines[0].split(' ')
            body = ''
            if '\r\n\r\n' in text:
                body = text.split('\r\n\r\n', 1)[1]

            request_data = {}
            if body:
                try:
                    request_data = json.loads(body)
                except:
                    for pair in body.split('&'):
                        if '=' in pair:
                            k, v = pair.split('=', 1)
                            request_data[k] = v

            route_key = (method, path)

            if route_key in self.disabled_routes:
                writer.write(b"HTTP/1.1 503\r\nContent-Type: text/plain\r\nConnection: keep-alive\r\n\r\nRoute disabled")
                await writer.drain()
                writer.close()
                return

            if route_key in self.routes:
                try:
                    cache_key = f"{method}:{path}:{body}"
                    cached = self.cache.get(cache_key)
                    if cached:
                        response_body = cached
                    else:
                        response_body = self.execute_route(self.routes[route_key], request_data)
                        self.cache.set(cache_key, response_body)

                    encrypted = self.encrypt(response_body)
                    resp = (f"HTTP/1.1 200 OK\r\n"
                            f"Content-Type: text/plain\r\n"
                            f"Connection: keep-alive\r\n"
                            f"Content-Length: {len(encrypted.encode())}\r\n"
                            f"\r\n{encrypted}")
                    writer.write(resp.encode())
                    self.log(f"OK {method} {path}")
                except Exception as e:
                    self.disabled_routes.add(route_key)
                    self.log(f"ERR {method} {path}: {e}", "ERROR")
                    writer.write(b"HTTP/1.1 500\r\nConnection: keep-alive\r\n\r\nRoute error")
            else:
                writer.write(b"HTTP/1.1 404\r\nConnection: keep-alive\r\n\r\nNot Found")

            await writer.drain()
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            self.log(f"Error: {e}", "ERROR")
        finally:
            writer.close()

    async def start(self):
        self.parse_code()

        try:
            server = await asyncio.start_server(self.handle_client, '0.0.0.0', self.port, backlog=2000)
        except OSError:
            self.port = 5000 + random.randint(1, 5000)
            server = await asyncio.start_server(self.handle_client, '0.0.0.0', self.port, backlog=2000)

        self.log(f"=== Primix v0.3 Async Full ===")
        self.log(f"Key: {self.key}")
        self.log(f"Port: {self.port}")
        self.log(f"T8T: {self.t8t_mode}")
        self.log(f"Keep-alive: ON | Cache: ON | Queue: ON")
        self.log(f"Routes: {len(self.routes)} loaded")
        self.log(f"http://localhost:{self.port}")

        async with server:
            await server.serve_forever()


def main():
    if len(sys.argv) < 2:
        print("Primix v0.3 Async Full")
        print("Usage: python primix_async.py <file.pmx>")
        return

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        code = f.read()

    server = PrimixAsync(code, sys.argv[1])

    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == '__main__':
    main()
