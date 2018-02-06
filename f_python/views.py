from flask import Flask, redirect, request, render_template, url_for
from f_python.forms import TransactionForm, WalletForm
from f_python.models import Wallet

app = Flask(
    __name__,
    template_folder='./templates/',
    static_folder='./static')


#
# Wallet
#

@app.route('/', methods=['GET'])
def wallet():
    wallet = Wallet.load()
    wallet.update()

    update_wallet_form = WalletForm()
    create_recurring_form = TransactionForm()

    context = {
        'wallet': wallet,
        'update_wallet_form': update_wallet_form,
        'create_recurring_form': create_recurring_form}

    return render_template('wallet.html', **context)


@app.route('/update-wallet', methods=['POST'])
def update_wallet():
    wallet = Wallet.load()
    form = WalletForm(request.form)
    if form.validate():
        balance = form.balance.data
        wallet.balance = balance
        wallet.save()

    return redirect(url_for('wallet'))


#
# Payday
#

@app.route('/<payday>')
def payday(payday=None):
    wallet = Wallet.load()
    payday = wallet.paydays[int(payday)] if payday else wallet.paydays[0]
    form = TransactionForm()

    return render_template('payday.html', wallet=wallet, payday=payday, form=form)


@app.route('/create-payday-transaction/<payday>', methods=['POST'])
def create_payday_transaction(payday):
    wallet = Wallet.load()
    payday = wallet.paydays[int(payday)] if payday else wallet.paydays[0]

    form = TransactionForm(request.form)
    if form.validate():
        transaction_type = form.trans_type.data
        transaction = form.name.data, form.amount.data

        if transaction_type == 'expense':
            payday.new_expense(transaction)

        if transaction_type == 'income':
            payday.new_income(transaction)

        wallet.save()

    return redirect(url_for('payday', wallet=wallet, payday=wallet.get_payday_id(payday)))


@app.route('/delete-payday-transaction/<payday>/<transaction_id>', methods=['GET', 'POST'])
def delete_payday_transaction(transaction_id, payday=None):
    wallet = Wallet.load()
    payday = wallet.paydays[int(payday)]

    payday.delete_transaction(transaction_id)
    wallet.save()

    return redirect(url_for('payday', wallet=wallet, payday=wallet.get_payday_id(payday)))


#
# Recurring Transactions
#

@app.route('/create-recurring-transaction', methods=['POST'])
def create_recurring_transaction():
    wallet = Wallet.load()

    form = TransactionForm(request.form)
    if form.validate():
        transaction_type = form.trans_type.data
        transaction = form.name.data, form.amount.data

        if transaction_type == 'expense':
            wallet.new_recurring_expense(transaction)

        if transaction_type == 'income':
            wallet.new_recurring_income(transaction)

        wallet.save()

    return redirect(url_for('wallet'))


@app.route('/delete-recurring-transaction/<transaction_id>', methods=['GET', 'POST'])
def delete_recurring_transaction(transaction_id):
    wallet = Wallet.load()

    wallet.delete_recurring_transaction(transaction_id)
    wallet.save()

    return redirect(url_for('wallet'))


@app.route('/edit-transaction/<payday>/<transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id, payday=None):
    wallet = Wallet.load()
    payday = wallet.paydays[int(payday)]
    transaction = payday.get_transaction(transaction_id)

    form = TransactionForm(request.form, obj=transaction)
    if form.validate():
        transaction.name = form.name.data
        transaction._amount = form.amount.data
        wallet.save()

        return redirect(url_for('payday', wallet=wallet, payday=wallet.get_payday_id(payday)))

    return render_template('transaction_edit.html', wallet=wallet, payday=payday, transaction=transaction, form=form)
