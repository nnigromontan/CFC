# Telegram Chat bot HDE integration 

# Этот бот предназначен для клиентов Helpdeskeddy. 
Функции бота: 
1. С помощью цепочки запросов получает информацию о конкретной заявке или заявках организации, сохраняет свойства этой заявки и в случае изменений отправляет клиенту оповещение.
2. Может вывести информацию о заявке или отфильтрованный список заявок по запросу клиента (/details, /tickets)
3. Для работы бота необходимы токены TELEGRAM_TOKEN, HELPDESK_TOKEN и TELEGRAM_CHAT_ID, хранящиеся в .env 

Получить HELPDESK_TOKEN можно с помощью конструкции
<import base64
encoded = base64.b64encode(b'alexandr.bogus@ugitsevice.com:a2e3a456-bb2b-48ea-8c2e-db84ade9bee7')
print(encoded)>

Описание API Helpdesk: https://helpdeskeddy.ru/api

# Авторы проекта
Александр Богус и Андрей Сергеев
