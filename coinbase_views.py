from coinbase.wallet.client import Client
from functools import reduce
from decimal import Decimal

TWO_PLACES = Decimal('0.01')

def print_reduced_buys(_my_data):
    api_key = _my_data.get('CB_API_KEY')
    api_secret = _my_data.get('CB_API_SECRET')

    client = Client(api_key, api_secret)
    accounts = client.get_accounts().get('data')
    relevant_accounts = [account for account in accounts if account['currency'] in ('BTC', 'ETH', 'LTC')]

    for account in relevant_accounts:
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
        """ fee = reduce(
            lambda x, y: x + y,
            [Decimal(buy['fee']['amount']) for buy in buys]
        ) """

        print('\t'.join([
            account.get('currency'),
            str(len(relevant_buys)),
            str(amount.quantize(TWO_PLACES)),
            str(total.quantize(TWO_PLACES)),
            #fee.quantize(TWO_PLACES),
        ]))
