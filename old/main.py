import os
import json
import requests
import asyncio
import time

from datetime import datetime, timedelta
from itertools import combinations

from destinations import *

my_cache = {}
'''
    Этот метод не безопасный, но как для тестового задания думал не перемудрять.
    А так весь кэш вижу как перспективу хранить в nosql дбшке.
'''

'''
    [x] - Сделать get запрос на сервер для отображения результатов
    [x] - Продумать как сохранять данные за 30 дней вперед
    [~] - Подтверждать тикеты по токену

    PS. Я ничего не понял насчёт подтверждения билетов. При каких условиях
    должен подтверждать их. Разве если я только что их взял, то они не и так
    валидны? Что должно мне передаваться, чтобы подтверждать их валидность в
    тот или иной момент? Те параметры, которые вписаны? И как мне их хранить?
    Как мне потом их передавать? В примере указано ещё bnum. Он нам передается?
    Как формируется этот check flight-ов? Насколько часто мне это нужно делать?
'''

def verify_ticket (booking_token, currency='KZT',
                        adults=1, children=0, infants=0):
    params = {
        'booking_token': booking_token,
        'currency': currency,
        'pnum': adults + children + infants,
        'adults': adults,
        'children': children,
        'infants': infants,
        'partner': 'picky'
    }
    res1 = requests.get('https://booking-api.skypicker.com/api/v0.1/check_flights',
                        params=params)
    '''
        Я не до конца понял что нужно тут делать... Но запрос насколько понял
        должен выполняться не recurrently. Поэтому нужды в async не увидел.
        Для юзания в проде, нужно чуть больше времени, чтобы ознакомиться с этим
        API и аргументами, которые он получает...
    '''


async def get_price(from_dest, to_dest, date_from, date_to,
                    adults=1, children=0, infants=0):
    params = {
        'fly_from': from_dest,
        'fly_to': to_dest,
        'date_from': date_from,
        'date_to': date_to,
        # format of dd/mm/yyyy
        'partner': 'picky',
        'adults': adults,
        'children': children,
        'infants': infants,
    }
    res = requests.get("https://api.skypicker.com/flights", params=params)
    print(json.dumps(res.json(), indent=4, sort_keys=True))
    return res.json()

async def update_24 ():
    while True:
        curr = datetime.now()
        days_30 = curr + timedelta(days=30)
        print(f"Now the date is {curr} and in 30 days the date will be {days_30}")

        for x in dests['KZ']:
            for y in dests['KZ'][x]:
                my_cache[f"{x}-{y}"] = await get_price(x, y,
                                f"{curr.day}/{curr.month}/{curr.year}",
                                f"{days_30.day}/{days_30.month}/{days_30.year}")
                my_cache[f"{y}-{x}"] = await get_price(y, x,
                                f"{curr.day}/{curr.month}/{curr.year}",
                                f"{days_30.day}/{days_30.month}/{days_30.year}")

        '''
            Updates when 00:00 ticks on a clock
        '''
        nearest = datetime((curr + timedelta(days=1)).year,
                            (curr + timedelta(days=1)).month,
                            (curr + timedelta(days=1)).day,
                            00, 00)

        await asyncio.sleep((nearest - curr).total_seconds())


async def main():
    '''
        puts all tasks in a recurrent mode.
    '''
    updating_every_day = asyncio.create_task(update_24())

    # task2 = asyncio.create_task(update_24())

    await updating_every_day
    # await task2
