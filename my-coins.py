import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from functools import reduce
from json import loads as jsonloads
from decimal import Decimal
from functools import reduce
from tabulate import tabulate

NAME = 'my-coins'
TWO_PLACES = Decimal('0.01')
FOUR_PLACES = Decimal('0.0001')
ALL = 'all'
COINS = 'coins'
STATUS = 'status'
BUY_HISTORY = 'buy_history'
_argv1 = sys.argv[1] if len(sys.argv) > 1 else None

with open(NAME + '.json') as _file:
    _input = jsonloads(_file.read())
_coins = _input.get('coins')
_history = _input.get('history')
_fiat = _input.get('fiat')
print(NAME, _fiat)

_query_params = {'symbol': ','.join(_coins.keys()), 'convert': _fiat}
_query_string = '?' + '&'.join([_k + '=' + _v for _k, _v in _query_params.items()])
_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest' + _query_string
_headers = {
    'X-CMC_PRO_API_KEY': _input.get('CMC_API_KEY'),
    'Accept': 'application/json'
}
_request = Request(url=_url, headers=_headers)
_response = urlopen(_request)
_api_data = jsonloads(_response.read()).get('data')

_total_price = Decimal('0')
_total_fee = Decimal('0')
_table_data = []
_table_headers = ('Coin', 'Price', 'Fee', 'Avg. Unit')
for _symbol, _trades in _history['buy'].items():
    _price_sum = reduce(
        lambda x, y: x + y,
        [Decimal(_trade['price']) for _trade in _trades]
    )
    _total_price += _price_sum
    _fee_sum = reduce(
        lambda x, y: x + y,
        [Decimal(_trade['fee']) for _trade in _trades]
    )
    _total_fee += _fee_sum
    _net_price = _price_sum - _fee_sum
    _average_unit_value = reduce(
        lambda x, y: x + y,
        [Decimal(_trade['unit_value']) * Decimal(_trade['price']) / _net_price for _trade in _trades]
    )
    _table_data.append([
        _symbol,
        _price_sum.quantize(TWO_PLACES),
        _fee_sum.quantize(TWO_PLACES),
        _average_unit_value.quantize(TWO_PLACES)
    ])
_table_data.append([
    '',
    _total_price.quantize(TWO_PLACES),
    _total_fee.quantize(TWO_PLACES)
])

if _argv1 in (ALL, BUY_HISTORY):
    print('\n' + tabulate(_table_data, _table_headers, tablefmt='plain', floatfmt='.2f'))

_fiat_sum = Decimal('0')
for _symbol in _coins.keys():
    _quote_price = _api_data[_symbol]['quote'][_fiat]['price']
    _fiat_sum += Decimal(_coins[_symbol]) * Decimal(_quote_price)
_diff = _fiat_sum - _total_price
_diff_percent = _diff / _total_price * 100
_table_data = [
    ['Value', _fiat_sum.quantize(TWO_PLACES)],
    ['Diff', _diff.quantize(TWO_PLACES)],
    ['Diff %', _diff_percent.quantize(TWO_PLACES)]
]

if not _argv1 or _argv1 in (ALL, STATUS):
    print('\n' + tabulate(_table_data, tablefmt='plain', floatfmt='.2f'))

_table_data = []
_table_headers = ('Symbol', 'Price', '1h%', '24h%', '7d%', '24h Volume')
for _symbol in _coins.keys():
    _quote_price = _api_data[_symbol]['quote'][_fiat]['price']
    _fiat_sum += Decimal(_coins[_symbol]) * Decimal(_quote_price)
    _table_data.append([
        _symbol,
        Decimal(_api_data[_symbol]['quote'][_fiat]['price']).quantize(FOUR_PLACES),
        Decimal(_api_data[_symbol]['quote'][_fiat]['percent_change_1h']).quantize(TWO_PLACES),
        Decimal(_api_data[_symbol]['quote'][_fiat]['percent_change_24h']).quantize(TWO_PLACES),
        Decimal(_api_data[_symbol]['quote'][_fiat]['percent_change_7d']).quantize(TWO_PLACES),
        Decimal(_api_data[_symbol]['quote'][_fiat]['volume_24h']).quantize(TWO_PLACES)
    ])

if _argv1 in (ALL, COINS):
    print('\n' + tabulate(_table_data, _table_headers, tablefmt='plain', floatfmt='.2f'))
