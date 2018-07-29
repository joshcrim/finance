from datetime import date, timedelta
from decimal import Decimal

from finance import db
from finance.wallet.models import Expense, Income, Payday


class WalletUpdater(object):

    def __init__(self, wallet):
        self.wallet = wallet

    def add_payday(self, date):
        payday = Payday(wallet=self.wallet, date=date)

        for income in self.wallet.recurring_incomes:
            i = Income(
                payday=payday,
                parent=income,
                name=income.name,
                amount=income.amount)

            db.session.add(i)

        for expense in self.wallet.recurring_expenses:
            e = Expense(
                payday=payday,
                parent=expense,
                name=expense.name,
                amount=expense.amount)

            db.session.add(e)

        db.session.commit()

    def add_next_payday(self):
        last_payday = self.wallet.paydays.order_by(Payday.date.desc()).first()
        next_pay_date = last_payday.date + timedelta(weeks=2)
        self.add_payday(next_pay_date)

    def update_savings(self):
        # Add the savings amount from all paydays before today to the wallet balance
        payday_savings = sum([p.savings for p in self.wallet.paydays.filter(Payday.date <= date.today())])
        self.wallet.balance = Decimal(self.wallet.balance) + payday_savings

    def update_paydays(self):
        # Remove the paydays before today
        for payday in self.wallet.paydays.filter(Payday.date <= date.today()):
            db.session.delete(payday)

        db.session.commit()

    def create_paydays(self):
        # Create new paydays to ensure the user can see 10 paydays into the future
        while self.wallet.paydays.count() < 10:
            self.add_next_payday()

    def update(self):
        self.update_savings()
        self.update_paydays()
        self.create_paydays()
