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
        self.tag = ''
        self.period = Period('month') # default period is month
        self.start_date = self.period.getPeriodStart(dt.min)
        self.end_date = self.period.getPeriodEnd(dt.today())

    def _addBudget(self, date, account, period, budget):
        assert period == self.period.period # only allow adding budget of matching period
        if account in self.budgetItems:
            self.total_budget -= float(self.budgetItems[account].budget)
            self.budgetItems[account].period = period
            self.budgetItems[account].budget = budget # update budget
        else:
            be = BudgetItem(date, account, period, budget)
            self.budgetItems[account] = be # add new budget

        self.total_budget += float(budget)

    def addBudget(self, budget):
        print('addBudget: {}'.format(budget))
        self._addBudget(budget.date, budget.account, budget.period, budget.budget)

    def addBudgetExpense(self, date, account, expense):
        if not (account in self.budgetItems): # if budget does no exist
            raise Exception('addBudgetExpense: Unhandled account {} in budget.\nself.budgetItems: {}'.format(account, self.budgetItems))

        # print('date: ', date, 'start_date: ', self.start_date, 'end_date: ', self.end_date)
        if date >= self.start_date and date <= self.end_date: # Expense should fall withing the period
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

    def setPeriod(self, period, start_date=dt.today()):
        self.period = Period(period)
        self.start_date = self.period.getPeriodStart(start_date)
        self.end_date = self.period.getPeriodEnd(start_date)

    def toList(self):
        result = []
        for account in self.budgetItems:
            result.append(self.budgetItems[account].toList())
        # Append totals
        result.append(['Totals', self.total_budget, self.total_expenses,
            self.getPercentExpenses(), self.getTotalRemaining(),
            self.getPercentRemaining()])
        return result

    def printReport(self, args):
        print('Budget Report:\n  Period: \'{}\''.format(self.period.period))
        if args.start_date:
            print('  Start: {}, End: {}'.format(self.start_date, self.end_date))
        if args.tag:
            print('  Tag \'{}\''.format(args.tag))
        print('\n')
        headings = ['Account', 'Budget', 'Expense', '(%)', 'Remaining', '(%)']
        budget_data = self.toList()
        print(tabulate(budget_data, headings, numalign="right", floatfmt=".1f"))

    # Collect Budget accounts
    def collectBudgets(self, entries, options_map, args):
        # Collect all budgets
        for entry in entries:
            if isinstance(entry, beancount.core.data.Custom) and entry.type == 'budget' and entry.values[1].value == self.period.period:
                account = str(entry.values[0].value)
                period = entry.values[1].value
                budget = abs(entry.values[2].value.number)
                self._addBudget(entry.date, account, period, budget)

        # Collect expense accounts not budgetted but have expenses within the report period
        acct_query = "select account WHERE account ~ 'Expense' "
        if args.tag:
            acct_query += " and '{}' in tags ".format(args.tag)

        if args.start_date:
            acct_query += " and date >= {} ".format(args.start_date)

        if args.end_date:
            acct_query += " and date <= {} ".format(args.end_date)

        rtypes, rrows = query.run_query(
            entries, options_map, acct_query, '', numberify=True)

        for i in range(len(rrows)):
            account = rrows[i][0]
            if not account in self.budgetItems:
                assert not account in self.budgetItems
                self._addBudget(dt.today().strftime(
                    "%Y-%m-%d"), account, self.period.period, 0.0)

# getBudgetReport : entries, options_map -> { account: BudgetItem }
def generateBudgetReport(entries, options_map, args):
    br = BudgetReport()
    if args.tag:
        br.tag = args.tag
    if args.period:
        br.setPeriod(args.period)
    if args.start_date:
        #br.start_date = dt.fromisoformat(args.start_date).date()
        br.setPeriod(br.period.period, dt.fromisoformat(args.start_date).date())
    if args.end_date:
        br.end_date = dt.fromisoformat(args.end_date).date()
        assert br.end_date >= br.start_date

    br.collectBudgets(entries, options_map, args)

    # Get actual postings for all budget accounts
    for account in br.budgetItems: # budgets:
        postings_query = "select date, account, position, balance AS amount WHERE account = '{}'".format(account)
        if args.tag:
            postings_query += " and '{}' in tags ".format(br.tag)

        if args.start_date:
            postings_query += " and date >= {} ".format(args.start_date)#.strftime('%Y-%m-%d'))

        if args.end_date:
            postings_query += " and date <= {} ".format(args.end_date)#.strftime('%Y-%m-%d'))
        #print('query: ', postings_query)
        rtypes, rrows = query.run_query(entries, options_map, postings_query, '', numberify=True)

        if len(rrows) != 0:
            try:
                date = rrows[len(rrows)-1][0] # Get date of last posting
                amount = abs(rrows[len(rrows)-1][3]) # get balance from last row
                if amount == 0.0:
                    print('Warning: adding zero expense for account= {}'.format(account))
            except Exception as e:
                print('Exception caused by rrows value: \n  ', rrows[len(rrows)-1])
            else:
                #print('adding expense: {}-{}'.format(account, amount))
                br.addBudgetExpense(date, account, amount)
        #else:
        #    print('Warning: No expenses found for account: {}'.format(account))

    return br
