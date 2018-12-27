from coinbase.wallet.client import Client

class CoinbaseHandler:
    def __init__(self, api_key, api_secret):
        client = Client(api_key, api_secret)
