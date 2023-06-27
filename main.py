from bot import make_bot
from aiogram.utils import executor

if __name__ == '__main__':
    executor.start_polling(make_bot())
