import os
import logging
import time
import requests
from dotenv import load_dotenv
from http import HTTPStatus

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

cfc_id = 483
ticket_id = 157142


def get_employees():
    URL = (HOST.__add__(f'/organizations/{cfc_id}'))
    try:
        session = requests.session()
        response = session.get(URL, headers=HEADERS)
        logger.info('API request successfully done!')
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f'Request error: {ConnectionError}'
                               f'Requesting endpoint: {HOST}'
                               f'Header: {HEADERS}')
        response = response.json()
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
    employees = response['data']['employees']
    employees = ','.join(str(x) for x in employees)
    return employees


def get_tickets():
    employees = get_employees()
    logger.info('Succesfully get employees from API.')
    URL = (HOST.__add__(f'/tickets/?user_list={employees}'))
    try:
        session = requests.session()
        response = session.get(URL, headers=HEADERS)
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


def get_ticket_id_from_tickets():
    """Получаем словарь с номерами ID заявок из списка"""
    tickets = get_tickets()
    logger.info('Succesfully get tickets list from API.')
    tickets_id = tickets['data'].keys()
    return tickets_id

def get_ticket():
    """Получаем конкретную заявку по ID"""
    try:
        session = requests.session()
        response = session.get((HOST.__add__(f'/tickets/{ticket_id}')), headers=HEADERS)
        logger.info('API request successfully done!')
        if response.status_code != HTTPStatus.OK:
            raise RuntimeError(f'Request error: {ConnectionError}'
                               f'Requesting endpoint: {HOST}'
                               f'Header: {HEADERS}')
        ticket = response.json()
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
    return ticket
    

def get_ticket_params():
    """Получаем значения owner, priority_id и status_id из заявки"""
    ticket = get_ticket()
    owner = ticket['data']['owner_name'] + ' ' + ticket['data']['owner_lastname']
    priority_id = ticket['data']['priority_id']
    status_id = ticket['data']['status_id']
    ticket_params = {
        'owner': owner,
        'priority_id': priority_id,
        'status_id': status_id,
    }
    return ticket_params

def session_identity_check(ticket_params):
    new_ticket_params = get_ticket_params()
    if ticket_params.values() != new_ticket_params.values():
        return True
    else:
        return False


print(session_identity_check(get_ticket_params()))
