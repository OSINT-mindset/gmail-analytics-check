import asyncio
from hashlib import sha1
import json
import os
import re
import ssl
import sys
import time
from typing import List, Any

from aiohttp import TCPConnector, ClientSession
from bs4 import BeautifulSoup as bs

from .executor import AsyncioProgressbarQueueExecutor, AsyncioSimpleExecutor


def create_ssl_context(proto=ssl.PROTOCOL_SSLv23, 
                                   verify_mode=ssl.CERT_NONE,
                                   protocols=None,
                                   options=None,
                                   ciphers="ALL"):
                protocols = protocols or ('PROTOCOL_SSLv3','PROTOCOL_TLSv1',
                                          'PROTOCOL_TLSv1_1','PROTOCOL_TLSv1_2')
                options = options or ('OP_CIPHER_SERVER_PREFERENCE','OP_SINGLE_DH_USE',
                                      'OP_SINGLE_ECDH_USE','OP_NO_COMPRESSION')
                context = ssl.SSLContext(proto)
                context.verify_mode = verify_mode
                # reset protocol, options
                # context.protocol = 0
                context.options = 0
                # for p in protocols:
                    # context.protocol |= getattr(ssl, p, 0)
                for o in options:
                    context.options |= getattr(ssl, o, 0)
                context.set_ciphers(ciphers)
                return context 


class InputData:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class OutputData:
    def __init__(self, gaia_id, canonical_email, error):
        self.gaia_id = gaia_id
        self.canonical_email = canonical_email
        self.error = error

    @property
    def fields(self):
        fields = list(self.__dict__.keys())
        fields.remove('error')

        return fields

    def __str__(self):
        error = ''
        if self.error:
            error = f' (error: {str(self.error)}'

        result = ''

        for field in self.fields:
            field_pretty_name = field.title().replace('_', ' ')
            value = self.__dict__.get(field)
            if value:
                result += f'{field_pretty_name}: {str(value)}\n'

        result += f'{error}'
        return result


class OutputDataList:
    def __init__(self, input_data: InputData, results: List[OutputData]):
        self.input_data = input_data
        self.results = results

    def __repr__(self):
        return f'Target {self.input_data}:\n' + '--------\n'.join(map(str, self.results))


class Processor:
    URL = 'https://analyticssuitefrontend-pa.clients6.google.com/v1/usermanagement/users?alt=json&key={}'
    HEADERS_WEB = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',    
        'accept-language': 'en,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'x-referer': 'https://analytics.google.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile': '?0',
    }
    HEADERS = {
        # 'authority': 'analyticssuitefrontend-pa.clients6.google.com',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'pragma': 'no-cache',
        'accept-encoding': 'gzip, deflate',
        'accept': '*/*',
        'cache-control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'x-goog-encode-response-if-executable': 'base64',
        'x-origin': 'https://analytics.google.com',
        'x-clientdetails': 'appVersion=5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F96.0.4664.110%20Safari%2F537.36&platform=MacIntel&userAgent=Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F96.0.4664.110%20Safari%2F537.36',
        'sec-ch-ua-mobile': '?0',
        'content-type': 'application/json',
        'x-requested-with': 'XMLHttpRequest',
        'x-javascript-user-agent': 'google-api-javascript-client/1.1.0',
        'x-goog-authuser': '0',
        'x-referer': 'https://analytics.google.com',
        'sec-ch-ua-platform': '"macOS"',
        'origin': 'https://analyticssuitefrontend-pa.clients6.google.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7',
        'x-client-data': 'CIi2yQEIorbJAQjEtskBCKmdygEI0aDKAQidicsBCOvyywEInvnLAQjX/MsBCOeEzAEItYXMAQjLicwBCISNzAEIrY7MAQjSj8wBCNqQzAEYjp7LAQ==',
    }
    COOKIES = {}
    KEY_REGEXP = re.compile(r'gmsSuiteApiKey\\x22:\\x22(.+?)\\x22,\\x22')

    def __init__(self, *args, **kwargs):
        from aiohttp_socks import ProxyConnector

        # make http client session
        proxy = kwargs.get('proxy')
        self.proxy = proxy
        if proxy:
            connector = ProxyConnector.from_url(proxy, ssl=False)
        else:
            connector = TCPConnector(ssl=False)
        # connector = TCPConnector(
        #     ssl_context=create_ssl_context(),
        #     use_dns_cache=True,
        # )
        self.session = ClientSession(
            connector=connector, trust_env=False
        )
        if kwargs.get('no_progressbar'):
            self.executor = AsyncioSimpleExecutor()
        else:
            self.executor = AsyncioProgressbarQueueExecutor()

    def use_ghunt_cookies(self, filename):
        if not os.path.exists(filename):
            print(f'There is not file {filename} with Google cookies! Download GHunt, make "check_and_gen" and copy resources/data.txt file to this path.')
            print('https://github.com/mxrch/GHunt/tree/master#usage')
            return False

        data = json.load(open(filename))
        self.HEADERS.update({'cookie': '; '.join([k+'='+v.strip('"') for k,v in data['cookies'].items()])})
        self.COOKIES = data["cookies"]

        return True

    async def use_analytics_api_key(self):
        r = await self.session.get('https://analytics.google.com/analytics/web/', headers=self.HEADERS_WEB, cookies=self.COOKIES)
        text = await r.text()
        key = self.KEY_REGEXP.search(text).groups()[0]
        self.URL = self.URL.format(key.strip('"'))

    def use_analytics_auth(self):
        cur_time = str(int(time.time()))
        auth_hash = sha1(' '.join([cur_time, self.COOKIES['SAPISID'], 'https://analytics.google.com']).encode()).hexdigest()
        self.HEADERS.update({'authorization': f'SAPISIDHASH {cur_time}_{auth_hash}'})

    async def close(self):
        await self.session.close()

    async def request(self, input_data: InputData) -> OutputDataList:
        result = None
        error = None
        output_data = []

        # gmail setup
        res = self.use_ghunt_cookies('data.txt')
        await self.use_analytics_api_key()
        self.use_analytics_auth()

        try:
            email = input_data.value
            data = json.dumps({"email":[email]})
            r = await self.session.post(self.URL, headers=self.HEADERS, data=data)
            result = await r.json()

            for user_data in result.get('principal', []):
                gaia_id = user_data['user']['gaiaId']
                canonical_email = user_data['user']['email']
                output_data.append(OutputData(gaia_id, canonical_email, error))

            if 'error' in result:
                print(error)
                # TODO: proper errors processing
                # output_data.append(OutputData('', '', result['error']['message']))

        except Exception as e:
            error = e

        results = OutputDataList(input_data, output_data)

        return results


    async def process(self, input_data: List[InputData]) -> List[OutputDataList]:
        tasks = [
            (
                self.request, # func
                [i],          # args
                {}            # kwargs
            )
            for i in input_data
        ]

        results = await self.executor.run(tasks)

        return results
