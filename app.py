"""
Логика интерфейса
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import logging
import threading  # модуль для работы с многопоточностью
from datetime import datetime
from config import CRYPTO, CURRENCIES, HISTORY_FILE, REFRESH_MS
from api_client import get_crypto_rate, get_cbr_rates, convert_price

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8',
)


class CryptoApp:
    def __init__(self, root): # инициализация
        self.root = root
        self.root.title('Курсы криптовалют')
        self.root.geometry('360x400')
        self.root.resizable(False, False)

        self.history = self.load_history()
        self.auto_refresh = tk.BooleanVar(value=False)
        self._refresh_job = None

        self._build_ui()

    def _build_ui(self): # создание виджитов
        pad = {'padx': 10, 'pady': 4}

        tk.Label(self.root, text='Криптовалюта:').pack(anchor='w', **pad)
        self.combo_box = ttk.Combobox(
            self.root, values=list(CRYPTO.keys()), state='readonly')
        self.combo_box.current(0)
        self.combo_box.pack(fill='x', **pad)

        tk.Label(self.root, text='Количество монет:').pack(anchor='w', **pad)
        self.entry_amount = tk.Entry(self.root, justify='center')
        self.entry_amount.insert(0, '1')
        self.entry_amount.pack(fill='x', **pad)

        tk.Label(self.root, text='Валюта отображения:').pack(anchor='w', **pad)
        self.combo_currency = ttk.Combobox(
            self.root, values=CURRENCIES, state='readonly')
        self.combo_currency.current(0)
        self.combo_currency.pack(fill='x', **pad)

        self.button_get = tk.Button(
            self.root, text='Получить курс', command=self.on_get_rate)
        self.button_get.pack(fill='x', **pad)

        self.label_status = tk.Label(
            self.root, text='', font=('Helvetica', 10), fg='gray')
        self.label_status.pack(**pad)

        self.label_rate = tk.Label(
            self.root, text='', font=('Helvetica', 12), anchor='w')
        self.label_rate.pack(fill='x', **pad)

        self.label_total = tk.Label(
            self.root, text='', font=('Helvetica', 12, 'bold'), anchor='w')
        self.label_total.pack(fill='x', **pad)

        tk.Checkbutton(
            self.root, text='Автообновление (раз в минуту)',
            variable=self.auto_refresh, command=self.toggle_auto_refresh
        ).pack(anchor='w', **pad)

        tk.Button(
            self.root, text='История', command=self.show_history
        ).pack(fill='x', **pad)

    def on_get_rate(self): # нажатие кнопок, ввод числа монет
        symbol = self.combo_box.get()
        if not symbol:
            messagebox.showwarning('Внимание',
                                   'Выберите криптовалюту.'
                                   )
            return

        try:
            amount = float(self.entry_amount.get().replace(',', '.'))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror('Ошибка ввода',
                                 'Введите положительное число монет.'
                                 )
            return

        currency = self.combo_currency.get()
        self.button_get.config(state='disabled')
        self.label_status.config(text='Загрузка…')

        threading.Thread(
            target=self._fetch_worker,
            args=(symbol, amount, currency),
            daemon=True,
        ).start()

    def _fetch_worker(self, symbol, amount, currency):
        try:
            price_usd = get_crypto_rate(symbol, CRYPTO)
            cbr = get_cbr_rates()
            rate = convert_price(price_usd, currency, cbr)
            total = rate * amount
            logging.info('Курс %s: %.2f %s', symbol, rate, currency)
            # Безопасная передача результата
            self.root.after(0, self._show_result, symbol, amount, currency, rate, total)
        except Exception as e:
            logging.error('Ошибка при получении курса %s: %s', symbol, e)
            # Безопасная передача ошибки
            self.root.after(0, self._show_error, str(e))

    def _show_result(self, symbol, amount, currency, rate, total):
        self.button_get.config(state='normal')
        self.label_status.config(text='')
        self.label_rate.config(text=f'Курс: {rate:,.2f} {currency} за 1 {symbol}')
        self.label_total.config(
            text=f'Итого: {total:,.2f} {currency} за {amount:g} шт.'
        )
        self.add_history(symbol, amount, currency, rate, total)

    def _show_error(self, message):
        self.button_get.config(state='normal')
        self.label_status.config(text='')
        self.label_rate.config(text='Ошибка получения курса')
        self.label_total.config(text='')
        messagebox.showerror('Ошибка', message)

    def toggle_auto_refresh(self): # автообновление включить выключить
        if self.auto_refresh.get():
            self._schedule_refresh()
        elif self._refresh_job is not None:
            self.root.after_cancel(self._refresh_job)
            self._refresh_job = None

    def _schedule_refresh(self): # вызав автообновления
        if self.auto_refresh.get():
            self.on_get_rate()
            self._refresh_job = self.root.after(
                REFRESH_MS, self._schedule_refresh)

    def load_history(self): # работа с историей сохранения JSON файлом и открытием истории
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_history(self):
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logging.error('Не удалось сохранить историю: %s', e)

    def add_history(self, symbol, amount, currency, rate, total):
        self.history.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': symbol,
            'amount': amount,
            'currency': currency,
            'rate': round(rate, 2),
            'total': round(total, 2),
        })
        self.save_history()

    def show_history(self):
        window = tk.Toplevel(self.root)
        window.title('История запросов')
        window.geometry('560x320')

        columns = ('time', 'symbol', 'amount', 'currency', 'rate', 'total')
        headers = {
            'time': 'Время', 'symbol': 'Монета', 'amount': 'Кол-во',
            'currency': 'Валюта', 'rate': 'Курс', 'total': 'Итого',
        }
        tree = ttk.Treeview(window, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=headers[col])
            tree.column(col, width=90, anchor='center')
        for row in self.history:
            tree.insert('', 'end', values=(
                row['time'], row['symbol'], row['amount'],
                row['currency'], row['rate'], row['total']))
        tree.pack(fill='both', expand=True)
