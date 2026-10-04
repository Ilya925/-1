""" Работа с API и конвертация
выполнение логики и расчетов
"""
import requests


def get_crypto_rate(symbol, crypto_map):
    """Курс монеты в USD по данным CoinGecko."""
    coin_id = crypto_map[symbol]['id']
    url = ('https://api.coingecko.com/api/v3/simple/price'
           f'?ids={coin_id}&vs_currencies=usd')
    response = requests.get(url, timeout=10)
    if response.status_code == 429:
        raise RuntimeError('Превышен лимит запросов к CoinGecko. Подождите минуту.')
    response.raise_for_status()
    data = response.json()
    return float(data[coin_id]['usd'])


def get_cbr_rates():
    """Курсы ЦБ РФ: сколько рублей за 1 USD и за 1 EUR."""
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return {
        'USD': float(data['Valute']['USD']['Value']),
        'EUR': float(data['Valute']['EUR']['Value']),
    }


def convert_price(price_usd, currency, cbr):
    """Переводит цену из USD в выбранную валюту."""
    if currency == 'USD':
        return price_usd
    if currency == 'RUB':
        return price_usd * cbr['USD']
    if currency == 'EUR':
        # Конвертация через USD: (USD->RUB) / (EUR->RUB) даёт кросс-курс
        return price_usd * cbr['USD'] / cbr['EUR']
    return price_usd
