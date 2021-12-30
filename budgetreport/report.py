# report.py
import re, calendar
from datetime import datetime as dt
import beancount
from beancount.query import query
from tabulate import tabulate
from .budget import BudgetItem

class Period:
    def __init__(self, period):
        self.period = period

    def getPeriodStart(self, date):
        if self.period == 'year':
            return dt(date.year, 1, 1)
        elif self.period == 'biannual':
            if date.month < 7:
                return dt(date.year, 1, 1) # 1st January
            else:
                return dt(date.year, 7, 1) # 1st July
        elif self.period == 'month':
            return dt(date.year, date.month, 1)
        elif self.period == 'week':
            if date.day < 8: day = 1
            elif date.day < 15: day = 8
            elif date.day < 22: day = 15
            else: day = 22 # FIXME: Last week may be 7 to 10 days
            return dt(date.year, date.month, day)
        elif self.period == 'day':
            return date
        else:
            return dt(1970, 1, 1) # If period == 'none', then period starts from 1970
 
    def getPeriodEnd(self, date):
        last_day_of_month = calendar.monthrange(date.year, date.month)[1]
        if self.period == 'year':
            return dt(date.year, 12, 31)
        elif self.period == 'biannual':
            if date.month < 7:
                return dt(date.year, 6, 30) # 1st January
            else:
                return dt(date.year, 12, 31) # 1st July
        elif self.period == 'month':
            return dt(date.year, date.month, last_day_of_month)
        elif self.period == 'week':
            if date.day < 8: day = 7
            elif date.day < 15: day = 14
            elif date.day < 22: day = 21
            else: day = last_day_of_month # FIXME: Last week may be 7 to 10 days
            return dt(date.year, date.month, day)
        elif self.period == 'day':
            return date
        else:
            return date
    
class BudggetReport:
    def __init__(self) -> None:
        self.budgetItems = {} # An dict to store budget report items
        self.total_budget = 0.0
        self.total_expenses = 0.0
        self.start_date = dt.today()
        self.end_date = dt.today()
        self.tag = ''

    def _addBudget(self, date, account, period, budget):
        if account in self.budgetItems:
            self.total_budget -= self.budgetItems[account].budget
            self.budgetItems[account].period = period
            self.budgetItems[account].budget = budget # update budget
        else:
            be = BudgetItem(date, account, period, budget)
            self.budgetItems[account] = be # add new budget

        self.total_budget += float(budget)

    def addBudget(self, budget):
        self._addBudget(budget.date, budget.account, budget.period, budget.budget)

    def addBudgetExpense(self, date, account, expense):
        if not account in self.budgetItems: # if budget does no exist
            raise Exception(
                'addBudgetExpense: Unhandled account {} in budget.'.format(account))
        self.total_expenses += float(expense)
        self.budgetItems[account].expense += float(expense)

    def getAccountBudget(self, account):
        return self.budgetItems[account].budget

    def getAccountExpense(self, account):
        return self.budgetItems[account].expense

    def getTotalRemaining(self):
        return self.total_budget - self.total_expenses

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
def collectBudgetAccounts(entries, options_map, args):
    budgets = {} #BudgetReport()
    # Collect all budgets
    for entry in entries:
        if isinstance(entry, beancount.core.data.Custom) and entry.type == 'budget':
            account = str(entry.values[0].value)
            period = entry.values[1]
            budget = abs(entry.values[2].value.number)
            budgets[account] = BudgetItem(entry.date, account, period, budget)
            #br.addBudget(entry.date, str(entry.values[0].value), entry.values[1], abs(
            #    entry.values[2].value.number))

    # Collect expense accounts not budgetted but have expenses
    acct_query = "select account WHERE account ~ 'Expense' "
    if args.tag:
        acct_query += "and '{}' in tags".format(args.tag)

    if args.start_date:
        # if args.tag:
        #     acct_query += " and "
        acct_query += "and date >= {}".format(args.start_date)

    if args.end_date:
        # if args.tag or args.start_date:
        #     acct_query += " and "
        # else:
        #     acct_query += " WHERE "
        acct_query += "and date <= {}".format(args.end_date)

    rtypes, rrows = query.run_query(
        entries, options_map, acct_query, '', numberify=True)
    #print('acct_query result = {}'.format(tabulate(rrows)))

    #budgetted_accounts = {**br.getBudgetItems()}
    for i in range(len(rrows)):
        #date = rrows[i][0]
        account = rrows[i][0]
        if not account in budgets: #budgetted_accounts:
            # dt.date.today().strftime("%Y-%m-%d")
            # Automatically add a monthly budget for unbudgetted transactions
            #br.addBudget(dt.today().strftime("%Y-%m-%d"), account, "none", 0.0)
            budgets[account] = BudgetItem(dt.today().strftime("%Y-%m-%d"), account, "none", 0.0)

    return budgets #{**br.getBudgetItems()} # return a copy for iteration


# getBudgetReport : entries, options_map -> { account: BudgetItem }
def generateBudgetReport(entries, options_map, args):
    br = BudggetReport()
    if args.tag:
        br.tag = args.tag
    if args.period:
        br.setPeriod(args.period)
    if args.start_date:
        br.start_date = args.start_date
    if args.end_date:
        br.end_date = args.end_date

    budgetted_accounts = collectBudgetAccounts(entries, options_map, args)
    for account in budgetted_accounts:
        br.addBudget(budgetted_accounts[account])
    # print(tabulate([(key, budgetted_accounts[key].__str__())
    #       for key in budgetted_accounts.keys()]))

    # Get actual postings for all budget accounts
    for budget_account in budgetted_accounts:
        postings_query = "select date, account, position, balance AS amount WHERE account = '{}'".format(budget_account)
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
            account = budget_account #rrows[len(rrows)-1][1]
            amount = abs(rrows[len(rrows)-1][3]) # get balance from last row
            if amount == 0.0:
                print('Warning: adding zero expense for account= {}'.format(account))
            br.addBudgetExpense(date, account, amount)

    return br
