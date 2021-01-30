import requests
import asyncio
import time
import threading
import json
import os
import pprint
import colorama

from datetime import datetime, timedelta
from itertools import combinations

from destinations import *

# params = {
#     'fly_from': "TSE",
#     'fly_to': "ALA",
#     'date_from': '01/03/2021',
#     'date_to': '02/03/2021',
#     'partner': 'picky',
#     'adults': 1,
#     'children': 0,
#     'infants': 0,
# }
#
# params1 = {
#     'booking_token': 'Bo-ZcxrVB2MEXt8RTtBHdUmQn52acvAjaWBCrRVZXESDhElsMwpaLQ4F_rYs9yS-E4nSSS8GFholp9azISyBb-YJ7o0QLqE0JJvIIciDndRqRtksdYjt-_WkIKT7mfDj40UpzXVvxIbNmV3QPy4CS8iy-Earq4KnJatwGb5i9JMfUYDwozA6WjESClC4Igx9yD6MVFwln7q2_zWVbR7CGTnVe-GxOswAO9n-TJH-CGGbUe13v67xtnFm_4R0bno-t5xJ28g_-qrvC3Bw6wILnvBt7B3EA6ROG6pzGm4-5BxVVUwq0uZv4QfjEVA28fNQdFPzOboLE_D_IclId-iCWTGnjNYpplEQEvIDXWzyy1EDHPoO7aFiVSZAwsP7IIyzUjKWJhKpuHsAjeGX0WMBLfKUkbYzvlkcFA3OMmNJmCXZgb43iLVKhWwfoML1c56KJL-SvDEQAKTQakxBbzHv4cKdIAMcIwWXCsRvPPbzJ1a3UIekF9K4tizgWRBCZ_PzVdWMjWTcCm36Dcm8avu8Rz5srVTm6izABWdVX3aeaNVEOM3YOJ-e1FOXPNmeud9ONtqRj2vrHi5aMjOZoFQpGBA==',
#     'currency': 'KZT',
#     'bnum': 1,
#     'pnum': 1,
#     'adults': 1,
#     'children': 0,
#     'infants': 0,
#     'partner': 'picky'
# }
#
# res = requests.get("https://api.skypicker.com/flights", params=params)
#
# print(res.json()['data'][0]['booking_token'])
#
# res1 = requests.get('https://booking-api.skypicker.com/api/v0.1/check_flights',
#                     params=params1)
#
# print(f"{res1.json()['price_change']}")



# my_list = ['asdasdasd', 'asd', 'qwe']
# testing_str = "asd"
# curr = datetime.now()
# days_30 = curr + timedelta(days=1)
# print(f"Now the date is {curr} and in 30 days the date will be {days_30}")
# res = {}
# combs = list(combinations(my_list, 2))
# print(combs)
# for x in my_list:
#     res[f"{x}-{next(y for y in my_list if y is not x)}"] = 32
# print(res)



# async def say_after(delay, what):
#     while True:
#         await asyncio.sleep(delay)
#         print(what)
#
# async def main():
#     task1 = asyncio.create_task(
#         say_after(1, 'hello'))
#
#     task2 = asyncio.create_task(
#         say_after(2, 'world'))
#
#     print(f"started at {time.strftime('%X')}")
#
#     # Wait until both tasks are completed (should take
#     # around 2 seconds.)
#     await task1
#     await task2
#
#     print(f"finished at {time.strftime('%X')}")
#
# asyncio.run(main())



# # use datetime
# from datetime import datetime, timedelta
#
# # get current time
# curr = datetime.now()
#
# # create object of nearest 16:30
# nearest = datetime(curr.year, curr.month, curr.day+1, 00, 00)
#
#
# # stupidly check if it's indeed the next nearest
# if nearest < curr:
#     nearest += timedelta(days=1)
#
# # get diff in seconds
# print(f"The current time is: {curr.day}:{curr.hour}:{curr.minute}:{curr.second}\n")
# print(f"The nearest time is: {nearest.day}:{nearest.hour}:{nearest.minute}:{nearest.second}\n")
# print (f"{(nearest - curr).total_seconds()}")



# for x in dests['KZ']:
#     for y in dests['KZ'][x]:
#         print(f"{x} - {y}")
