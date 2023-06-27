import threading
import time

import requests
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext

import settings
from messages import Messages
from sql_module import User, Category, Product, ProductData, Statistic
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states import CreateInvoice, FindUser, BeginMailing, NewProduct, BuyProduct, ChangeBalance, CreateCategory
from payments import CrystalPay, CryptoBot
from settings import BOT_TOKEN
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pagination import Pagination

bot = Bot(token='5473936156:AAElTjeR8ydJrPK57_eOF1dDEs1I9aqiBbg')
dp = Dispatcher(bot, storage=MemoryStorage())

messages = Messages()


def check_payments(user_id, payment_id, amount, pay_system):
    if pay_system == 'crystal-pay':
        while True:
            if CrystalPay.check_invoice(payment_id) is True:
                requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                             json={'chat_id': user_id, 'text': 'Деньги были успешно зачислены на ваш счет'})
                user = User.get_by_tg_id(user_id)[0]
                user.current_deposit += int(amount)
                user.all_deposit += int(amount)
                user.create()
                s = Statistic.get()
                s.deposits += int(amount)
                s.create()
                break
            time.sleep(1)

    elif pay_system == 'crypto-bot':
        while True:
            if CryptoBot.check_invoice(payment_id) is True:
                requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                             json={'chat_id': user_id, 'text': 'Деньги были успешно зачислены на ваш счет'})
                user = User.get_by_tg_id(user_id)[0]
                user.current_deposit += int(amount)
                user.all_deposit += int(amount)
                user.create()
                s = Statistic.get()
                s.deposits += int(amount)
                s.create()
                break
            time.sleep(1)


