from flask import redirect, request, render_template, url_for
from flask_login import current_user, login_required

from finance import db
from finance.wallet import bp
from finance.wallet.forms import TransactionForm, WalletForm
from finance.wallet.models import Expense, Income, Payday, RecurringExpense, RecurringIncome
from finance.wallet.updater import WalletUpdater


#
# Wallet
#

@bp.route('/', methods=['GET'])
@login_required
def wallet():
    wallet = current_user.wallet

    updater = WalletUpdater(wallet)
    updater.update()

    update_wallet_form = WalletForm()
    create_recurring_form = TransactionForm()

    context = {
        'wallet': wallet,
        'update_wallet_form': update_wallet_form,
        'create_recurring_form': create_recurring_form}

    return render_template('wallet.html', **context)


@bp.route('/update-wallet', methods=['POST'])
@login_required
def update_wallet():
    wallet = current_user.wallet

    form = WalletForm(request.form)
    if form.validate():
        balance = form.balance.data
        wallet.balance = balance
        db.session.add(wallet)
        db.session.commit()

    return redirect(url_for('wallet.wallet'))


@bp.route('/<payday>')
@login_required
def payday(payday=None):
    wallet = current_user.wallet
    payday = Payday.query.get(payday)

    form = TransactionForm()

    return render_template('payday.html', wallet=wallet, payday=payday, form=form)


@bp.route('/create-payday-transaction/<payday>', methods=['POST'])
@login_required
def create_payday_transaction(payday):
    wallet = current_user.wallet
    payday = Payday.query.get(payday)

    form = TransactionForm(request.form)
    if form.validate():
        transaction_type = form.trans_type.data

        if transaction_type == 'expense':
            expense = Expense(
                payday=payday,
                name=form.name.data,
                amount=form.amount.data)

            db.session.add(expense)

        if transaction_type == 'income':
            income = Income(
                payday=payday,
                name=form.name.data,
                amount=form.amount.data)

            db.session.add(income)

        db.session.commit()

    return redirect(url_for('wallet.payday', wallet=wallet, payday=payday.id))


@bp.route('/delete-payday-income/<payday>/<transaction_id>', methods=['GET', 'POST'])
@login_required
def delete_payday_income(transaction_id, payday=None):
    wallet = current_user.wallet
    payday = Payday.query.get(payday)

    income = Income.query.get(transaction_id)
    db.session.delete(income)
    db.session.commit()

    return redirect(url_for('wallet.payday', wallet=wallet, payday=payday.id))


@bp.route('/delete-payday-expense/<payday>/<transaction_id>', methods=['GET', 'POST'])
@login_required
def delete_payday_expense(transaction_id, payday=None):
    wallet = current_user.wallet
    payday = Payday.query.get(payday)

    income = Expense.query.get(transaction_id)
    db.session.delete(income)
    db.session.commit()

    return redirect(url_for('wallet.payday', wallet=wallet, payday=payday.id))


@bp.route('/create-recurring-transaction', methods=['POST'])
@login_required
def create_recurring_transaction():
    wallet = current_user.wallet

    form = TransactionForm(request.form)
    if form.validate():
        transaction_type = form.trans_type.data

        if transaction_type == 'expense':
            recurring_expense = RecurringExpense(
                wallet=wallet,
                name=form.name.data,
                amount=form.amount.data)

            for payday in wallet.paydays:
                expense = Expense(
                    payday=payday,
                    parent=recurring_expense,
                    name=form.name.data,
                    amount=form.amount.data)

                db.session.add(expense)

            db.session.add(recurring_expense)

        if transaction_type == 'income':
            recurring_income = RecurringIncome(
                wallet=wallet,
                name=form.name.data,
                amount=form.amount.data)

            for payday in wallet.paydays:
                income = Income(
                    payday=payday,
                    parent=recurring_income,
                    name=form.name.data,
                    amount=form.amount.data)

                db.session.add(income)

            db.session.add(recurring_income)

        db.session.commit()

    return redirect(url_for('wallet.wallet'))


@bp.route('/delete-recurring-income/<transaction_id>', methods=['GET', 'POST'])
@login_required
def delete_recurring_income(transaction_id):
    income = RecurringIncome.query.get(transaction_id)

    for child in income.children:
        db.session.delete(child)

    db.session.delete(income)
    db.session.commit()

    return redirect(url_for('wallet.wallet'))


@bp.route('/delete-recurring-expense/<transaction_id>', methods=['GET', 'POST'])
@login_required
def delete_recurring_expense(transaction_id):
    expense = RecurringExpense.query.get(transaction_id)

    for child in expense.children:
        db.session.delete(child)

    db.session.delete(expense)
    db.session.commit()

    return redirect(url_for('wallet.wallet'))
