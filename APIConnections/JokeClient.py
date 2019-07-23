import requests
import yaml
import os
import json

API_SETTINGS_FILE = os.path.dirname(os.path.abspath(__file__)) + '\\api_settings.yml'


class JokeClient:

    def __init__(self):
        with open(API_SETTINGS_FILE, 'r') as stream:
            try:
                api_settings = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self.url = api_settings['joke']['url']

    def get_api_response(self):
        """Get response object from the API"""
        return requests.get(self.url)

    @staticmethod
    def clean_api_response(resp):
        """Extract only the content from a response object"""
        return resp.content.decode('UTF-8')

    def get_random_joke(self):
        """Get a random fact from the API"""
        return json.loads(self.clean_api_response(self.get_api_response())).replace('quote', '').replace('&quot;', '')

    def get_random_chuck_norris_joke(self):
        """Get a random fact that is in english from the API"""
        joke = self.get_random_joke()
        while 'Chuck Norris' not in joke:
            joke = self.get_random_joke()
        return joke


if __name__ == '__main__':
    jokeClient = JokeClient()
    joke = jokeClient.get_random_chuck_norris_joke()
    print "tmp"
