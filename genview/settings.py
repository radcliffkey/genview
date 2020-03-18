from starlette.config import Config
from starlette.datastructures import URL, Secret

config = Config(".env")

DEBUG = config('DEBUG', cast=bool, default=False)

GV_PORT = config('GV_PORT', cast=int, default=8000)

GEN_USER = config('GEN_USER', cast=Secret)
GEN_PASSWD = config('GEN_PASSWD', cast=Secret)

GEN_URL = config('GEN_URL', cast=URL, default='https://generator.geneea.com')
