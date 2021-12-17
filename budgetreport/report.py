#!/usr/bin/env python3
import re
import datetime as dt
import beancount
from beancount.query import query
from tabulate import tabulate


class BudgetReportItem:
    def __init__(self, date, account, budget):
        self.date = date
        self.account = account
        self.budget = float(budget)
        self.expense = 0.0

    def __str__(self):
        return [self.date, self.account, self.budget, self.expense]

    def getRemaining(self):
        return self.budget - self.expense

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

class BudggetReport:
    def __init__(self) -> None:
        self.budgetReportItems = {} # An dict to store budget report items
        self.total_budget = 0.0
        self.total_expenses = 0.0

    def addBudget(self, date, account, budget):
        if account in self.budgetReportItems:
            self.total_budget -= self.budgetReportItems[account].budget
            self.budgetReportItems[account].budget = budget # update budget
        else:
            be = BudgetReportItem(date, account, budget)
            self.budgetReportItems[account] = be # add new budget
            
        self.total_budget += float(budget)
        

    def addBudgetExpense(self, date, account, expense):
        if not account in self.budgetReportItems: # if budget does no exist
            raise Exception(
                'addBudgetExpense: Unhandled account {} in budget.'.format(account))
        self.total_expenses += float(expense)
        self.budgetReportItems[account].expense += float(expense)

    def getAccountBudget(self, account):
        return self.budgetReportItems[account].budget

    def getAccountExpense(self, account):
        return self.budgetReportItems[account].expense

    def getTotalRemaining(self):
        return self.total_budget - self.total_expenses

    def getPercentExpenses(self):
        if not self.total_budget == 0:
            return round(100.0 * float(self.total_expenses) / float(self.total_budget), 1)

    def getPercentRemaining(self):
        if not self.total_budget == 0:
            return round(100.0 * float(self.getTotalRemaining()) / float(self.total_budget), 1)

    def getBudgetReportItems(self):
        return self.budgetReportItems

    def toList(self):
        result = []
        for account in self.budgetReportItems:
            result.append(self.budgetReportItems[account].toList())
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
def collectBudgetAccounts(entries, options_map, args, br):
    # Collect all budgets
    for entry in entries:
        if isinstance(entry, beancount.core.data.Custom) and entry.type == 'budget':
            br.addBudget(entry.date, str(entry.values[0].value), abs(
                entry.values[1].value.number))
   
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

    budgetted_accounts = {**br.getBudgetReportItems()}

    for i in range(len(rrows)):
        #date = rrows[i][0]
        account = rrows[i][0]
        if not account in budgetted_accounts:
            # dt.date.today().strftime("%Y-%m-%d")
            br.addBudget(dt.date.today().strftime("%Y-%m-%d"), account, 0.0)

    return {**br.getBudgetReportItems()} # return a copy for iteration


# getBudgetReport : entries, options_map -> { account: BudgetReportItem }
def generateBudgetReport(entries, options_map, args):
    br = BudggetReport()

    budgetted_accounts = collectBudgetAccounts(entries, options_map, args, br)
    # print(tabulate([(key, budgetted_accounts[key].__str__())
    #       for key in budgetted_accounts.keys()]))

    # Get actual postings for all budget accounts
    for budget_account in budgetted_accounts:
        postings_query = "select date, account, position, balance AS amount WHERE account = '{}'".format(budget_account)
        if args.tag:
            postings_query += " and '{}' in tags".format(args.tag)

        if args.start_date:
            postings_query += " and date >= {}".format(args.start_date)

        if args.end_date:
            postings_query += " and date <= {}".format(args.end_date)
        
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
