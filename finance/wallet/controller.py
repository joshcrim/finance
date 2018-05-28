from finance import api
from finance.wallet.models import Payday, Wallet


def register_api(app):
    api.create_api(
        Wallet,
        app=app,
        methods=["GET"])

    api.create_api(
        Payday,
        app=app,
        methods=["GET"],
        include_methods=[
            'income_sum',
            'expense_sum',
            'savings',
            'savings_to_date'])
