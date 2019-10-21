from decimal import Decimal
from functools import reduce
from tabulate import tabulate

TWO_PLACES = Decimal('0.01')
RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'

def get_buys_total_value(key, my_data):
    _history = my_data.get('history')
    return reduce(
        lambda x, y: x + y,
        [Decimal(trade[key]) for coin_trades in _history['buy'].values() for trade in coin_trades]
    )

def colorize(value):
    if isinstance(value, Decimal) and value != 0:
        return (RED if value < 0 else GREEN) + str(value) + ENDC
    return str(value)

def print_status(my_data, api_data):
    _coins = my_data.get('coins')
    _history = my_data.get('history')
    _fiat = my_data.get('fiat')
    _fiat_sum = Decimal('0')

    _total_price = get_buys_total_value('price', my_data)
    _total_fee = get_buys_total_value('fee', my_data)

    for _symbol in _coins.keys():
        _quote_price = api_data[_symbol]['quote'][_fiat]['price']
        _fiat_sum += Decimal(_coins[_symbol]) * Decimal(_quote_price)

    _diff = _fiat_sum - _total_price
    _diff_percent = _diff / _total_price * 100
    _table_data = [
        ['Investment (Fees)', _total_price.quantize(TWO_PLACES), _total_fee.quantize(TWO_PLACES)],
        ['Present Value', _fiat_sum.quantize(TWO_PLACES)],
        ['Difference (%)', colorize(_diff.quantize(TWO_PLACES)), colorize(_diff_percent.quantize(TWO_PLACES))],
    ]

    print('\n' + tabulate(_table_data, tablefmt='plain', floatfmt='.2f'))

def print_buys(my_data):
    _history = my_data.get('history')
    _table_data = []
    _table_headers = ('Symbol', 'Cost', 'Fee', 'Cost Per Unit')

    for _symbol, _trades in _history['buy'].items():
        _price_sum = reduce(lambda x, y: x + y, [Decimal(_trade['price']) for _trade in _trades])
        _fee_sum = reduce(lambda x, y: x + y, [Decimal(_trade['fee']) for _trade in _trades])
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

    _total_price = get_buys_total_value('price', my_data)
    _total_fee = get_buys_total_value('fee', my_data)
    _table_data.append([
        '',
        _total_price.quantize(TWO_PLACES),
        _total_fee.quantize(TWO_PLACES)
    ])

    print('\n' + tabulate(_table_data, _table_headers, tablefmt='plain', floatfmt='.2f'))

def print_coins(my_data, api_data):
    _coins = my_data.get('coins')
    _fiat = my_data.get('fiat')
    _table_data = []
    _table_headers = ('Symbol', 'Price', '1h%', '24h%', '7d%', '24h Volume')

    for _symbol in _coins.keys():
        _table_data.append([
            _symbol,
            _get_decimal_value(api_data[_symbol]['quote'][_fiat]['price']),
            colorize(_get_decimal_value(api_data[_symbol]['quote'][_fiat]['percent_change_1h'])),
            colorize(_get_decimal_value(api_data[_symbol]['quote'][_fiat]['percent_change_24h'])),
            colorize(_get_decimal_value(api_data[_symbol]['quote'][_fiat]['percent_change_7d'])),
            _get_decimal_value(api_data[_symbol]['quote'][_fiat]['volume_24h'])
        ])

    print('\n' + tabulate(_table_data, _table_headers, tablefmt='plain', floatfmt='.2f'))

def print_market(my_data, api_data):
    _fiat = my_data.get('fiat')

    _table_data = [
        ['Total Market Cap', Decimal(api_data['quote'][_fiat]['total_market_cap']).quantize(TWO_PLACES)],
        ['Total 24h Volume', Decimal(api_data['quote'][_fiat]['total_volume_24h']).quantize(TWO_PLACES)],
        ['BTC Dominance (%)', Decimal(api_data['btc_dominance']).quantize(TWO_PLACES)],
        ['ETH Dominance (%)', Decimal(api_data['eth_dominance']).quantize(TWO_PLACES)],
        #['Active Cryptocurrencies', api_data['active_cryptocurrencies']],
        #['Active Exchanges', api_data['active_exchanges']],
        #['Active Market Pairs', api_data['active_market_pairs']]
    ]

    print('\n' + tabulate(_table_data, tablefmt='plain', floatfmt='.2f'))

def _get_decimal_value(value):
    return '' if value is None else Decimal(value).quantize(TWO_PLACES)
