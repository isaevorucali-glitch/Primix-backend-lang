# Синтаксис Primix v0.4

## Расширения файлов

- `.pmx` — серверный файл (бекенд)
- `.pwx` — файл-связка для фронтенда (лежит на фронте)

## .pwx синтаксис (фронтенд-связка)

connect to key <ключ>
routes /api/users
routes /api/data
ws /chat
timeout 5
reconnect on
reconnect interval 3

## Сервер

start run/server
start run/server ghost

## Маршруты

go request /path then
    respond "GET"

go fields /path then
    respond "POST"

## Ответы

respond "text"
respond json {"key": "value"}
respond msgpack {"key": "value"}

## Переменные

name = "Primix"
counter = 0
counter = counter + 1

## Условия

if counter > 10 then
    respond "High"
else
    respond "Low"

## Циклы

repeat 3 times
    print "Hello"

## Периодические

every 5 min do
    print "Alive"

## Хранилище

store on/ key
get to/ key

## Межсерверная связь

throw to/key data
throw to/$key data

## База данных

db query "SELECT * FROM users"
db store table data

## Файлы

file read "config.txt"
file write "log.txt" "content"

## Безопасность

/add t8t mixed|jp|en|rnd
lock down
physical only
blackhole
intruder alert
block key <key>
whitelist <key>
key expires 24h

## SOS и мониторинг

/add sos mod! backup1 backup2
/view in its entirety dev_laptop

## Управление

status
log on/off
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

## Экстренные

burn server
reload server