class States:
    @staticmethod
    @dp.message_handler(state=CreateInvoice.amount)
    async def set_amount(message: types.Message, state: FSMContext):
        amount = message.text

        if dp.data[message.from_user.id]['pay-system'] == 'crystal-pay':
            response = CrystalPay.create_invoice(amount)
            msg, btns = messages.get_payment_message1(response['url'], amount)
            await message.answer(msg, reply_markup=btns)
            await state.finish()
            t = threading.Thread(target=check_payments,
                                 args=(message.from_user.id, response['id'], amount, 'crystal-pay'))
            t.start()
            dp.data[message.from_user.id].pop('pay-system')

        elif dp.data[message.from_user.id]['pay-system'] == 'crypto-bot':
            coin = dp.data[message.from_user.id]['coin']
            r = CryptoBot.get_exchange_rates()
            rate = list(filter(lambda x: x['source'] == coin and x['target'] == 'USD', r.json()['result']))[0]
            rub_amount = float(amount) / float(rate['rate'])
            response = CryptoBot.create_invoice(rub_amount, coin).json()

            msg, btns = messages.get_payment_crypto_bot_message(coin, response['result']['amount'],
                                                                response['result']['pay_url'])

            await message.answer(msg, reply_markup=btns)
            await state.finish()

            t = threading.Thread(target=check_payments, args=(
                message.from_user.id, response['result']['invoice_id'], amount,
                dp.data[message.from_user.id]['pay-system']))

            t.start()
            dp.data.pop(message.from_user.id)

    @staticmethod
    @dp.message_handler(state=FindUser.username)
    async def find_user(message: types.Message, state: FSMContext):
        user = User.get_by_username(message.text)

        await state.finish()

        if len(user) == 0:
            return await message.answer('Пользователь с заданным именем не найден')

        user = user[0]

        msg, btns = messages.get_info_user_message(user.username, user.tg_id, user.current_deposit, user.all_deposit)

        await message.answer(msg, reply_markup=btns)

    @staticmethod
    @dp.message_handler(state=BeginMailing.mail_text)
    async def begin_mailing(message: types.Message, state: FSMContext):
        mail_text = message.text
        await state.finish()

        for user in User.all():
            await bot.send_message(user.tg_id, mail_text)

        await message.answer('Рассылка успешно завершена')

    @staticmethod
    @dp.message_handler(state=NewProduct.name)
    async def get_product_name(message: types.Message, state: FSMContext):
        if message.text == 'Отменить':
            return await state.finish()
        await state.update_data(name=message.text)
        await NewProduct.next()
        await message.answer('Введите стоимость:')

    @staticmethod
    @dp.message_handler(state=NewProduct.cost)
    async def get_product_cost(message: types.Message, state: FSMContext):
        if message.text == 'Отменить':
            await state.finish()
        await state.update_data(cost=message.text)
        await NewProduct.next()
        await message.answer('Вставьте файл с аккаунтами:')

    @staticmethod
    @dp.message_handler(state=NewProduct.file, content_types=types.ContentType.DOCUMENT)
    async def get_product_cost(message: types.Message, state: FSMContext):
        if message.text == 'Отменить':
            await state.finish()
        await message.document.download(destination_file='accounts.txt')
        data = await state.get_data()
        lines = list(filter(lambda x: x != '', open('accounts.txt').read().split('\n')))

        product = Product(name=data['name'], cost=data['cost'], category_id=dp.data['category_id'],
                          quantity=len(lines)).create()

        for line in lines:
            ProductData(data=line, product_id=product.id).create()

        await state.finish()
        await message.answer('Аккаунты были успешном загружены')

    @staticmethod
    @dp.message_handler(state=BuyProduct.quantity)
    async def get_quantity(message: types.Message, state: FSMContext):
        quantity = int(message.text)

        if quantity < 0:
            return await message.answer(f'Невенрый формат!')

        product = dp.data[f'{message.from_user.id}_buy']

        if quantity > int(product.quantity):
            return await message.answer(f'В наличии имеется только {product.quantity} шт!')

        amount = quantity * int(product.cost)
        user = User.get_by_tg_id(message.from_user.id)[0]

        if amount > user.current_deposit:
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton('💰Пополнить', callback_data='deposit'))
            await state.finish()
            return await message.answer('Недостаточно средств на балансе', reply_markup=markup)

        user.current_deposit -= amount
        user.create()

        product_data = ProductData.get_by_product_id(product.id)[:quantity]
        user_file = open(f'users_purchases/{message.from_user.id}.txt', 'wb')

        for data in product_data:
            user_file.write(bytes(data.data + '\n', 'utf-8'))

        user_file.close()

        for _ in product_data:
            settings.session.delete(_)
            settings.session.commit()

        product.quantity -= quantity
        product.create()

        statistic = Statistic.get()
        statistic.sold_accounts += quantity
        statistic.create()

        await message.answer_document(open(f'users_purchases/{message.from_user.id}.txt', "rb"))
        await state.finish()

    @staticmethod
    @dp.message_handler(state=ChangeBalance.amount)
    async def change_balance(message: types.Message, state: FSMContext):
        amount = int(message.text)
        user = dp.data['user_change_balance'][0]
        user.current_deposit = amount
        user.create()

        await message.answer('Вы успешно сменили баланс!')
        await state.finish()

    @staticmethod
    @dp.message_handler(state=CreateCategory.name)
    async def create_category(message: types.Message, state: FSMContext):
        name = message.text
        category = Category(name=name)
        category.create()

        await state.finish()
        await message.answer('Категория успешно создана!')


'''
======================================================================================================================
'''


