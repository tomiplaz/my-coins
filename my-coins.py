import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from json import loads as jsonloads
from constants import (BASE_URL, NAME, ALL, STATUS, BUYS, COINS, MARKET)
from views import (print_status, print_buys, print_coins, print_market)

def _get_api_data(url):
    _headers = {
        'X-CMC_PRO_API_KEY': _my_data.get('CMC_API_KEY'),
        'Accept': 'application/json'
    }
    _request = Request(url=url, headers=_headers)
    _response = urlopen(_request)
    return jsonloads(_response.read()).get('data')

_dir_path = os.path.dirname(os.path.realpath(__file__))
_argv1 = sys.argv[1] if len(sys.argv) > 1 else None

with open(_dir_path + '/' + NAME + '.json') as _file:
    _my_data = jsonloads(_file.read())
_coins = _my_data.get('coins')
_fiat = _my_data.get('fiat')

_query_params = {'symbol': ','.join(_coins.keys()), 'convert': _fiat}
_query_string = '?' + '&'.join([_k + '=' + _v for _k, _v in _query_params.items()])
_url =  BASE_URL + '/v1/cryptocurrency/quotes/latest' + _query_string
_api_data = _get_api_data(_url)

print(NAME, _fiat)

if _argv1 in (ALL, MARKET):
    _market_query_string = '?convert=' + _fiat
    _market_api_url = BASE_URL + '/v1/global-metrics/quotes/latest?convert=' + _fiat
    _market_api_data = _get_api_data(_market_api_url)
    print_market(_my_data, _market_api_data)

if not _argv1 or _argv1 in (ALL, STATUS):
    print_status(_my_data, _api_data)

if _argv1 in (ALL, BUYS):
    print_buys(_my_data)

if _argv1 in (ALL, COINS):
    print_coins(_my_data, _api_data)
