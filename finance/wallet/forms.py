from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField


class TransactionForm(FlaskForm):
    trans_type = SelectField(choices=[('expense', 'Expense'), ('income', 'Income')])
    name = StringField()
    amount = DecimalField(places=2)


class WalletForm(FlaskForm):
    balance = DecimalField(places=2)
