#!/usr/bin/env python3
# main.py
import re
import beancount
from beancount import loader
from beancount.query import query
from tabulate import tabulate
#import budget_report

class BudgetReportItem:
    def __init__(self, date, account, budget):
        self.date = date
        self.account = account
        self.budget = budget
        self.expense = 0

    def __str__(self):
        return self.account

class BudggetReport:
    def __init__(self) -> None:
        self.budgetReportItems = {} # An dict to store budget report items
        self.total_budget = 0
        self.total_expenses = 0
        self.total_remaining = 0

    def addBudget(self, date, account, budget):
        be = BudgetReportItem(date, account, budget)
        self.total_budget += budget
        self.budgetReportItems[account] = be

    def addBudgetExpense(self, account, expense):
        self.total_expenses += expense
        self.total_remaining = self.total_budget - self.total_expenses
        self.budgetReportItems[account].expense = expense

    def getBudgetReportItems(self):
        return self.budgetReportItems

    def printReport(self):
        print("\n")
        print("{:<30} {:<8} {:<17} {:<17}".format("Budget Account", "Budget", "Expense (%)", "Remaining (%)"))
        print("{:<30} {:<8} {:<17} {:<17}".format("------------------------------", "-------", "----------------", "----------------"))

        for budget_account in self.budgetReportItems:
            bri = self.budgetReportItems[budget_account]
            str_expense = "{:<8}({:<5})".format(bri.expense, round(100 * bri.expense / bri.budget, 1))
            remaining = bri.budget - bri.expense
            str_remaining = "{:<8}({:<5})".format(remaining, round(100 * remaining / bri.budget, 1))
            print("{:<30} {:<8} {:<17} {:<17}".format(bri.account, bri.budget, str_expense, str_remaining))

        # Print totals
        print("{:<30} {:<8} {:<17} {:<17}".format("------------------------------", "-------", "----------------", "----------------"))
        str_expense_total = "{:<8}({:<5})".format(self.total_expenses, round(100 * self.total_expenses / self.total_budget, 1))
        str_remaining_total = "{:<8}({:<5})".format(self.total_remaining, round(100 * self.total_remaining / self.total_budget, 1))
        print("{:<30} {:<8} {:<17} {:<17}".format(" ", self.total_budget, str_expense_total, str_remaining_total))

# getBudgetReport : entries, options_map -> { account: BudgetReportItem }
def generateBudgetReport(entries, options_map, args):
    br = BudggetReport()

    for entry in entries:
        if isinstance(entry, beancount.core.data.Custom) and entry.type == 'budget':
            #be = BudgetReportItem(entry.date, str(entry.values[0].value), abs(entry.values[1].value.number))
            br.addBudget(entry.date, str(entry.values[0].value), abs(entry.values[1].value.number))

    # Get actual expenses for all budget accounts
    for budget_account in br.getBudgetReportItems():
        sql_query = "select account, SUM(position) AS amount WHERE account ~ '{}'".format(budget_account)
        if args.tag:
            sql_query += " and '{}' in tags".format(args.tag)

        if args.start_date:
            sql_query += " and date >= {}".format(args.start_date)

        if args.end_date:
            sql_query += " and date <= {}".format(args.end_date)

        rtypes, rrows = query.run_query(entries, options_map, sql_query, '', numberify=True)
        if len(rrows) != 0:
            account = rrows[0][0]
            amount = rrows[0][1]
            br.addBudgetExpense(account, amount)
            #be = __theBudgetReport[account]
            #be.expense = amount

    return br

# ========================================================================
import argparse
import pkg_resources  # part of setuptools

def script_main():
    parser = argparse.ArgumentParser(description="Budget report for beancount files")
    parser.add_argument("-v", "--version", action="version", help="Print version number and exit",
        version='%(prog)s {}'.format(pkg_resources.require("budget_report")[0].version))
    parser.add_argument("-t", "--tag", help="Budget tag to use")
    parser.add_argument("-s", "--start-date", help="Budget start date")
    parser.add_argument("-e", "--end-date", help="Budget end date")
    parser.add_argument("filename", help="Name of beancount file to process")
    args = parser.parse_args()

    entries, errors, options_map = loader.load_file(args.filename)
    if errors:
        print(errors)
        #assert False

    br = generateBudgetReport(entries, options_map, args)
    br.printReport()

