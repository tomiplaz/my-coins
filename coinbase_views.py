from coinbase.wallet.client import Client
from functools import reduce
from decimal import Decimal
from tabulate import tabulate

TWO_PLACES = Decimal('0.01')

def print_reduced_buys(_my_data):
    api_key = _my_data.get('CB_API_KEY')
    api_secret = _my_data.get('CB_API_SECRET')

    table_data = []
    table_headers = ('Symbol', 'Buys Count', 'Total Amount', 'Total Cost', 'Coinbase Fee', 'Bank Fee', 'Cost Per Unit')

    client = Client(api_key, api_secret)
    accounts = client.get_accounts().get('data')
    relevant_accounts = [account for account in accounts if account['currency'] in ('BTC', 'ETH', 'LTC')]

    for account in relevant_accounts:
        per_unit = 0
        buys = client.get_buys(account.get('id')).get('data')
        relevant_buys = [buy for buy in buys if buy['total']['currency'] == 'EUR' and buy['status'] == 'completed']

        amount = reduce(
            lambda x, y: x + y,
            [Decimal(buy['amount']['amount']) for buy in relevant_buys]
        )
        total = reduce(
            lambda x, y: x + y,
            [Decimal(buy['total']['amount']) for buy in relevant_buys]
        )
        fees = [fee for buy_fees in [buy['fees'] for buy in relevant_buys] for fee in buy_fees]
        coinbase_fee = reduce(
            lambda x, y: x + y,
            [Decimal(fee['amount']['amount']) for fee in fees if fee['type'] == 'coinbase']
        )
        bank_fee = reduce(
            lambda x, y: x + y,
            [Decimal(fee['amount']['amount']) for fee in fees if fee['type'] == 'bank']
        )
        per_unit = (total - coinbase_fee - bank_fee) / amount

        table_data.append([
            account.get('currency'),
            len(relevant_buys),
            amount.quantize(TWO_PLACES),
            total.quantize(TWO_PLACES),
            coinbase_fee.quantize(TWO_PLACES),
            bank_fee.quantize(TWO_PLACES),
            per_unit.quantize(TWO_PLACES),
        ])

    print('\n' + tabulate(table_data, table_headers, tablefmt='plain', floatfmt='.2f'))
