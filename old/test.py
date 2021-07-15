import requests
import asyncio
import time
import threading
import json
import os
import pprint

from datetime import datetime, timedelta
from itertools import combinations


params = {
    'fly_from': "TSE",
    'fly_to': "ALA",
    'date_from': '23%2F04%2F2020',
    'date_to': '20%2F05%2F2020',
    'partner': 'picky',
    'adults': 1,
    'children': 0,
    'infants': 0,
}

params1 = {
    'booking_token': 'Bo-ZcxrVB2MEXt8RTtBHdUmQn52acvAjaWBCrRVZXESDhElsMwpaLQ4F_rYs9yS-E4nSSS8GFholp9azISyBb-YJ7o0QLqE0JJvIIciDndRqRtksdYjt-_WkIKT7mfDj40UpzXVvxIbNmV3QPy4CS8iy-Earq4KnJatwGb5i9JMfUYDwozA6WjESClC4Igx9yD6MVFwln7q2_zWVbR7CGTnVe-GxOswAO9n-TJH-CGGbUe13v67xtnFm_4R0bno-t5xJ28g_-qrvC3Bw6wILnvBt7B3EA6ROG6pzGm4-5BxVVUwq0uZv4QfjEVA28fNQdFPzOboLE_D_IclId-iCWTGnjNYpplEQEvIDXWzyy1EDHPoO7aFiVSZAwsP7IIyzUjKWJhKpuHsAjeGX0WMBLfKUkbYzvlkcFA3OMmNJmCXZgb43iLVKhWwfoML1c56KJL-SvDEQAKTQakxBbzHv4cKdIAMcIwWXCsRvPPbzJ1a3UIekF9K4tizgWRBCZ_PzVdWMjWTcCm36Dcm8avu8Rz5srVTm6izABWdVX3aeaNVEOM3YOJ-e1FOXPNmeud9ONtqRj2vrHi5aMjOZoFQpGBA==',
    'currency': 'KZT',
    'bnum': 1,
    'pnum': 1,
    'adults': 1,
    'children': 0,
    'infants': 0,
    'partner': 'picky'
}

res = requests.get("https://api.skypicker.com/flights", params=params)

print(res.text)

# res1 = requests.get('https://booking-api.skypicker.com/api/v0.1/check_flights',
#                     params=params1)

# print(f"{res1.json()['price_change']}")


