import json

cities_list = ['Almaty', 'Astana', 'Moscow', 'Peter', 'Shymkent']

names = {
    'Almaty' : 'ALA',
    'Astana': 'TSE',
    'Moscow': 'MOW',
    'Peter': 'LED',
    'Shymkent': 'CIT',
}

cities_iata = ['ALA', 'TSE', 'MOW', 'LED', 'CIT']

dests = {
    'KZ': {
        'ALA': ['TSE', 'CIT', 'MOW'],
        'CIT': ['ALA'],
        'TSE': ['ALA', 'MOW', 'LED'],
    }
}

my_dict = {
    "ALA" : {
        "TSE":"",
        "MOW":"",
        "LED":"",
        "CIT":"",
    },
    "TSE": {
        "ALA":"",
        "MOW":"",
        "LED":"",
        "CIT":"",
    },
    "MOW":{
        "ALA":"",
        "TSE":"",
        "LED":"",
        "CIT":"",
    },
    "LED":{
        "ALA":"",
        "MOW":"",
        "TSE":"",
        "CIT":"",
    },
    "CIT":{
        "ALA":"",
        "MOW":"",
        "LED":"",
        "TSE":"",
    },
}
