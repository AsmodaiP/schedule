from calendar import weekheader
from cmath import log
from concurrent.futures.process import _ExceptionWithTraceback
from datetime import date, datetime, timedelta
from sre_constants import RANGE
from time import time
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from dotenv import load_dotenv
import loguru
import telegram
from loguru import logger


SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', None)

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
ID_FOR_NOTIFICATION =  os.getenv('ID_FOR_NOTIFICATION', None)
bot = telegram.Bot(token=TELEGRAM_TOKEN)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials_service.json')
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
RANGE_NAME = os.environ['RANGE_NAME']
START_POSITION_FOR_PLACE = 14

logger.add('bot.log', rotation='20 KB',retention=2, backtrace=True)

days_range = {
    0: (3, 16),
    1: (17, 30),
    2: (31, 44),
    3: (45, 58),
    4: (59, 72),
    5: (73, 86)
}


def main():
    tommorow = datetime.today()+timedelta(1)
    weekday = tommorow.weekday()
    if weekday == 0:
        return True
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=f'{RANGE_NAME}E{days_range[weekday][0]}:E{days_range[weekday][1]}', majorDimension='ROWS').execute()
    values = result.get('values', [])
    msg = ''

    msg = '\n'.join([row[0] for row in values if len(row)>0])
    msg.replace('       ', '')
    bot.send_message(chat_id=ID_FOR_NOTIFICATION, text=msg, parse_mode='Markdown')
    return True


if __name__== '__main__':
    succsess = False
    while not  succsess:
        try:
            succsess = main()
        except Exception as e:
            logger.exception('Error')
            time.sleep(5)
