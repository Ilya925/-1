"""Настройки и данные (можно добавлять данные, чтобы не просматривать весь код
Добавлено авто обновление раз в минуту
"""

CRYPTO = {
    'BTC': {'id': 'bitcoin', 'name': 'Bitcoin'},
    'ETH': {'id': 'ethereum', 'name': 'Ethereum'},
    'TRUMP': {'id': 'official-trump', 'name': 'Official Trump'},
    'USDT': {'id': 'tether', 'name': 'Tether'},
    'SOL': {'id': 'solana', 'name': 'Solana'},
}

CURRENCIES = ['USD', 'RUB', 'EUR']  # список валют для выпадающего списка

HISTORY_FILE = 'history.json'
LOG_FILE = 'app.log'
REFRESH_MS = 60000  # автообновление раз в минуту
