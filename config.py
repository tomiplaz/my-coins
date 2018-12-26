from os import path
from json import loads
from constants import NAME

cmc_api_key = 'cmc_api_key'
cb_api_key = 'cb_api_key'
cb_api_secret = 'cb_api_secret'
fiat = 'fiat'

class MissingConfigValue(Exception):
    def __init__(self, key):
        self.key = key

class Config:
    required_keys = (
        cmc_api_key,
        cb_api_key,
        cb_api_secret,
        fiat,
    )

    def __init__(self):
        dir_path = path.dirname(path.realpath(__file__))

        try:
            with open(dir_path + '/config2.json') as file:
                deserialized_json = loads(file.read())

                for key in self.required_keys:
                    setattr(self, key, deserialized_json.get(key))

                    if not getattr(self, key):
                        raise MissingConfigValue(key)
        except IOError as e:
            print(
                'Error reading config.json',
                'Make sure config.json is defined in project\'s root directory',
                sep='\n'
            )
            exit()
        except MissingConfigValue as e:
            print(
                'Missing {0} value in config.json'.format(e.key),
                'Make sure {0} is defined in config.json'.format(e.key),
                sep='\n'
            )
            exit()
