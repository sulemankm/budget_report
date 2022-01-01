# report.py
from datetime import datetime as dt
import beancount
from beancount.query import query
from tabulate import tabulate
from .budget import BudgetItem
from .period import Period

class BudgetReport:
    def __init__(self) -> None:
        self.budgetItems = {} # An dict to store budget report items
        self.total_budget = 0.0
        self.total_expenses = 0.0
        self.start_date = dt.today()
        self.end_date = dt.today()
        self.tag = ''
        self.period = Period('none')

    def _addBudget(self, date, account, period, budget):
        if account in self.budgetItems:
            self.total_budget -= float(self.budgetItems[account].budget)
            self.budgetItems[account].period = period
            self.budgetItems[account].budget = budget # update budget
        else:
            be = BudgetItem(date, account, period, budget)
            self.budgetItems[account] = be # add new budget

        self.total_budget += float(budget)

    def addBudget(self, budget):
        # print('addBudget: budget: ', budget)
        # print('B4 _addBudget: self.budgetItems: ', self.budgetItems)
        self._addBudget(budget.date, budget.account, budget.period, budget.budget)
        # print('After _addBudget: self.budgetItems: ', self.budgetItems)

    def addBudgetExpense(self, date, account, expense):
        # print("\naddBudgetExpense:")
        # print("self.period:", self.period)
        # print("Account:", account)
        # print("self.budgetItems: ", self.budgetItems)
        if not (account in self.budgetItems): # if budget does no exist
            raise Exception('addBudgetExpense: Unhandled account {} in budget.\nself.budgetItems: {}'.format(
                account, self.budgetItems))
        self.total_expenses += float(expense)
        self.budgetItems[account].expense += float(expense)

    def getAccountBudget(self, account):
        return self.budgetItems[account].budget

    def getAccountExpense(self, account):
        return self.budgetItems[account].expense

    def getTotalRemaining(self):
        return float(self.total_budget) - float(self.total_expenses)

    def getPercentExpenses(self):
        if not self.total_budget == 0:
            return round(100.0 * float(self.total_expenses) / float(self.total_budget), 1)

    def getPercentRemaining(self):
        if not self.total_budget == 0:
            return round(100.0 * float(self.getTotalRemaining()) / float(self.total_budget), 1)

    def getBudgetItems(self):
        return self.budgetItems

    def setPeriod(self, period):
        self.period = Period(period)
        self.start_date = self.period.getPeriodStart(dt.today())
        self.end_date = self.period.getPeriodEnd(dt.today())

    def toList(self):
        result = []
        for account in self.budgetItems:
            result.append(self.budgetItems[account].toList())
        # Append totals
        result.append(['Totals', self.total_budget, self.total_expenses,
            self.getPercentExpenses(), self.getTotalRemaining(),
            self.getPercentRemaining()])
        return result

    def printReport(self):
        headings = ['Account', 'Budget', 'Expense', '(%)', 'Remaining', '(%)']
        budget_data = self.toList()
        print(tabulate(budget_data, headings, numalign="right", floatfmt=".1f"))

    # Collect Budget accounts
    def collectBudgets(self, entries, options_map, args):
        # budgets = {} #BudgetReport()
        # Collect all budgets
        for entry in entries:
            if isinstance(entry, beancount.core.data.Custom) and entry.type == 'budget':
                account = str(entry.values[0].value)
                period = entry.values[1].value
                budget = abs(entry.values[2].value.number)
                self._addBudget(entry.date, account, period, budget)
                # self.budgetItems[account] = BudgetItem(
                #     entry.date, account, period, budget)
                # budgets[account] = BudgetItem(entry.date, account, period, budget)
                #br.addBudget(entry.date, str(entry.values[0].value), entry.values[1].value, abs(
                #    entry.values[2].value.number))

        # Collect expense accounts not budgetted but have expenses
        acct_query = "select account WHERE account ~ 'Expense' "
        if args.tag:
            acct_query += "and '{}' in tags".format(args.tag)

        if args.start_date:
            acct_query += "and date >= {}".format(args.start_date)

        if args.end_date:
            acct_query += "and date <= {}".format(args.end_date)

        rtypes, rrows = query.run_query(
            entries, options_map, acct_query, '', numberify=True)
        #print('acct_query result = {}'.format(tabulate(rrows)))

        for i in range(len(rrows)):
            account = rrows[i][0]
            if not account in self.budgetItems: # budgets: #budgetted_accounts:
                assert not account in self.budgetItems #budgets
                self._addBudget(dt.today().strftime(
                    "%Y-%m-%d"), account, args.period, 0.0)
                # self.budgetItems[account] = BudgetItem(dt.today().strftime(
                #     "%Y-%m-%d"), account, args.period, 0.0)
                #budgets[account] = BudgetItem(dt.today().strftime("%Y-%m-%d"), account, args.period, 0.0)

        # print("collectBudgets():")
        # print(self.budgetItems)
        #return budgets #{**br.getBudgetItems()} # return a copy for iteration

# getBudgetReport : entries, options_map -> { account: BudgetItem }
def generateBudgetReport(entries, options_map, args):
    br = BudgetReport()
    if args.tag:
        br.tag = args.tag
    if args.period:
        br.setPeriod(args.period)
    if args.start_date:
        br.start_date = args.start_date
    if args.end_date:
        br.end_date = args.end_date

    #budgets = collectBudgets(entries, options_map, args)
    br.collectBudgets(entries, options_map, args)
    # print("\ngenerateBudgetReport:")
    # print(budgets)
    # for (account, budget) in budgets.items():
    #     print(account, ': ', budget)
    #     if budget.period == args.period:
    #         br.addBudget(budget)
            #br._addBudget(budget.date, budget.account, budget.period, budget.budget)

    # print('br.budgetItems: ', br.budgetItems)
    # print(tabulate([(key, budgetted_accounts[key].__str__())
    #       for key in budgetted_accounts.keys()]))

    # Get actual postings for all budget accounts
    for account in br.budgetItems: # budgets:
        postings_query = "select date, account, position, balance AS amount WHERE account = '{}'".format(account)
        if args.tag:
            postings_query += " and '{}' in tags".format(br.tag)

        if args.start_date:
            postings_query += " and date >= {}".format(br.start_date)

        if args.end_date:
            postings_query += " and date <= {}".format(br.end_date)

        rtypes, rrows = query.run_query(entries, options_map, postings_query, '', numberify=True)
        #print('postings_query result: \n {}'.format(tabulate(rrows)))

        if len(rrows) != 0:
            date = rrows[len(rrows)-1][0] # Get date of last posting
            #account = account #rrows[len(rrows)-1][1]
            amount = abs(rrows[len(rrows)-1][3]) # get balance from last row
            if amount == 0.0:
                print('Warning: adding zero expense for account= {}'.format(account))
            br.addBudgetExpense(date, account, amount)

    return br
