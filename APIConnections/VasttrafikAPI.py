import base64
import json
import time as time_module

import requests
import yaml
import os

TOKEN_URL = 'https://api.vasttrafik.se/token'
API_BASE_URL = 'https://api.vasttrafik.se/bin/rest.exe/v2'
API_SETTINGS_FILE = os.path.dirname(os.path.abspath(__file__)) +'\\api_settings.yml'


def fetch_token(key, secret):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + base64.b64encode((key + ':' + secret).encode()).decode()
    }
    data = {'grant_type': 'client_credentials'}

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    obj = json.loads(response.content.decode('UTF-8'))
    return obj['access_token']


class VasttrafikClient:

    @staticmethod
    def merge_dicts(d1, d2):
        d = d1.copy()
        for k, v in d2.iteritems():
            d[k] = v
        return d

    @staticmethod
    def latlon_to_string_representation(latlon):
        return str(round(latlon * 1000000)).rstrip('0').rstrip('.')

    def __init__(self, key=None, secret=None):

        with open(API_SETTINGS_FILE, 'r') as stream:
            try:
                api_settings = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        if key is None:
            key = api_settings['Vasttrafik']['Key']

        if secret is None:
            secret = api_settings['Vasttrafik']['Secret']
        self.token = fetch_token(key, secret)
        self.format = 'json'

    # /location.allstops
    def get_all_stops(self, query_params=None):
        data = self.get('/location.allstops')
        return data['LocationList']['StopLocation']

    # /location.nearbystops
    def get_nearby_stops(self, lat, long, query_params=None):
        data = self.get('/location.nearbystops?originCoordLat=' + str(lat) + '&originCoordLong=' + str(long))
        return data['LocationList']['StopLocation']

    # /location.name
    def get_stops_by_name(self, query, query_params=None):
        data = self.get('/location.name?input=' + query, query_params)
        return data['LocationList']['StopLocation']

    # /arrivalBoard endpoint
    def get_arrivals(self, stopID, date=None, time=None, query_params=None):
        if date is not None and time is not None:
            get_str = '/arrivalBoard?id=' + str(stopID) + '&date=' + date + '&time=' + time
        else:
            get_str = '/arrivalBoard?id=%d&date=%s&time=%s' % \
                      (stopID, time_module.strftime("%Y-%m-%d"), time_module.strftime("%H:%M"))
        data = self.get(get_str, query_params)
        return data['ArrivalBoard']['Arrival']

    # /departureBoard endpoint
    def get_departures(self, stopID, date=None, time=None, query_params=None):
        if date is not None and time is not None:
            get_str = '/departureBoard?id=' + str(stopID) + '&date=' + date + '&time=' + time
        else:
            get_str = '/departureBoard?id=%s&date=%s&time=%s' % \
                      (stopID, time_module.strftime("%Y-%m-%d"), time_module.strftime("%H:%M"))
        data = self.get(get_str, query_params)
        try:
            return data['DepartureBoard']['Departure']
        except KeyError:
            # No departures found
            return list()

    # /trip endpoint
    def calculate_trip_stations(self, start_id, stop_id, query_params=None):
        return self.get('/trip?originId=%d&destId=%d' % (start_id, stop_id), query_params)

    def get(self, endpoint, query_params=None):
        url = API_BASE_URL + endpoint

        if query_params is not None:
            for key, value in query_params.iteritems():
                url += '&' + key + '=' + value
            url += '&format=' + self.format
        elif '?' in url:
            url += '&format=' + self.format
        else:
            url += '?format=' + self.format

        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return json.loads(res.content.decode('UTF-8'))
        else:
            raise Exception('Error: ' + str(res.status_code) + str(res.content))


if __name__ == '__main__':
    c = VasttrafikClient()
    print 'Loaded client'
