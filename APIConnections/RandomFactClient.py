import requests
import yaml
import os
import json

API_SETTINGS_FILE = os.path.dirname(os.path.abspath(__file__)) + '\\api_settings.yml'


class RandomFactClient:

    def __init__(self):
        with open(API_SETTINGS_FILE, 'r') as stream:
            try:
                api_settings = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.url = api_settings['random_fact']['url']

    def get_random_fact(self):
        """Get a random fact from the API"""
        return json.loads(requests.get(self.url).content.decode('UTF-8'))

    def get_random_english_fact(self):
        """Get a random fact that is in english from the API"""
        random_fact = self.get_random_fact()
        while random_fact['language'] != 'en':
            random_fact = self.get_random_fact()
        return random_fact


if __name__ == '__main__':
    randomClient = RandomFactClient()
    random_fact = randomClient.get_random_english_fact()
    print "tmp"