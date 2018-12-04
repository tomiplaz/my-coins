from coinbase.wallet.client import Client
from functools import reduce
from decimal import Decimal
from tabulate import tabulate

TWO_PLACES = Decimal('0.01')

def print_reduced_buys(_my_data):
    api_key = _my_data.get('CB_API_KEY')
    api_secret = _my_data.get('CB_API_SECRET')

    table_data = []
    table_headers = ('Symbol', 'Buys Count', 'Total Amount', 'Total Cost', 'Coinbase Fee', 'Bank Fee', 'Avg. Unit Cost', 'Wt. Unit Cost')

    client = Client(api_key, api_secret)
    accounts = client.get_accounts().get('data')
    relevant_accounts = [account for account in accounts if account['currency'] in ('BTC', 'ETH', 'LTC')]

    for account in relevant_accounts:
        buys = client.get_buys(account.get('id')).get('data')
        relevant_buys = [buy for buy in buys if buy['total']['currency'] == 'EUR' and buy['status'] == 'completed']

        symbol = account.get('currency')
        buys_count = len(relevant_buys)

        total_amount = total_cost = total_cost_no_fee = coinbase_fee = bank_fee = 0
        for buy in relevant_buys:
            total_amount += Decimal(buy['amount']['amount'])
            total_cost += Decimal(buy['total']['amount'])
            total_cost_no_fee += Decimal(buy['subtotal']['amount'])
            coinbase_fee += Decimal([fee['amount']['amount'] for fee in buy['fees'] if fee['type'] == 'coinbase'].pop())
            bank_fee += Decimal([fee['amount']['amount'] for fee in buy['fees'] if fee['type'] == 'bank'].pop())

        avg_unit_cost = (total_cost - coinbase_fee - bank_fee) / total_amount
        wt_unit_cost = reduce(
            lambda x, y: x + y,
            [Decimal(buy['unit_price']['amount']) * Decimal(buy['subtotal']['amount']) / total_cost_no_fee for buy in relevant_buys]
        )

        table_data.append([
            symbol,
            buys_count,
            total_amount.quantize(TWO_PLACES),
            total_cost.quantize(TWO_PLACES),
            coinbase_fee.quantize(TWO_PLACES),
            bank_fee.quantize(TWO_PLACES),
            avg_unit_cost.quantize(TWO_PLACES),
            wt_unit_cost.quantize(TWO_PLACES),
        ])

    print('\n' + tabulate(table_data, table_headers, tablefmt='plain', floatfmt='.2f'))
