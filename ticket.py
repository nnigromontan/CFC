import logging
import os
import json

import requests
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

cfc_id = 483
ticket_id = 5000

def get_employees():
    URL = (HOST.__add__(f'/organizations/{cfc_id}'))
    response = requests.get(URL, headers=HEADERS)
    logger.info('API request successfully done!')
    response = response.json()
    employees = response['data']['employees']
    employees = ','.join(str(x) for x in employees)
    return employees

def get_tickets():
    employees = get_employees()
    URL = (HOST.__add__(f'/tickets/?user_list={employees}'))
    response = requests.get(URL, headers=HEADERS)
    logger.info('API request successfully done!')
    tickets = response.json()
    return tickets

def get_ticket_id_from_tickets():
    """Получаем ID заявки из списка"""
    tickets = get_tickets()
    tickets_id = tickets['data'].keys()
    tickets_id = ','.join(str(x) for x in tickets_id)
    print(tickets_id)


def get_ticket():
    """Получаем конкретную заявку по ID из списка заявок"""
    response = requests.get((HOST.__add__(f'/tickets/{ticket_id}')), headers=HEADERS)
    response = response.json()
    logger.info(response)
    return print(response)

get_ticket_id_from_tickets()
