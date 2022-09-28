import json

import requests


def get_swagger(url):
    resp = requests.request("GET", url).text
    respJson = json.loads(resp)
