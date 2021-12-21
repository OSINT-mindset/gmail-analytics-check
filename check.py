#!/usr/bin/env python3
from hashlib import sha1
import json
import os
import re
import requests
import sys
import time


URL = 'https://analyticssuitefrontend-pa.clients6.google.com/v1/usermanagement/users?alt=json&key={}'

HEADERS = {
    'authority': 'analyticssuitefrontend-pa.clients6.google.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'x-goog-encode-response-if-executable': 'base64',
    'x-origin': 'https://analytics.google.com',
    'x-clientdetails': 'appVersion=5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F96.0.4664.110%20Safari%2F537.36&platform=MacIntel&userAgent=Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F96.0.4664.110%20Safari%2F537.36',
    'sec-ch-ua-mobile': '?0',
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    'x-javascript-user-agent': 'google-api-javascript-client/1.1.0',
    'x-goog-authuser': '0',
    'x-referer': 'https://analytics.google.com',
    'sec-ch-ua-platform': '"macOS"',
    'accept': '*/*',
    'origin': 'https://analyticssuitefrontend-pa.clients6.google.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'accept-language': 'en,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7',
    'x-client-data': 'CIi2yQEIorbJAQjEtskBCKmdygEI0aDKAQidicsBCOvyywEInvnLAQjX/MsBCOeEzAEItYXMAQjLicwBCISNzAEIrY7MAQjSj8wBCNqQzAEYjp7LAQ==',
}

COOKIES = {}
KEY_REGEXP = re.compile(r'gmsSuiteApiKey\\x22:\\x22(.+?)\\x22,\\x22')


def use_ghunt_cookies(filename):
    global HEADERS, COOKIES, URL

    if not os.path.exists(filename):
        print(f'There is not file {filename} with Google cookies! Download GHunt, make "check_and_gen" and copy resources/data.txt file to this path.')
        print('https://github.com/mxrch/GHunt/tree/master#usage')
        return False

    data = json.load(open(filename))
    HEADERS.update({'cookies': '; '.join([f'{k}={v}' for k,v in data['cookies'].items()])})
    COOKIES = data["cookies"]

    return True

def use_analytics_api_key():
    global URL
    r = requests.get('https://analytics.google.com/analytics/web/', cookies=COOKIES)
    key = KEY_REGEXP.search(r.text).groups()[0]
    URL = URL.format(key)


def use_analytics_auth():
    global HEADERS
    cur_time = str(int(time.time()))
    auth_hash = sha1(' '.join([cur_time, COOKIES['SAPISID'], 'https://analytics.google.com']).encode()).hexdigest()
    HEADERS.update({'authorization': f'SAPISIDHASH {cur_time}_{auth_hash}'})


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: ./check.py alex@telegram.org')
        sys.exit(1)

    if not use_ghunt_cookies('data.txt'):
        sys.exit(2)

    use_analytics_api_key()
    use_analytics_auth()

    email = sys.argv[1]

    r = requests.post(URL, headers=HEADERS, cookies=COOKIES, data=json.dumps({"email":[email]}))
    print(r.text)
