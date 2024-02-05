import requests


def get_static(**params):
    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=params)
    return response.content


def geocode(name):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": name,
        "format": "json"}
    response = requests.get(geocoder_api_server, params=params)

    if not response:
        print('Error', response.reason, response.status_code)
        exit(-1)

    return response.json()


def get_toponym(json_data):
    return json_data["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]


def get_toponym_coord(toponym):
    return list(map(float, toponym['Point']['pos'].split(" ")))


def get_spn(toponym):
    lon1, lat1 = map(float, toponym['boundedBy']['Envelope']["lowerCorner"].split())
    lon2, lat2 = map(float, toponym['boundedBy']['Envelope']["upperCorner"].split())
    return lon2 - lon1, lat2 - lat1


def search_org(**params):
    search_api = 'https://search-maps.yandex.ru/v1/'
    api_key = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'
    params['apikey'] = api_key
    response = requests.get(search_api, params=params)

    if not response:
        print('Error', response.reason, response.status_code)
        exit(-1)

    return response.json()


def get_org(json_data):
    org = json_data['features']
    return org


def get_org_info(org):
    org_name = org["properties"]["CompanyMetaData"]["name"]
    org_address = org["properties"]["CompanyMetaData"]["address"]
    org_hours = org['properties']['CompanyMetaData']['Hours']
    return org_name, org_address, org_hours['text']


def get_org_coords(org):
    point = org['geometry']['coordinates']
    return point
