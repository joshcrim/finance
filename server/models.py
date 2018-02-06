from datetime import date, timedelta
from decimal import Decimal

import jsonpickle
jsonpickle.set_encoder_options('json', indent=4)


def delete_list_item(x_list, item_id):
    for x in x_list:
        if x.id == int(item_id):
            del x_list[x_list.index(x)]


transaction_id = 0


def transaction(trans):
    if not isinstance(trans, Transaction):
        name, amount = trans

        global transaction_id
        transaction_id += 1

        trans = Transaction(transaction_id, name, Decimal(amount))

    return trans


class Transaction(object):

    def __init__(self, id, name, amount):
        self.id = id
        self.name = name
        self._amount = amount

    def __str__(self):
        return '{t.name}: ${t.amount}'.format(t=self)

    def __repr__(self):
        return '<Transaction: {t.name} - ${t.amount}'.format(t=self)

    @property
    def amount(self):
        return self._amount


class Payday(object):

    def __init__(self, date):
        self.date = date
        self.incomes = list()
        self.expenses = list()

    def __str__(self):
        return '{} - ${}'.format(self.date.strftime("%B %d"), self.savings)

    def __repr__(self):
        return '<Payday: {p.date.strftime("%d/%m/%y")} - ${p.savings}>'.format(p=self)

    @property
    def income_sum(self):
        return sum([i.amount for i in self.incomes])

    @property
    def expense_sum(self):
        return sum([e.amount for e in self.expenses])

    @property
    def savings(self):
        return self.income_sum - self.expense_sum

    def get_transaction(self, transaction_id):
        for transaction in self.incomes + self.expenses:
            if transaction.id == int(transaction_id):
                return transaction

    def new_income(self, transaction_data):
        self.incomes.append(transaction(transaction_data))

    def new_expense(self, transaction_data):
        self.expenses.append(transaction(transaction_data))

    def delete_transaction(self, transaction_id):
        for x in [self.incomes, self.expenses]:
            delete_list_item(x, transaction_id)


class Wallet(object):

    def __init__(self, first_payday_date):
        self.balance = Decimal(0)
        self.paydays = list()
        self.recurring_incomes = list()
        self.recurring_expenses = list()

        self.updater = WalletUpdater(self)
        self.updater.add_payday(first_payday_date)

    def __str__(self):
        return 'Wallet: ${}'.format(self.balance)

    def __repr__(self):
        return '<Wallet: ${}>'.format(self.balance)

    @classmethod
    def load(self):
        with open('data.json', 'r') as file:
            wallet = jsonpickle.decode(file.read())

        return wallet

    def save(self):
        with open('data.json', 'w') as file:
            file.write(jsonpickle.encode(self))

    def update(self):
        WalletUpdater(self).update()
        self.save()

    def get_payday_id(self, payday):
        return self.paydays.index(payday)

    def savings_for_payday(self, payday):
        payday_index = self.get_payday_id(payday)
        return self.balance + sum([p.savings for p in self.paydays[:payday_index + 1]])

    def new_recurring_income(self, transaction_data):
        trans = transaction(transaction_data)
        self.recurring_incomes.append(trans)

        for payday in self.paydays:
            payday.new_income(trans)

    def new_recurring_expense(self, transaction_data):
        trans = transaction(transaction_data)
        self.recurring_expenses.append(trans)

        for payday in self.paydays:
            payday.new_expense(trans)

    def delete_recurring_transaction(self, transaction_id):
        for x in [self.recurring_incomes, self.recurring_expenses]:
            delete_list_item(x, transaction_id)

        for payday in self.paydays:
            payday.delete_transaction(transaction_id)


class WalletUpdater(object):

    def __init__(self, wallet):
        self.wallet = wallet

    def add_payday(self, date):
        payday = Payday(date)

        for income in self.wallet.recurring_incomes:
            payday.new_income(income)

        for expense in self.wallet.recurring_expenses:
            payday.new_income(expense)

        self.wallet.paydays.append(payday)

    def add_next_payday(self):
        next_pay_date = self.wallet.paydays[-1].date + timedelta(weeks=2)
        self.add_payday(next_pay_date)

    def update_savings(self):
        # Add the savings amount from all paydays before today to the wallet balance
        self.wallet.balance = Decimal(self.wallet.balance) + sum([p.savings for p in self.wallet.paydays if p.date < date.today()])

    def update_paydays(self):
        # Remove the paydays before today
        self.wallet.paydays = [p for p in self.wallet.paydays if p.date >= date.today()]

    def create_paydays(self):
        # Create new paydays to ensure the user can see 10 paydays into the future
        while len(self.wallet.paydays) < 10:
            self.add_next_payday()

    def update(self):
        self.update_savings()
        self.update_paydays()
        self.create_paydays()
