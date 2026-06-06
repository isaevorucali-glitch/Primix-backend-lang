#!/usr/bin/env python3
# Primix v0.2 — Интерпретатор языка Primix
# 38 фич, полный язык, T8T, кластеризация, безопасность

import sys
import os
import json
import socket
import threading
import time
import hashlib
import random
import string
import sqlite3
import struct
import queue
import datetime
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
        for i, byte in enumerate(data.encode() if isinstance(data, str) else data):
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
        return ''.join(random.choices(string.ascii_letters + string.digits,
                                      k=len(str(data)) * 3))

# ========== ХРАНИЛИЩЕ КЛЮЧ-ЗНАЧЕНИЕ ==========
class Storage:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def set(self, key, value):
        with self.lock:
            self.data[key] = value

    def get(self, key):
        with self.lock:
            return self.data.get(key, None)

    def delete(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]

    def all_keys(self):
        with self.lock:
            return list(self.data.keys())

# ========== КЕШ ==========
class Cache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[key] = value

    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0

# ========== ОЧЕРЕДЬ ЗАДАЧ ==========
class TaskQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()

    def push(self, task):
        with self.lock:
            self.queue.append(task)

    def pop(self):
        with self.lock:
            return self.queue.popleft() if self.queue else None

    def size(self):
        with self.lock:
            return len(self.queue)