class QiBot:
    def __init__(self):
        self.commands = {
            '💻Мой профиль': self.profile,
            '💰Пополнить баланс': self.deposit,
            '🛒Покупка': self.buy,
            'Пользователи': self.users,
            'Товар': self.product,
            'Статистика': self.statistic
        }

    @staticmethod
    async def users(message: types.Message):
        if message.from_user.id == settings.ADMIN_ID:
            msg, btns = messages.get_user_messages()
            await bot.send_message(message.from_user.id, msg, reply_markup=btns)

    @staticmethod
    async def product(message: types.Message):
        if message.from_user.id == settings.ADMIN_ID:
            msg, btns = messages.get_categories_message()
            await bot.send_message(message.from_user.id, msg, reply_markup=btns)

    @staticmethod
    async def statistic(message: types.Message):
        if message.from_user.id == settings.ADMIN_ID:
            msg = messages.get_statistic_message(Statistic.get())
            await bot.send_message(message.from_user.id, msg)

    @staticmethod
    async def buy(message: types.Message):
        categories = Category.all()
        p = Pagination(categories, 5)
        paginated_data = p.get_paginated()
        msg, btns = messages.get_buy_message(categories[paginated_data[0]['begin']:paginated_data[0]['over']])
        if p.has_next(0):
            btns.add(InlineKeyboardButton('->', callback_data='buy_paginate:1'))
        await message.answer(msg, reply_markup=btns)

    @staticmethod
    @dp.message_handler(commands=['start'])
    async def start(message: types.Message):
        User().create_or_pass(message.from_user.id, message.from_user.username)
        msg, btns = messages.get_start_message()
        await bot.send_photo(chat_id=message.chat.id, caption=msg, photo=types.input_file.InputFile('start.jpg'),
                             reply_markup=btns)

    @staticmethod
    @dp.message_handler(commands=['admin'])
    async def admin(message: types.Message):
        if message.from_user.id == settings.ADMIN_ID:
            msg, btns = messages.get_admin_message()
            await message.answer(msg, reply_markup=btns)

    @staticmethod
    async def profile(message: types.Message):
        user = User.get_by_tg_id(message.from_user.id)[0]
        msg, btns = messages.get_profile_message(user.current_deposit)
        await message.answer(msg, reply_markup=btns)

    @staticmethod
    async def deposit(message: types.Message):
        msg, btns = messages.get_payments_message()
        await bot.send_message(message.from_user.id, msg, reply_markup=btns)


'''
======================================================================================================================
'''


class CallbackHandlers:
    def __init__(self):
        self.callbacks = {
            'deposit': self.handle_callback,
            'crystal-pay': self.deposit_with_crystal,
            'crypto-bot': self.deposit_with_crypto,
            'BTC': self.set_coin,
            'TON': self.set_coin,
            'ETH': self.set_coin,
            'USDT': self.set_coin,
            'USDC': self.set_coin,
            'BUSD': self.set_coin,
            'users': self.users_admin,
            'find': self.find_user,
            'mailing': self.mailing,
            'product': self.get_categories,
            'all_categories': self.products,
            'add_category': self.create_category,
            'statistic': self.get_statistic
        }

    @staticmethod
    async def get_statistic(callback: types.CallbackQuery):
        msg = messages.get_statistic_message(Statistic.get())
        await bot.send_message(callback.from_user.id, msg)

    @staticmethod
    async def create_category(callback: types.CallbackQuery):
        await CreateCategory.name.set()
        await bot.send_message(callback.from_user.id, 'Введите имя категории:')

    @staticmethod
    async def get_categories(callback: types.CallbackQuery):
        msg, btns = messages.get_categories_message()
        await bot.send_message(callback.from_user.id, msg, reply_markup=btns)

    @staticmethod
    async def products(callback: types.CallbackQuery):
        categories = Category.all()
        p = Pagination(categories, 5)
        paginated_data = p.get_paginated()
        msg, btns = messages.get_all_categories(categories[paginated_data[0]['begin']:paginated_data[0]['over']])
        if p.has_next(0):
            btns.add(InlineKeyboardButton('->', callback_data='paginate:1'))
        await bot.send_message(callback.from_user.id, msg, reply_markup=btns)

    @staticmethod
    async def users_admin(callback: types.CallbackQuery):
        msg, btns = messages.get_user_messages()
        await bot.send_message(callback.from_user.id, msg, reply_markup=btns)

    @staticmethod
    async def mailing(callback: types.CallbackQuery):
        await BeginMailing.mail_text.set()
        await bot.send_message(callback.from_user.id, 'Введите текст рассылки:')

    @staticmethod
    async def find_user(callback: types.CallbackQuery):
        msg = messages.get_find_user_message()
        await FindUser.username.set()
        await bot.send_message(callback.from_user.id, msg)

    @staticmethod
    async def handle_callback(callback: types.CallbackQuery):
        msg, btns = messages.get_payments_message()
        await bot.send_message(callback.from_user.id, msg, reply_markup=btns)

    @staticmethod
    async def deposit_with_crystal(callback: types.CallbackQuery):
        dp.data[callback.from_user.id] = {'pay-system': 'crystal-pay'}
        await CreateInvoice.amount.set()
        await bot.send_message(callback.from_user.id, 'Укажите сумму (USD):')

    @staticmethod
    async def deposit_with_crypto(callback: types.CallbackQuery):
        dp.data[callback.from_user.id] = {'pay-system': 'crypto-bot'}
        await bot.send_message(callback.from_user.id, 'Выберите монету:', reply_markup=messages.get_crypto_btns())

    @staticmethod
    async def set_coin(callback: types.CallbackQuery):
        dp.data[callback.from_user.id]['coin'] = callback.data
        await CreateInvoice.amount.set()
        await bot.send_message(callback.from_user.id, 'Укажите сумму (USD):')


