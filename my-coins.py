from environment import Environment
from coinbase_handler import CoinbaseHandler

environment = Environment()
coinbaseHandler = CoinbaseHandler(
    api_key=environment.cb_api_key,
    api_secret=environment.cb_api_secret,
)
