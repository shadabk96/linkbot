import os

from dotenv import load_dotenv


__DIR__ = os.path.dirname(__file__)
load_dotenv(dotenv_path=__DIR__ + '/.env')

if os.getenv('COFFEEBOT_DATABASE_URI') is not None:
    DATABASE_URI = os.getenv('COFFEEBOT_DATABASE_URI')
else:
    DATABASE_URI = 'sqlite:////' + __DIR__ + os.getenv('COFFEEBOT_DATABASE_FILENAME')
