"""
Создаем и запускаем окно приложения
"""
import tkinter as tk
from app import CryptoApp


def main():
    root = tk.Tk()
    CryptoApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
