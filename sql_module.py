import datetime
import settings
from settings import base, session, engine
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship


class User(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True)
    username = Column(String(100), unique=True)
    current_deposit = Column(Integer, default=0)
    all_deposit = Column(Integer, default=0)
    is_banned = Column(Boolean, default=False)

    def create(self):
        session.add(self)
        session.commit()
        return self

    @staticmethod
    def get_by_username(username: str):
        return session.query(User).filter(User.username == username).all()

    @staticmethod
    def get_by_tg_id(tg_id: int):
        return session.query(User).filter(User.tg_id == tg_id).all()

    @staticmethod
    def all():
        return session.query(User).filter(User.is_banned == False).all()

    def create_or_pass(self, tg_id: int, username: str):
        if len(self.get_by_tg_id(tg_id)) == 0:
            self.username = username
            self.tg_id = tg_id
            self.create()


class Category(base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)

    def create(self):
        session.add(self)
        session.commit()
        return self

    @staticmethod
    def all():
        return session.query(Category).all()

    @staticmethod
    def get(_id):
        return session.query(Category).get(_id)


class Product(base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    cost = Column(Integer, default=0)
    quantity = Column(Integer, default=0)

    def create(self):
        session.add(self)
        session.commit()
        return self

    @staticmethod
    def get_by_category_id(_id):
        return session.query(Product).filter(Product.category_id == _id).all()

    @staticmethod
    def get(_id):
        return session.query(Product).get(_id)


class ProductData(base):
    __tablename__ = 'products_data'
    id = Column(Integer, primary_key=True)
    data = Column(String(500), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))

    def create(self):
        session.add(self)
        session.commit()
        return self

    @staticmethod
    def get_by_product_id(_id):
        return session.query(ProductData).filter(ProductData.product_id == _id).all()


class Statistic(base):
    __tablename__ = 'statistic'
    id = Column(Integer, primary_key=True)
    deposits = Column(Integer, default=0)
    sold_accounts = Column(Integer, default=0)

    def create(self):
        session.add(self)
        session.commit()
        return self

    @staticmethod
    def get():
        return session.query(Statistic).get(1)

# Statistic().create()

# base.metadata.drop_all(engine)
# base.metadata.create_all(engine)
