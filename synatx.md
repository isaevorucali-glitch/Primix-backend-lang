# Синтаксис Primix

## Сервер

start run/server
start run/server ghost

## Маршруты

go request /hello then
    respond "GET ответ"

go fields /save then
    respond "POST ответ"

## Ответы

respond "текст"
respond json {"ключ": "значение"}
respond msgpack {"ключ": "значение"}

## Переменные

имя = "значение"
счётчик = 0
счётчик = счётчик + 1

## Хранилище

store on/ ключ
get to/ ключ

## Связь серверов

throw to/ключ данные
throw to/$key данные

## Условия

if счётчик больше 10 then
    respond "Много"
else
    respond "Мало"

## Циклы

repeat 3 times
    print "Повтор"

## Периодические задачи

every 5 min do
    print "Живой"

## База данных

db query "SELECT * FROM users"
db store users данные

## Файлы

file read "config.txt"
file write "log.txt" "текст"

## Команды управления

status              состояние сервера
log on/off          вкл выкл логи
debug on            отладка
env ключ = значение переменная окружения
ping ключ           проверка сервера
timeout сек         таймаут
list servers        список серверов
key rotate          сменить ключ
save state          сохранить
load state          загрузить
clear cache         очистить кеш

## Безопасность

/add t8t mixed      смешанный шифр
/add t8t jp         японский шифр
/add t8t en         английский шифр
/add t8t rnd        рандомный шифр
lock down           полная блокировка
physical only       только физический доступ
blackhole           режим тишины
intruder alert      тревога при вторжении
block key ключ      заблокировать
whitelist ключ      белый список
key expires 24h     срок ключа

## СОС и мониторинг

/add sos mod! ключ1 ключ2     запасные серверы
/view in its entirety ключ1    отчёты на комп

## Кластер

cache on            кеш
queue on            очередь
balance on          балансировка

## Экстренные

burn server         самоуничтожение
reload server       перезагрузка кода