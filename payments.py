import requests
from settings import CRYSTAL_PAY_TOKEN_1, CRYPTO_BOT_TOKEN
import json


class CrystalPay:
    @staticmethod
    def create_invoice(amount):
        request = f'https://api.crystalpay.ru/v1/?s={CRYSTAL_PAY_TOKEN_1}&n=emptylll&o=invoice-create&amount={amount}&lifetime=60&currency=USD'
        response = requests.get(request).json()
        print(response)
        return response

    @staticmethod
    def check_invoice(payment_id):
        request = f'https://api.crystalpay.ru/v1/?s={CRYSTAL_PAY_TOKEN_1}&n=emptylll&o=invoice-check&i={payment_id}'
        response = requests.get(request).json()
        if response['state'] == 'payed':
            return True


class CryptoBot:
    @staticmethod
    def auth():
        requests.get('https://pay.crypt.bot/api/getMe',
                     headers={'Crypto-Pay-API-Token': f'{CryptoBot}'})

    @staticmethod
    def create_invoice(amount, coin):
        print(amount, coin)
        response = requests.get('https://testnet-pay.crypt.bot/api/createInvoice',
                                headers={'Crypto-Pay-API-Token': f'{CRYPTO_BOT_TOKEN}'},
                                json={'asset': f'{coin}', 'amount': float(amount)})

        return response

    @staticmethod
    def check_invoice(payment_id):
        response = requests.get('https://testnet-pay.crypt.bot/api/getInvoices',
                                headers={'Crypto-Pay-API-Token': '6092:AAWIT4QJN08hTP9UHtbtdY2X8dxAxIO5zHY'},
                                json={'invoice_ids': f'{payment_id},'}).json()

        if response['result']['items'][0]['status'] == 'paid':
            return True

    @staticmethod
    def get_exchange_rates():
        response = requests.get('https://testnet-pay.crypt.bot/api/getExchangeRates',
                                headers={'Crypto-Pay-API-Token': f'{CRYPTO_BOT_TOKEN}'}, )
        return response