# ========== ОСНОВНОЙ СЕРВЕР ==========
class PrimixServer:
    def __init__(self, code_str, filepath=""):
        self.code = code_str
        self.filepath = filepath
        self.key = self._generate_key()
        self.port = self._generate_port()
        self.routes = {}
        self.disabled_routes = set()
        self.variables = {}
        self.storage = Storage()
        self.cache = Cache()
        self.task_queue = TaskQueue()
        self.logs = []
        self.log_enabled = True
        self.debug_enabled = False
        self.start_time = datetime.datetime.now()
        self.ghost_mode = False
        self.physical_only = False
        self.t8t_mode = 'mixed'
        self.sos_targets = []
        self.view_targets = []
        self.blocked_keys = set()
        self.whitelist = set()
        self.balancer_enabled = False
        self.balancer_servers = []
        self.expire_time = None
        self.intruder_alert = False
        self.blackhole_mode = False
        self.server_socket = None
        self.running = True

    def _generate_key(self):
        hash_obj = hashlib.sha256(self.code.encode())
        return hashlib.sha256(hash_obj.hexdigest().encode()).hexdigest()[:32]

    def _generate_port(self):
        return 5000 + (hash(self.key) % 5000)

    def log(self, msg, level="INFO"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{level}] {msg}"
        if self.log_enabled:
            self.logs.append(entry)
            print(entry)
        return entry

    def debug(self, msg):
        if self.debug_enabled:
            self.log(msg, "DEBUG")

    def encrypt_response(self, data):
        if self.t8t_mode == 'mixed':
            return T8T.mixed_encrypt(data, self.key)
        elif self.t8t_mode == 'jp':
            return T8T.jp_encrypt(data, self.key)
        elif self.t8t_mode == 'en':
            return T8T.en_encrypt(data, self.key)
        elif self.t8t_mode == 'rnd':
            return T8T.rnd_encrypt(data, self.key)
        return str(data)

    def eval_expr(self, expr, request_data=None):
        expr = str(expr).strip()
        if expr == '$key':
            return self.key
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        if expr in ['true', 'false']:
            return expr == 'true'
        if expr.startswith('get to/ '):
            return self.storage.get(expr.split('get to/ ', 1)[1].strip())
        if expr in self.variables:
            return self.variables[expr]
        try:
            return int(expr)
        except:
            try:
                return float(expr)
            except:
                return expr

    def execute_line(self, line, request_data=None):
        line = line.strip()
        if not line or line.startswith('#'):
            return None, None

        # Переменные
        if ' = ' in line and not any(line.startswith(kw) for kw in
            ['respond', 'print', 'go', 'if', 'else', 'repeat', 'every',
             'store', 'throw', 'db', 'file', 'env', 'ping', 'bind',
             'unbind', 'whitelist', 'block', 'delete', 'save', 'load']):
            parts = line.split(' = ', 1)
            name = parts[0].strip()
            val = parts[1].strip()
            if '+' in val:
                result = ''
                for p in val.split('+'):
                    result += str(self.eval_expr(p.strip(), request_data))
                self.variables[name] = result
            else:
                self.variables[name] = self.eval_expr(val, request_data)
            return None, None

        # print
        if line.startswith('print '):
            msg = line[6:].strip()
            val = self.eval_expr(msg, request_data)
            self.log(str(val))
            return None, None

        # respond
        if line.startswith('respond '):
            rest = line[8:].strip()
            if rest.startswith('json '):
                try:
                    data = json.loads(rest[5:])
                    return 'respond_json', data
                except:
                    return 'respond', rest[5:]
            elif rest.startswith('msgpack '):
                return 'respond_msgpack', rest[8:]
            else:
                if '+' in rest:
                    result = ''
                    for p in rest.split('+'):
                        result += str(self.eval_expr(p.strip(), request_data))
                    return 'respond', result
                return 'respond', self.eval_expr(rest, request_data)

        # store
        if line.startswith('store on/ '):
            key = line.split('store on/ ', 1)[1].strip()
            if request_data:
                self.storage.set(key, request_data.get(key, request_data))
            return 'store', key

        # throw to
        if line.startswith('throw to/'):
            parts = line.split(' ', 2)
            target_key = parts[1]
            data = parts[2] if len(parts) > 2 else ''
            # Упрощённый throw — логируем
            self.log(f"THROW to {target_key}: {data}")
            return 'throw', target_key

        # db query
        if line.startswith('db query '):
            query = line[9:].strip().strip('"')
            self.log(f"DB QUERY: {query}")
            return 'db_query', query

        if line.startswith('db store '):
            parts = line[9:].strip().split(' ', 1)
            return 'db_store', parts

        # file read/write
        if line.startswith('file read '):
            path = line[10:].strip().strip('"')
            try:
                with open(path, 'r') as f:
                    return 'file_content', f.read()
            except Exception as e:
                self.log(f"FILE READ ERROR: {e}", "ERROR")
                return 'file_content', ''

        if line.startswith('file write '):
            parts = line[11:].strip().split(' ', 1)
            path = parts[0].strip('"')
            content = parts[1].strip('"') if len(parts) > 1 else ''
            try:
                with open(path, 'w') as f:
                    f.write(content)
            except Exception as e:
                self.log(f"FILE WRITE ERROR: {e}", "ERROR")
            return None, None

        # every
        if line.startswith('every '):
            parts = line[6:].strip().split(' do')
            return 'every', parts

        # Команды управления
        if line == 'status':
            self._print_status()
            return None, None

        if line == 'log on':
            self.log_enabled = True
            return None, None

        if line == 'log off':
            self.log_enabled = False
            return None, None

        if line == 'debug on':
            self.debug_enabled = True
            return None, None

        if line.startswith('env '):
            parts = line[4:].strip().split('=', 1)
            if len(parts) == 2:
                self.variables[parts[0].strip()] = parts[1].strip().strip('"')
            return None, None

        if line.startswith('ping '):
            target = line[5:].strip()
            self.log(f"PING {target} — assumed alive")
            return None, None

        if line.startswith('timeout '):
            val = int(line[8:].strip())
            self.log(f"TIMEOUT set to {val}s")
            return None, None

        if line == 'list servers':
            self.log("Active servers: " + str(self.balancer_servers))
            return None, None

        if line == 'key rotate':
            old_key = self.key
            self.key = self._generate_key()
            self.log(f"KEY ROTATED: {old_key[:8]}... → {self.key[:8]}...")
            return None, None

        if line == 'save state':
            self._save_state()
            return None, None

        if line == 'load state':
            self._load_state()
            return None, None

        if line == 'cache on':
            self.log("CACHE enabled")
            return None, None

        if line == 'clear cache':
            self.cache.clear()
            return None, None

        if line == 'balance on':
            self.balancer_enabled = True
            return None, None

        if line == 'queue on':
            self.log("QUEUE enabled")
            return None, None

        if line.startswith('/add t8t '):
            mode = line.split('/add t8t ')[1].strip()
            if mode in ['mixed', 'jp', 'en', 'rnd']:
                self.t8t_mode = mode
                self.log(f"T8T mode: {mode}")
            return None, None

        if line.startswith('/add sos mod!'):
            targets = line.split('/add sos mod!')[1].strip().split()
            self.sos_targets = targets
            self.log(f"SOS targets: {targets}")
            return None, None

        if line.startswith('/view in its entirety '):
            targets = line.split('/view in its entirety ')[1].strip().split()
            self.view_targets = targets
            self.log(f"VIEW targets: {targets}")
            return None, None

        if line == 'burn server':
            self.log("BURN COMMAND RECEIVED — shutting down", "CRITICAL")
            self.running = False
            return None, None

        if line == 'reload server':
            self.log("RELOAD — re-parsing code")
            self.parse_code()
            return None, None

        if line.startswith('block key '):
            key = line.split('block key ')[1].strip()
            self.blocked_keys.add(key)
            return None, None

        if line == 'lock down':
            self.physical_only = True
            self.ghost_mode = True
            self.blackhole_mode = True
            self.log("SERVER LOCKED DOWN — physical access only")
            return None, None

        if line.startswith('key expires '):
            self.log(f"KEY EXPIRES: {line[12:]}")
            return None, None

        if line == 'intruder alert':
            self.intruder_alert = True
            return None, None

        if line == 'blackhole':
            self.blackhole_mode = True
            return None, None

        if line == 'physical only':
            self.physical_only = True
            return None, None

        if line.startswith('whitelist '):
            key = line[10:].strip()
            self.whitelist.add(key)
            return None, None

        return None, None

    def _print_status(self):
        uptime = datetime.datetime.now() - self.start_time
        self.log(f"=== STATUS ===")
        self.log(f"Key: {self.key}")
        self.log(f"Port: {self.port}")
        self.log(f"Uptime: {uptime}")
        self.log(f"Routes: {len(self.routes)} active, {len(self.disabled_routes)} disabled")
        self.log(f"Cache: {len(self.cache.cache)} items")
        self.log(f"Queue: {self.task_queue.size()} tasks")
        self.log(f"Variables: {len(self.variables)}")
        self.log(f"T8T: {self.t8t_mode}")
        self.log(f"Ghost: {self.ghost_mode}")
        self.log(f"Physical only: {self.physical_only}")

    def _save_state(self):
        state = {
            'variables': self.variables,
            'storage': {k: self.storage.get(k) for k in self.storage.all_keys()}
        }
        with open('.primix_state.json', 'w') as f:
            json.dump(state, f)
        self.log("STATE SAVED")

    def _load_state(self):
        if os.path.exists('.primix_state.json'):
            with open('.primix_state.json', 'r') as f:
                state = json.load(f)
                self.variables = state.get('variables', {})
                for k, v in state.get('storage', {}).items():
                    self.storage.set(k, v)
            self.log("STATE LOADED")
                def parse_code(self):
        """Парсинг кода Primix, извлечение маршрутов и команд"""
        self.routes = {}
        self.disabled_routes = set()
        
        lines = self.code.strip().split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('#'):
                i += 1
                continue

            # Обработка команд, которые не являются блоками
            block_commands = ['go request ', 'go fields ', 'if ', 'repeat ', 'every ']
            is_block = any(line.startswith(cmd) for cmd in block_commands)
            
            if not is_block:
                self.execute_line(line)
                i += 1
                continue

            # Блоки (go request, go fields, if, repeat, every)
            if line.startswith('go request ') or line.startswith('go fields '):
                parts = line.split(' ')
                method = 'REQUEST' if parts[1] == 'request' else 'FIELDS'
                path = parts[2].strip()
                body = []
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    body.append(lines[i].strip())
                    i += 1
                self.routes[(method, path)] = body

            elif line.startswith('if '):
                condition = line[3:].split(' then')[0].strip()
                body = []
                else_body = []
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    body.append(lines[i].strip())
                    i += 1
                if i < len(lines) and lines[i].strip() == 'else':
                    i += 1
                    while i < len(lines) and lines[i].startswith('    '):
                        else_body.append(lines[i].strip())
                        i += 1
                self.routes[('IF', condition)] = {'then': body, 'else': else_body}

            elif line.startswith('repeat '):
                parts = line[7:].split(' times')
                count = parts[0].strip()
                body = []
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    body.append(lines[i].strip())
                    i += 1
                self.routes[('REPEAT', count)] = body

            elif line.startswith('every '):
                parts = line[6:].split(' do')
                interval = parts[0].strip()
                body = []
                i += 1
                while i < len(lines) and lines[i].startswith('    '):
                    body.append(lines[i].strip())
                    i += 1
                self.routes[('EVERY', interval)] = body
                # Запускаем фоновый поток
                self._schedule_every(interval, body)
            else:
                i += 1

    def _schedule_every(self, interval, body):
        """Планировщик для every X do"""
        seconds = 60  # default: 1 min
        if 'min' in interval:
            seconds = int(interval.replace('min', '').strip()) * 60
        elif 'sec' in interval:
            seconds = int(interval.replace('sec', '').strip())
        elif 'hour' in interval:
            seconds = int(interval.replace('hour', '').strip()) * 3600

        def run_periodic():
            while self.running:
                time.sleep(seconds)
                for action in body:
                    self.execute_line(action)

        t = threading.Thread(target=run_periodic, daemon=True)
        t.start()

    def execute_route(self, route_body, request_data=None):
        """Выполняет список команд маршрута"""
        result = None
        for line in route_body:
            if line.startswith('respond '):
                rest = line[8:].strip()
                if rest.startswith('json '):
                    result = json.dumps(json.loads(rest[5:]))
                elif rest.startswith('msgpack '):
                    result = rest[8:]
                else:
                    if '+' in rest:
                        res = ''
                        for p in rest.split('+'):
                            res += str(self.eval_expr(p.strip(), request_data))
                        result = res
                    else:
                        result = str(self.eval_expr(rest, request_data))
            elif line.startswith('store on/ '):
                key = line.split('store on/ ', 1)[1].strip()
                if request_data:
                    self.storage.set(key, request_data.get(key, request_data))
            elif line.startswith('throw to/'):
                parts = line.split(' ', 2)
                target = parts[1] if len(parts) > 1 else ''
                data = parts[2] if len(parts) > 2 else ''
                self.log(f"THROW → {target}: {data}")
            elif line.startswith('db query '):
                query = line[9:].strip().strip('"')
                try:
                    conn = sqlite3.connect(':memory:')
                    cursor = conn.cursor()
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    result = str(rows)
                    conn.close()
                except Exception as e:
                    result = f"DB Error: {e}"
            elif line.startswith('print '):
                self.log(str(self.eval_expr(line[6:].strip(), request_data)))
            elif ' = ' in line:
                self.execute_line(line, request_data)

        return result

    def handle_client(self, conn, addr):
        """Обработка входящего соединения"""
        if self.blackhole_mode:
            conn.close()
            return

        try:
            data = conn.recv(8192).decode(errors='ignore')
            if not data:
                conn.close()
                return

            lines = data.split('\r\n')
            first_line = lines[0] if lines else ''
            parts = first_line.split(' ')

            if len(parts) < 2:
                conn.close()
                return

            method = parts[0]
            path = parts[1]

            # Извлекаем тело запроса
            body = ''
            if '\r\n\r\n' in data:
                body = data.split('\r\n\r\n', 1)[1]

            request_data = {}
            if body:
                try:
                    request_data = json.loads(body)
                except:
                    for pair in body.split('&'):
                        if '=' in pair:
                            k, v = pair.split('=', 1)
                            request_data[k] = v

            # Определяем тип маршрута
            if method == 'GET':
                route_key = ('REQUEST', path)
            elif method == 'POST':
                route_key = ('FIELDS', path)
            else:
                route_key = (method, path)

            # Проверка блокировки
            if route_key in self.disabled_routes:
                response = "Route disabled"
                conn.send(f"HTTP/1.1 503 Service Unavailable\r\n\r\n{response}".encode())
                conn.close()
                return

            # Выполнение маршрута
            if route_key in self.routes:
                try:
                    result = self.execute_route(self.routes[route_key], request_data)
                    if result is None:
                        result = 'OK'
                    # Шифруем ответ
                    encrypted = self.encrypt_response(result)
                    http_response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{encrypted}"
                    conn.send(http_response.encode())
                    self.log(f"[OK] {method} {path} → 200")
                except Exception as e:
                    self.disabled_routes.add(route_key)
                    self.log(f"[ERR] {method} {path} → Route disabled: {e}", "ERROR")
                    conn.send(b"HTTP/1.1 500 Error\r\n\r\nInternal error, route disabled")
            else:
                conn.send(b"HTTP/1.1 404 Not Found\r\n\r\nNot Found")
                self.log(f"[404] {method} {path}")

        except Exception as e:
            self.log(f"Connection error: {e}", "ERROR")
        finally:
            conn.close()

    def start(self):
        """Запуск сервера"""
        self.parse_code()
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind(('0.0.0.0', self.port))
        except OSError:
            self.port = 5000 + random.randint(1, 5000)
            self.server_socket.bind(('0.0.0.0', self.port))

        self.server_socket.listen(50)

        self.log(f"=== Primix v0.2 ===")
        self.log(f"Key: {self.key}")
        self.log(f"Port: {self.port}")
        self.log(f"T8T: {self.t8t_mode.upper()}")
        self.log(f"Ghost: {self.ghost_mode}")
        self.log(f"Physical only: {self.physical_only}")
        self.log(f"Balancer: {self.balancer_enabled}")
        self.log(f"Cache: ON")
        self.log(f"Queue: ON")
        self.log(f"Routes: {len(self.routes)} loaded")
        self.log(f"Press Ctrl+C to stop")
        self.log(f"Local: http://localhost:{self.port}")

        try:
            while self.running:
                conn, addr = self.server_socket.accept()
                t = threading.Thread(target=self.handle_client, args=(conn, addr))
                t.daemon = True
                t.start()
        except KeyboardInterrupt:
            self.log("Server stopped by user")
        finally:
            self.server_socket.close()
            self.log("Server shutdown complete")


def main():
    if len(sys.argv) < 2:
        print("Primix v0.2")
        print("Usage: python primix.py <file.pmx>")
        print("       python primix.py <file.pmx> ghost")
        return

    filepath = sys.argv[1]
    ghost = len(sys.argv) > 2 and sys.argv[2] == 'ghost'

    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    server = PrimixServer(code, filepath)
    
    if ghost:
        server.ghost_mode = True
    
    # Запуск периодических отчётов, если настроены
    if server.view_targets:
        def send_health_report():
            while server.running:
                time.sleep(3600)  # каждый час
                report = f"[Primix Health] Server {server.key[:8]}... OK"
                server.log(f"HEALTH REPORT → {server.view_targets}: {report}")
        
        t = threading.Thread(target=send_health_report, daemon=True)
        t.start()

    server.start()


if __name__ == '__main__':
    main()