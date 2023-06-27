from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, InputFile



class Buttons():
    @staticmethod
    def get_start_btn():
        btn1 = KeyboardButton('💻Мой профиль')
        btn2 = KeyboardButton('💰Пополнить баланс')
        btn3 = KeyboardButton('🛒Покупка')
        btn4 = KeyboardButton('📦Предзаказ')
        btn5 = KeyboardButton('🗣Отзывы')
        btn6 = KeyboardButton('📋Правила')
        btn7 = KeyboardButton('🚑Замена/поддержка')

        return ReplyKeyboardMarkup().row(btn1, btn2).row(btn3, btn4).row(btn5, btn6).add(btn7)

    @staticmethod
    def get_profile_btn():
        pass