class SpecialCallbackHandlers:
    @staticmethod
    async def paginate(callback: types.CallbackQuery):
        await dp.current_state().finish()

        last = int(callback.data.split(':')[1])
        categories = Category.all()

        p = Pagination(categories, 5)
        paginated_data = p.get_paginated()
        keys = paginated_data.keys()

        if 'buy' in callback.data:
            if p.has_next(last) and p.has_previous(last):
                msg, btns = messages.get_buy_all_categories(
                    categories[paginated_data[last]['begin']:paginated_data[last]['over']])
                btns.add(InlineKeyboardButton('<-', callback_data=f'buy_paginate:{last - 1}'),
                         InlineKeyboardButton('->', callback_data=f'buy_paginate:{last + 1}'))

                return await callback.message.edit_text(msg, reply_markup=btns)

            elif p.has_next(last):
                msg, btns = messages.get_buy_all_categories(
                    categories[paginated_data[last]['begin']:paginated_data[last]['over']])
                btns.add(InlineKeyboardButton('->', callback_data=f'buy_paginate:{last + 1}'))

                return await callback.message.edit_text(msg, reply_markup=btns)

            elif p.has_previous(last):
                msg, btns = messages.get_buy_all_categories(
                    categories[paginated_data[last]['begin']:paginated_data[last]['over']])

                btns.add(InlineKeyboardButton('<-', callback_data=f'buy_paginate:{last - 1}'))

                return await callback.message.edit_text(msg, reply_markup=btns)

        if p.has_next(last) and p.has_previous(last):
            msg, btns = messages.get_all_categories(
                categories[paginated_data[last]['begin']:paginated_data[last]['over']])
            btns.add(InlineKeyboardButton('<-', callback_data=f'paginate:{last - 1}'),
                     InlineKeyboardButton('->', callback_data=f'paginate:{last + 1}'))

            return await callback.message.edit_text(msg, reply_markup=btns)

        elif p.has_next(last):
            msg, btns = messages.get_all_categories(
                categories[paginated_data[last]['begin']:paginated_data[last]['over']])
            btns.add(InlineKeyboardButton('->', callback_data=f'paginate:{last + 1}'))

            return await callback.message.edit_text(msg, reply_markup=btns)

        elif p.has_previous(last):
            msg, btns = messages.get_all_categories(
                categories[paginated_data[last]['begin']:paginated_data[last]['over']])

            btns.add(InlineKeyboardButton('<-', callback_data=f'paginate:{last - 1}'))

            return await callback.message.edit_text(msg, reply_markup=btns)

    @staticmethod
    async def get_category_settings(callback: types.CallbackQuery):
        category_id = callback.data.split(':')[1]
        category = Category.get(category_id)
        products = Product.get_by_category_id(category_id)
        msg, btns = messages.get_category_settings(category.name, products, category_id)
        await bot.send_message(callback.from_user.id, msg, reply_markup=btns)

    @staticmethod
    async def get_product_info(callback: types.CallbackQuery):
        product_id = callback.data.split(':')[1]
        product = Product.get(product_id)
        msg, btns = messages.get_product_info(product)
        await bot.send_message(callback.from_user.id, msg, reply_markup=btns)

    @staticmethod
    async def delete_product(callback: types.CallbackQuery):
        product_id = callback.data.split(':')[1]
        product = Product.get(product_id)
        settings.session.delete(product)
        settings.session.commit()
        await bot.send_message(callback.from_user.id, 'Товар был успешно удален')

    @staticmethod
    async def category_delete(callback: types.CallbackQuery):
        category_id = callback.data.split(':')[1]
        category = Category.get(category_id)
        settings.session.delete(category)
        settings.session.commit()
        await bot.send_message(callback.from_user.id, 'Категория была успешно удалена')

    @staticmethod
    async def new_product(callback: types.CallbackQuery):
        category_id = callback.data.split(':')[1]
        dp.data['category_id'] = category_id
        await NewProduct.name.set()
        await bot.send_message(callback.from_user.id, 'Введите название товара: ')

    @staticmethod
    async def get_products(callback: types.CallbackQuery):
        category_id = callback.data.split(':')[1]
        products = Product.get_by_category_id(category_id)

        msg, btns = messages.get_product_message(products)
        await callback.message.edit_text(msg, reply_markup=btns)

    @staticmethod
    async def buy_product(callback: types.CallbackQuery):
        product_id = callback.data.split(':')[1]
        product = Product.get(product_id)
        category = Category.get(product.category_id)

        msg = messages.get_product_info1(product, category)

        dp.data[f'{callback.from_user.id}_buy'] = product

        await BuyProduct.quantity.set()
        await bot.send_message(callback.from_user.id, msg)

    @staticmethod
    async def change_balance(callback: types.CallbackQuery):
        user_id = callback.data.split(':')[1]
        user = User.get_by_tg_id(int(user_id))
        dp.data['user_change_balance'] = user
        await ChangeBalance.amount.set()
        await bot.send_message(callback.from_user.id, 'Введите сумму, которую хотите установить пользвателю:')


