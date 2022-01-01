# budget.py

class BudgetItem:
    def __init__(self, date, account, period, budget):
        self.date = date
        self.account = account
        self.period = period
        self.budget = float(budget)
        self.expense = 0.0

    def __str__(self):
        return 'BudgetItem: ' + str(self.date) + ' ' + str(self.account) + ' ' + str(self.period) + ' ' + str(self.budget) + ' ' + str(self.expense)

    def getRemaining(self):
        return float(self.budget) - float(self.expense)

    def getPercentExpense(self):
        if self.budget:
            return round(100.0 * float(self.expense) / float(self.budget), 1)

    def getPercentRemaining(self):
        if self.budget:
            return round(100.0 * float(self.getRemaining()) / float(self.budget), 1)

    def toList(self):
        return [self.account, self.budget, self.expense,
                self.getPercentExpense(), self.getRemaining(),
                self.getPercentRemaining()]
