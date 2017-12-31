from wtforms import DecimalField, Form, SelectField, StringField


class TransactionForm(Form):
    trans_type = SelectField(choices=[('expense', 'Expense'), ('income', 'Income')])
    name = StringField()
    amount = DecimalField(places=2)


class WalletForm(Form):
    balance = DecimalField(places=2)
