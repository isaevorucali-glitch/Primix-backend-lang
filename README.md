# Primix 🚀

Первый в мире бекенд-язык с соединением по ключам и T8T шифрованием.

---

## Что такое Primix

Primix — это язык для создания серверов. Серверы находят друг друга по ключам, а не по IP-адресам. Трафик шифруется через T8T.

Написан на Python. Работает везде: Windows, Linux, Mac, Android, Raspberry Pi.

---

## Почему Primix

- Нет IP-адресов и портов — только ключи
- Нет HTTP-уязвимостей — свой протокол
- Нет сложной настройки — запустил и работает
- Не падает при ошибке — маршруты изолированы
- Шифрует всё — даже если перехватят, не прочитают

---

## Быстрый старт

```bash
git clone https://github.com/ТВОЙ_ЛОГИН/primix-lang.git
cd primix-lang
python primix_async.py examples/server.pmx
```

Открой браузер: localhost:5847/hello

---

Расширения файлов

Расширение Что это
.pmx Серверный файл (бекенд)
.pwx Файл-связка для фронтенда (лежит на фронте, подключает к серверу)

---

Пример .pmx (сервер)

```
start run/server
log on
cache on

counter = 0
server_name = "Alpha"

go request /hello then
    respond "Hello, World!"

go request /api/users then
    respond json {"name": "Ivan", "age": 13}

go fields /save then
    store on/ data
    respond "Saved!"

go request /count then
    counter = counter + 1
    respond "Requests: " + counter

every 5 min do
    print "Server alive"
```

---

Пример .pwx (связка на фронтенде)

```
connect to key xK9mF2wQ7vL4pR1nT8yU5bN3hJ6cA0dG

routes /api/users
routes /api/data
routes /api/auth

ws /chat

timeout 5
reconnect on
reconnect interval 3
```

---

Возможности

· 🔑 Связь серверов по ключам (не по IP)
· 🔐 T8T шифрование (3 слоя: mixed, jp, en, rnd)
· 👻 Режим призрака (сервер невидим в сети)
· 🆘 SOS авто-переброс задач при падении
· 📊 Отчёты на обычный компьютер каждый час
· 💻 Кроссплатформенность
· 📝 Простой синтаксис (учится за час)
· 🛡️ Изоляция маршрутов (один упал — остальные живы)
· 📦 JSON + MessagePack
· 🗄️ SQLite база данных
· ⚡ Кеш, очереди, балансировка
· 🏠 Физический доступ только с места
· 📋 Логирование в файл
· 🔄 WebSocket для реалтайма

---

Синтаксис

Сервер

```
start run/server
start run/server ghost
```

Маршруты

```
go request /path then
    respond "GET"

go fields /path then
    respond "POST"
```

Ответы

```
respond "text"
respond json {"key": "value"}
respond msgpack {"key": "value"}
```

Переменные

```
name = "Primix"
counter = 0
counter = counter + 1
```

Условия

```
if counter > 10 then
    respond "High"
else
    respond "Low"
```

Циклы

```
repeat 3 times
    print "Hello"
```

Периодические задачи

```
every 5 min do
    print "Alive"
```

Хранилище

```
store on/ key
get to/ key
```

Межсерверная связь

```
throw to/key data
throw to/$key data
```

База данных

```
db query "SELECT * FROM users"
db store table data
```

Файлы

```
file read "config.txt"
file write "log.txt" "content"
```

Безопасность

```
/add t8t mixed
/add t8t jp
/add t8t en
/add t8t rnd
lock down
physical only
blackhole
intruder alert
block key enemy_key
whitelist trusted_key
key expires 24h
```

SOS и мониторинг

```
/add sos mod! backup1 backup2
/view in its entirety dev_laptop
```

Управление

```
status
log on / off
debug on
clear cache
cache on
queue on
balance on
env key = value
ping key
timeout 30
list servers
key rotate
save state
load state
```

Экстренные
'''
burn server
reload server
```

---

Инструменты

Инструмент Файл Что делает
Интерпретатор primix_async.py Запускает .pmx файлы
IDE ide.py Редактор с подсветкой и логами
Лаунчер launcher.pyw Запуск в 2 клика
Пакетный менеджер primix_pm.py Установка пакетов
Балансировщик balancer.go Распределение нагрузки

---

Пакетный менеджер

```bash
python primix_pm.py available
python primix_pm.py install auth
python primix_pm.py list
python primix_pm.py search cache
```

Встроенные пакеты: auth, db, cache, logger, api, security

---


---

Дорожная карта

Версия Что
v0.2 Базовый сервер + синтаксис
v0.3 Async ядро + все фичи
v0.4 Пакетный менеджер
v0.5 Балансировщик на Go
v0.6 WebSocket + реалтайм
v0.7 Кластеры автоскейл
v0.8 PBP протокол
v0.9 Альфа-релиз
v1.0 Ядро на Go (миллион юзеров)
v2.0 Релиз

---

Автор
prime41k