_bot = QiBot()
_callback_handler = CallbackHandlers()


@dp.message_handler(content_types=['text'])
async def handler(msg):
    await _bot.commands[msg.text](msg)


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    if 'paginate' in callback.data:
        return await SpecialCallbackHandlers.paginate(callback)

    elif 'buy_category_id' in callback.data:
        return await SpecialCallbackHandlers.get_products(callback)

    elif 'buy_product' in callback.data:
        return await SpecialCallbackHandlers.buy_product(callback)

    elif 'category_id' in callback.data:
        return await SpecialCallbackHandlers.get_category_settings(callback)

    elif 'product_delete' in callback.data:
        return await SpecialCallbackHandlers.delete_product(callback)

    elif 'product_get' in callback.data:
        return await SpecialCallbackHandlers.get_product_info(callback)

    elif 'category_delete' in callback.data:
        return await SpecialCallbackHandlers.category_delete(callback)

    elif 'new_product' in callback.data:
        return await SpecialCallbackHandlers.new_product(callback)

    elif 'buy_category_id' in callback.data:
        return await SpecialCallbackHandlers.get_products(callback)

    elif 'change_balance' in callback.data:
        return await SpecialCallbackHandlers.change_balance(callback)

    await _callback_handler.callbacks[callback.data](callback)


def make_bot():
    return dp
