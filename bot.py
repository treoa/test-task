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


class DoesNotExist(Exception):
    """
        When such ticket does not exist in cache with given destinations
    """
    pass


class InvalidRequestError(ValueError):
    """
        When an invalid request for ticker verification is sent
    """
    pass


class FlighUnavailable(Exception):
    """
        When the given flight in verification is given as invalid for booking
    """
    pass


async def parse_dates(state:FSMContext):
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
            min_price = float('inf')
            for a in range(len(the_res['data'])):
                if the_res['data'][a]['price'] < min_price:
                    min_book_token = the_res['data'][a]['booking_token']
            my_dict[from_dest][to_dest] = min_book_token if min_book_token != 0 else ""
            async with state.proxy() as data:
                data['parsed'] = my_dict


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
    try:
        res1 = requests.get('https://booking-api.skypicker.com/api/v0.1/check_flights',
                        params=params)
        if res1.status_code == 200:
            return json.loads(res1.text)
        else:
            raise InvalidRequestError
    except InvalidRequestError:
        print(f"The request was sent incorrectly")

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
async def start_handler(message: types.Message, state:FSMContext):
    """
        Default start handler
    """
    await Form.started.set() 
    await send_message(message.from_user.id, "Привет, ответь мне если готов искать билеты на авиа")


async def parsing_cncrtly(state: FSMContext):
    while True:
        now = datetime.now()
        future_t = datetime(now.year, now.month, now.day, 23, 59)
        delta_t = future_t - now
        delta_t = delta_t.total_seconds() + 60
        await asyncio.sleep(delta_t)
        parse_dates(state)


async def send_scnd_msg(message:types.Message):
    await send_message(message.from_user.id, "Откуда летим? Отправьте в формате IATA")
    await Form.asked_from.set()


@dp.message_handler(state=Form.started)
async def ask_from(message: types.Message, state: FSMContext):
    """
        Ask destination from where passenger is flying
    """
    await send_message(message.from_user.id, "Подожди пока обновятся цены. В идеале это будет делаться без тебя, но сейчас я вынужден обновить свою информацию о билетах!\n Я напишу тебе через несколько секунд!")
    t1 = asyncio.create_task(parsing_cncrtly(state))
    t2 = asyncio.create_task(send_scnd_msg(message))
    await t1
    await t2


@dp.message_handler(state=Form.asked_from)
async def ask_to(message: types.Message, state: FSMContext):
    """
        Ask destination to where passenger is flying
    """
    async with state.proxy() as data:
        data['fly_from'] = message.text
    await send_message(message.from_user.id, "Куда летим? Отправьте в формате IATA")
    await Form.asked_to.set()
    

@dp.message_handler(state=Form.asked_to)
async def checking_ticket(message: types.Message, state: FSMContext):
    """
        Ask verification from passenger
    """
    async with state.proxy() as data:
        data['fly_to'] = message.text
    await Form.checking.set()
    try:
        async with state.proxy() as data:
            token = data['parsed'][data['fly_from'][data['fly_to']]]
            if token == "":
                raise DoesNotExist
            msg = f"Passengers: 1 \nAdults: 1 \nChildren: 0 \nInfants: 0\nFly from: {data['fly_from']} \nFly to: {data['fly_to']}"
            yes_btn = InlineKeyboardButton('Да!', callback_data='yes')
            await bot.send_message(message.from_user.id, 'Подтверди',
                           reply_markup=yes_btn)
    except DoesNotExist:
        print(f"Such ticket does not exist")


@dp.message_handler(text="yes", state=Form.checking)
async def verify_ticket(query: types.CallbackQuery, state: FSMContext):
    """
        Checking the ticket for availability
    """
    try:
        async with state.proxy() as data:
            res = verification(booking_token = data['parsed'][data['fly_from']][data['fly_to']])
            if not res['flights_invalid'] and res['flights_checked']:
                print(res)
                await send_message(query.from_user.id, f"```{res}```", parse_mode=types.ParseMode.MARKDOWN)
                # Here we will make our manipulations with the flight ticket as we need. For now I am not given any further instructions
            else:
                raise FlighUnavailable
    except FlighUnavailable:
        print(f"The chosen flight is unavailale")


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