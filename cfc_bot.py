import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='journal.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
)

logger = logging.getLogger()

HELPDESK_TOKEN = os.getenv('HELPDESK_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 60
HOST = 'https://helpdesk.ugits.net/api/v2'
HEADERS = {'Authorization': f'Basic {HELPDESK_TOKEN}'}

TICKET_STATUSES = {
    'na-soglasovanii': 'Заявка на согласовании, и ждет распреления.',
    'naznacheno': 'Заявка назначена, ответственный исполнитель {owner}.',
    'prinjato': 'Заявка принята в работу, и ждет выполнения.',
    'v-rabote': 'Заявка взята в работу исполнителем.',
    'na-storone-klienta': 'Заявка на вашей стороне и требует вашего внимания!',
    '10-trebuetsja-kontrol': 'Заявка требует вашего внимания, пожалуйста свяжитесь с нами!',
    '14': 'Заявка выполнена: просим оценить качество работы!',
}

TICKET_PRIORITIES = {
    '1': 'Приоритет вашей заявки - Важно',
    '2': 'Приоритет вашей заявки - Нужен Приоритет',
    '3': 'Приоритет вашей заявки - Минимальный',
    '4': 'Приоритет вашей заявки - Срочно',
    '5': 'Приоритет вашей заявки - Выполнение отложено',
    '6': 'Приоритет вашей заявки - Стандартный',
    '7': 'Приоритет вашей заявки - Блокирующий',  
    '8': 'Приоритет вашей заявки - Критический',  
}

cfc_id = 483


def get_employees(cfc_id):
    params = {'id': cfc_id}
    try:
        response = requests.get((HOST.join('organizations/{cfc_id}')), headers=HEADERS, params=params)
        logger.info('API request successfully done!')
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f'Request error: {ConnectionError}'
                               f'Requesting endpoint: {HOST}'
                               f'Header: {HEADERS}')
        employees = response.json({"data":"employees"})
    except requests.JSONDecodeError as error:
        logger.error(f'Unable to decode JSON: {error}')
        raise requests.JSONDecodeError
    except requests.exceptions.Timeout as error:
        logger.error(f'Client did not send request in time: {error}')
        raise requests.exceptions.Timeout
    except requests.HTTPError as error:
        logger.error(f'Connection error: {error}')
        raise requests.HTTPError
    except requests.RequestException as error:
        logger.error(f'Incorrect response: {error}')
        raise SystemExit(error)
    return employees


def get_tickets(employees):
    params = {'user_list': employees}
    try:
        response = requests.get((HOST.join('tickets/user_list={employees}')), headers=HEADERS, params=params)
        logger.info('API request successfully done!')
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f'Request error: {ConnectionError}'
                               f'Requesting endpoint: {HOST}'
                               f'Header: {HEADERS}')
        tickets = response.json()
    except requests.JSONDecodeError as error:
        logger.error(f'Unable to decode JSON: {error}')
        raise requests.JSONDecodeError
    except requests.exceptions.Timeout as error:
        logger.error(f'Client did not send request in time: {error}')
        raise requests.exceptions.Timeout
    except requests.HTTPError as error:
        logger.error(f'Connection error: {error}')
        raise requests.HTTPError
    except requests.RequestException as error:
        logger.error(f'Incorrect response: {error}')
        raise SystemExit(error)
    return tickets 

def get_ticket(tickets):
    """Получаем конкретную заявку из списка заявок"""
    logger.info(tickets)


def send_message(bot, message):
    """Отправляет сообщение в Telegram."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Message has been sent successfully')
    except telegram.TelegramError as error:
        logger.error(f'Message has not been sent beacause of {error}')



def check_ticket_response(response):
    """Проверка ответа API на соответствие ожиданиям."""
    if not isinstance(response, dict):
        raise TypeError('Incorrect DATA type!')
    if 'status_id' not in response:
        raise KeyError('Expected dict keys are missing!')
    status_id = response.get('status_id')
    priority_id = response.get('priority_id')
    ticket_owner = response.get('owner_name', 'owner_lastname')
    return status_id, priority_id, ticket_owner


def parse_status(ticket, status_id):
    """Определяет статус, приоритет и исполнителя заявки."""
    if ticket is None:
        logger.error('Empty ticket value!')
        raise ValueError('Empty ticket value!')
    try:
        ticket_status = ticket['status_id'] #сохранить в сессию
        ticket_priority = ticket['priority_id']
        ticket_owner = ticket['owner_name', 'owner_lastname']
    except KeyError:
        logger.error('Expected dict keys are missing!')
        raise KeyError('Expected dict keys are missing!')
    except ValueError:
        logger.error('Variable value is empty!')
        raise ValueError('Variable value is empty!')
    if status_id not in TICKET_STATUSES:
        logger.error('Unknown ticket status')
        raise ValueError('Unknown ticket status')
    verdict_status = TICKET_STATUSES[ticket_status]
    verdict_priority = TICKET_PRIORITIES[ticket_priority]
    parse_result = (
        f'Изменился статус выполнения заявки "{ticket}". {verdict_status}',
        f'Изменился приоритет выполнения заявки "{ticket}". {verdict_priority}',
        f'Изменился исполнитель заявки - назначен {ticket_owner}.'
    )
    return parse_result

def check_ticket_status_change(ticket):
    """Проверяет изменения в заявке раз в 60 секунд."""
    if ticket is None:
        logger.error('Empty ticket value!')
        raise ValueError('Empty ticket value!')
    ticket_status_check = ticket.get('status_id')
    ticket_priority_check = ticket.get('priority_id')
    ticket_owner_check = ticket.get('owner_name', 'owner_lastname')

def check_tokens():
    """Проверяет запрос на наличие необходимых переменных."""
    if not HELPDESK_TOKEN or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.critical('Empty token value!')
        return False
    else:
        return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    if check_tokens():
        logger.info('Correct tokens received')
    else:
        raise ValueError('Empty token value!')

    while True:
        try:
            response_1 = get_employees(cfc_id)
            response_2 = get_tickets(response_1)
            tickets = check_ticket_response(response_2)
            if tickets is None:
                logger.error('Tickets list is empty!')
                raise ValueError('tickets value is empty!')
            status_tickets = tickets[0].get('status_id')
            if status_tickets is None:
                logger.debug('No status updates')
                raise ValueError('status_tickets value is empty!')
            message = parse_status(tickets[0])
            send_message(bot, message)
        except ValueError:
            logger.error('Variable value is empty!')
            raise ValueError('Variable value is empty!')
        except ConnectionError as error:
            logger.error(f'Endpoint is unavailable {error}!')
            raise ConnectionError(f'Endpoint is unavailable {error}!')
        except Exception as error:
            message = f'Program crash: {error}'
            logger.error(message)
            send_message(bot, message)

        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
