import crayons
from dateparser import parse
from decimal import Decimal
import jsonpickle
import os
import sys

from server.models import Wallet

jsonpickle.set_encoder_options('json', indent=4)


def newline():
    print()


def blue(string, *args):
    print(crayons.blue(str(string).format(*args), bold=True))


def green(string, *args):
    print(crayons.green(str(string).format(*args), bold=True))


def red(string, *args):
    print(crayons.red(str(string).format(*args), bold=True))


class JsonHandler(object):
    def __enter__(self):
        with open('data.json', 'r') as file:
            self.data = jsonpickle.decode(file.read())
            return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open('data.json', 'w') as file:
            file.write(jsonpickle.encode(self.data))


class Menu(object):

    def __init__(self):
        self.choices = {
            '1': self.update_balance,
            '2': self.quit
        }

    def display_menu(self):
        blue("""
        1. Update Balance
        2. Quit
        """)

    def run(self, data):
        self.wallet = data
        self.wallet.update()

        newline()
        green('{} for {}'.format(self.wallet, self.wallet.paydays[0]))

        while True:
            self.display_menu()

            choice = input('Select an option: ')
            action = self.choices.get(choice)

            newline()
            if action:
                action()

            else:
                red('Please enter a valid selection')

    def update_balance(self):
        balance = input("Enter new wallet balance: ")
        self.wallet.balance = Decimal(balance)

        newline()
        green('{}'.format(self.wallet))

    def quit(self):
        green('Wallet Saved')
        newline()

        sys.exit(0)


if __name__ == '__main__':
    if not os.path.exists('data.json'):
        import jsonpickle
        jsonpickle.set_encoder_options('json', indent=4)

        date = parse(input("Enter next payday: ")).date()
        wallet = Wallet(date)
        wallet.updater.create_paydays()

        with open('data.json', 'w') as file:
            file.write(jsonpickle.encode(wallet))

    with JsonHandler() as data:
        Menu().run(data)
