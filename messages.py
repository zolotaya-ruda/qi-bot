from aiogram.types import InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton


class Messages:
    @staticmethod
    def get_start_message():
        msg = '''Приветствую!

Здесь вы сможете приобрести аккаунты eBay-Kleinanzeigen

Отзывы - @qiklein
Связь - @modestqi'''

        btn1 = KeyboardButton('💻Мой профиль')
        btn2 = KeyboardButton('💰Пополнить баланс')
        btn3 = KeyboardButton('🛒Покупка')
        btn4 = KeyboardButton('📦Предзаказ')
        btn5 = KeyboardButton('🗣Отзывы')
        btn6 = KeyboardButton('📋Правила')
        btn7 = KeyboardButton('🚑Замена/поддержка')

        return msg, ReplyKeyboardMarkup().row(btn1, btn2).row(btn3, btn4).row(btn5, btn6).add(btn7)

    @staticmethod
    def get_profile_message(deposit):
        msg = f'''💬Ваш ChatID: 1460245641
👤Ваш логин: @idkhoooow
💰Ваш баланс: {deposit} USD'''

        return msg, InlineKeyboardMarkup().add(InlineKeyboardButton('Пополнить баланс', callback_data='deposit'))

    @staticmethod
    def get_payments_message():
        msg = 'Выберите способ пополнения'

        return msg, InlineKeyboardMarkup().add(InlineKeyboardButton('Crystal Pay', callback_data='crystal-pay')) \
            .add(InlineKeyboardButton('CryptoBot', callback_data='crypto-bot'))

    @staticmethod
    def get_payment_message1(payment_url, amount):
        msg = f'''CrystalPay ополнение

Сумма к оплате: {amount} USD
⚠️Платеж будет засчитан автоматически.'''

        return msg, InlineKeyboardMarkup().add(InlineKeyboardButton("💳Оплатить", url=payment_url))

    @staticmethod
    def get_crypto_btns():
        return InlineKeyboardMarkup().add(InlineKeyboardButton('BTC', callback_data='BTC'),
                                          InlineKeyboardButton('TON', callback_data='TON'),
                                          InlineKeyboardButton('ETH', callback_data='ETH'),
                                          InlineKeyboardButton('USDT', callback_data='USDT'),
                                          InlineKeyboardButton('USDC', callback_data='USDC'),
                                          InlineKeyboardButton('BUSD', callback_data='BUSD'))

    @staticmethod
    def get_payment_crypto_bot_message(coin, amount, payment_url):
        msg = f'''CryptoBot пополнение
        
Сумма к оплате: {amount} {coin}
⚠️Платеж будет засчитан автоматически.
        '''

        return msg, InlineKeyboardMarkup().add(InlineKeyboardButton("💳Оплатить", url=payment_url))

    @staticmethod
    def get_admin_message():
        msg = 'Вы находитесь в админ-панеле'

        return msg, ReplyKeyboardMarkup().row(KeyboardButton('Пользователи', callback_data='users')).row(
            KeyboardButton('Товар', callback_data='product')).row(
            KeyboardButton('Статистика', callback_data='statistic')).row(
            KeyboardButton('Отменить')
        )

    @staticmethod
    def get_user_messages():
        msg = 'Пользователи'
        return msg, InlineKeyboardMarkup().add(InlineKeyboardButton('Рассылка', callback_data='mailing'),
                                               InlineKeyboardButton('Найти', callback_data='find'))

    @staticmethod
    def get_find_user_message():
        msg = 'Введите username пользователя'
        return msg

    @staticmethod
    def get_info_user_message(username, _id, current_deposit, all_deposits):
        msg = f'''@{username}
id: {_id}
текущий баланс: {current_deposit}
баланс за все время: {all_deposits}'''

        return msg, InlineKeyboardMarkup().add(
            InlineKeyboardButton('Изменить баланс', callback_data=f'change_balance:{_id}'),
            InlineKeyboardButton('Заблокировать', callback_data='ban'))

    @staticmethod
    def get_categories_message():
        msg = 'Настройки категорий'

        return msg, InlineKeyboardMarkup().add(
            InlineKeyboardButton('Просмотреть все категории', callback_data='all_categories'),
            InlineKeyboardButton('Добавить категорию', callback_data='add_category'))

    @staticmethod
    def get_all_categories(categories):
        markup = InlineKeyboardMarkup()
        msg = 'Все категории'
        for category in categories:
            markup.add(InlineKeyboardButton(category.name, callback_data=f'category_id:{category.id}'))

        return msg, markup

    @staticmethod
    def get_category_settings(category_name, products, category_id):
        msg = f'Выбрана категория: {category_name}'
        markup = InlineKeyboardMarkup()

        for product in products:
            markup.add(InlineKeyboardButton(product.name, callback_data=f'product_get:{product.id}'))

        return msg, markup.add(
            InlineKeyboardButton('Добавить товар', callback_data=f'new_product:{category_id}'),
            InlineKeyboardButton('Удалить категорию', callback_data=f'category_delete:{category_id}'))

    @staticmethod
    def get_product_info(product):
        msg = f'''{product.quantity}шт.-{product.name}-{product.cost}$'''
        return msg, InlineKeyboardMarkup().add(
            InlineKeyboardButton('Удалить', callback_data=f'product_delete:{product.id}'))

    @staticmethod
    def get_buy_message(categories):
        markup = InlineKeyboardMarkup()
        msg = 'Выберите категорию'
        for category in categories:
            markup.add(InlineKeyboardButton(category.name, callback_data=f'buy_category_id:{category.id}'))

        return msg, markup

    @staticmethod
    def get_product_message(products):
        msg = f'''Выберите товар'''
        markup = InlineKeyboardMarkup()

        for product in products:
            markup.add(InlineKeyboardButton(f"{product.quantity}шт.-{product.name}-{product.cost}$",
                                            callback_data=f"buy_product:{product.id}"))

        markup.add(InlineKeyboardButton('Назад', callback_data='buy_paginate:0'))

        return msg, markup

    @staticmethod
    def get_buy_all_categories(categories):
        markup = InlineKeyboardMarkup()
        msg = 'Выберите категорию'
        for category in categories:
            markup.add(InlineKeyboardButton(category.name, callback_data=f'buy_category_id:{category.id}'))

        return msg, markup

    @staticmethod
    def get_product_info1(product, category):
        msg = f'''Категория: {category.name}
Товар: {product.name}
Количество: {product.quantity}
Цена: {product.cost} USD

Введите желаемое количество'''
        return msg

    @staticmethod
    def get_statistic_message(statistic):
        msg = f'''Продано аккаунтов за все время: {statistic.sold_accounts}
Общая сумма депозитов: {statistic.deposits}'''
        return msg
