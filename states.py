from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateInvoice(StatesGroup):
    amount = State()


class FindUser(StatesGroup):
    username = State()


class BeginMailing(StatesGroup):
    mail_text = State()


class NewProduct(StatesGroup):
    name = State()
    cost = State()
    file = State()


class BuyProduct(StatesGroup):
    quantity = State()


class ChangeBalance(StatesGroup):
    amount = State()


class CreateCategory(StatesGroup):
    name = State()