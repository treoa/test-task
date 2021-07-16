import dateutil
import requests
import json
import asyncio
import logging

from datetime import date, datetime
from bottle import (run, post, response, request as breq)
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.utils import exceptions
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


from creds import *
from destinations import my_dict


# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')


# Configure local aiogram storage
'''
    Recommended to use Redis, but in testing version Redis seems okay. But in the same way 
    via aiogram you up your redis server and configure it right in this file.
    The major disadvantage of local storage is that for each user the storage will be 
    built up individually and it needs to have updating for each of the user local cache.
'''
storage = MemoryStorage()
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


bot_url = f"'https://api.telegram.org/bot{API_TOKEN}/'"


class Form(StatesGroup):
    started = State()
    asked_from = State()
    asked_to = State()
    checking = State()
    verifying = State()
    finished = State()


async def parse_dates(state: FSMContext):
    '''
        Here is the update of prices should be. But for now it cannot be done, because of 
        absence of affiliate ID to use the Kiwi API.
        Even though I have the familiarity with thus API, I would do according to it. But,
        eventually some fields could be missed, because I need an official connection to 
        the API, otherwise server side refuses with 400 error.
    '''
    print(f"Updating the prices")
    now = datetime.now()
    for from_dest in my_dict:
        for to_dest in my_dict[from_dest]:
            params = {
                'fly_from': from_dest,
                'fly_to': to_dest,
                'date_from': f'{now.strftime("%d")}%2F{now.strftime("%m")}%2F{now.strftime("%Y")}',
                'date_to': f'{(now + dateutil.relativedelta.relativedelta(months=1)).strftime("%d")}%2F{(now + dateutil.relativedelta.relativedelta(months=1)).strftime("%m")}%2F{(now + dateutil.relativedelta.relativedelta(months=1)).strftime("%Y")}',
                'partner': 'picky',
                'adults': 1,
                'children': 0,
                'infants': 0,
            }
            while True:
                """
                    asyncio sleep guarantees us that during sleep other processes will be still continued 
                    and will not be reallocated for sleep fn.
                    Assuming that the code will be started right at 12 AM. Later it can be redone using 
                    timedelta and timenow
                """
                res = requests.get("https://api.skypicker.com/flights", params=params)
                # Here is the parsing of json file should be done, which I do not know how json file looks like
                the_res = json.loads(res.text)
                min_book_token = 0
                for a in range(len(the_res['data'])):
                    if the_res['data'][a]['price'] < min_price:
                        min_book_token = the_res['data'][a]['booking_token']
                my_dict[from][to] = min_book_token




async def verification (booking_token:str, currency:str ='KZT', adults:int = 1, children:int = 0, infants:int = 0):
    '''
        Verify tickets. Request way could be incorrect, because I do not have an access to the API,
        because of the registration issues for it, so server refuses my requests.
    '''
    params = {
        'booking_token': booking_token,
        'currency': 'KZT',
        'bnum': 1,
        'pnum': adults+infants+children,
        'adults': adults,
        'children': children,
        'infants': infants,
        'partner': 'picky'
    }

    res1 = requests.get('https://booking-api.skypicker.com/api/v0.1/check_flights',
                        params=params)

    print(f"{res1.json()['price_change']}")


async def send_message(user_id: int, text: str,
                       disable_notification: bool = False,
                       parse_mode=types.ParseMode.HTML) -> bool:
    """
        Safe messages sender
    """
    try:
        await bot.send_message(user_id, text,
                               disable_notification=disable_notification,
                               parse_mode=types.ParseMode.HTML)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep \
                    {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text, disable_notification,
                                  parse_mode)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


@dp.message_handler(state="*", commands='start')
async def start_handler(message: types.Message):
    """
        Default start handler
    """
    await Form.started.set()
    await send_message(message.from_user.id, "Привет, ответь мне если готов искать билеты на авиа!")


@dp.message_handler(state=Form.started)
async def ask_from(message: types.Message, state: FSMContext):
    """
        Ask destination from where passenger is flying
    """
    await send_message(message.from_user.id, "Куда летим? Отправьте в формате IATA")
    await Form.asked_from.set()



@dp.message_handler


async def on_shutdown():
    '''
        Upon the connection of the REDIS database for caching, it is needed to be closed on shutdown.
        But for this version, redis is not needed.
    '''
    # await dp.storage.close()
    # await dp.storage.wait_closed()
    pass

if __name__ == '__main__':
    print(f"The bost has started\n")
    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)