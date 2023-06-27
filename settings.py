from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

BOT_TOKEN = ''

engine = create_engine('mysql+pymysql://root:@localhost/qi_bot')
engine.connect()

base = declarative_base()
session = Session(bind=engine)

ACTIVE_PAYMENTS = {}

CRYSTAL_PAY_TOKEN_1 = 'c2cfa3959b56d4fce2df326d4012219c17874894'
CRYSTAL_PAY_TOKEN_2 = '40c8d9df90c68921a17feebaca094b6e68690baf'

CRYPTO_BOT_TOKEN = ''

ADMIN_ID = 1460245641