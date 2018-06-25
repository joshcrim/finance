from finance import db


class Transaction(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Numeric(precision=10, decimal_return_scale=2))


class RecurringIncome(Transaction):
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    children = db.relationship('Income', backref='parent', lazy='dynamic')

    def __repr__(self):
        return '<RecurringIncome %r>' % self.name


class RecurringExpense(Transaction):
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    children = db.relationship('Expense', backref='parent', lazy='dynamic')

    def __repr__(self):
        return '<RecurringExpense %r>' % self.name


class Income(Transaction):
    payday_id = db.Column(db.Integer, db.ForeignKey('payday.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('recurring_income.id'), nullable=True)

    def __repr__(self):
        return '<Income %r>' % self.name


class Expense(Transaction):
    payday_id = db.Column(db.Integer, db.ForeignKey('payday.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('recurring_expense.id'), nullable=True)

    def __repr__(self):
        return '<Expense %r>' % self.name


class Payday(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    incomes = db.relationship('Income', backref='payday', lazy='dynamic', cascade="all,delete")
    expenses = db.relationship('Expense', backref='payday', lazy='dynamic', cascade="all,delete")

    date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return '<Payday %r>' % self.date

    @property
    def income_sum(self):
        return sum([i.amount for i in self.incomes.all()])

    @property
    def expense_sum(self):
        return sum([e.amount for e in self.expenses.all()])

    @property
    def savings(self):
        return self.income_sum - self.expense_sum

    @property
    def savings_to_date(self):
        paydays = self.wallet.paydays.filter(Payday.date <= self.date)
        return self.wallet.balance + sum([p.savings for p in paydays])


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    paydays = db.relationship('Payday', backref='wallet', lazy='dynamic')
    recurring_incomes = db.relationship('RecurringIncome', backref='wallet', lazy='dynamic')
    recurring_expenses = db.relationship('RecurringExpense', backref='wallet', lazy='dynamic')

    balance = db.Column(db.Numeric(precision=10, decimal_return_scale=2))

    @property
    def recurring_income_sum(self):
        return sum([i.amount for i in self.recurring_incomes.all()])

    @property
    def recurring_expense_sum(self):
        return sum([e.amount for e in self.recurring_expenses.all()])
