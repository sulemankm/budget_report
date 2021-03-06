import sys
from budgetreport import report, main
from beancount import loader

def testSingleAccountBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2021-01-01 custom "budget" Expenses:Groceries "month"   1000.0 USD

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand
    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 1000.0
      assert br.total_expenses == 400.0
      assert br.getTotalRemaining() == 600.0
      assert br.getAccountBudget('Expenses:Groceries') == 1000.0
      assert br.getAccountExpense('Expenses:Groceries') == 400.0

def testBudgetWithZeroValue(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2021-01-01 custom "budget" Expenses:Groceries "month"   0.0 USD

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand
    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 0.0
      assert br.total_expenses == 400.0
      assert br.getTotalRemaining() == -400.0
      assert br.getAccountBudget('Expenses:Groceries') == 0.0
      assert br.getAccountExpense('Expenses:Groceries') == 400.0

def testTaggedBugget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2021-01-01 custom "budget" Expenses:Groceries "month"   1000.0 USD

    pushtag #test-budget

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    200.0 USD
      Assets:CashInHand

    poptag #test-budget

    2021-01-03 * "Payee 2" "Some description"
      Expenses:Groceries                    100.0 USD
      Assets:CashInHand

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", "-t", "test-budget", "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 1000.0
      assert br.total_expenses == 600.0
      assert br.getTotalRemaining() == 400.0
      assert br.getAccountBudget('Expenses:Groceries') == 1000.0
      assert br.getAccountExpense('Expenses:Groceries') == 600.0

def testBuggetWithStartAndEndDate(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2021-01-01 custom "budget" Expenses:Groceries "month"   1000.0 USD

    2020-12-31 * "TestPayee" "Some description"
      Expenses:Groceries                    500.0 USD
      Assets:CashInHand

    2021-01-01 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand

    2021-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    300.0 USD
      Assets:CashInHand

    2021-01-10 * "TestPayee" "Some description"
      Expenses:Groceries                    200.0 USD
      Assets:CashInHand

    2021-01-13 * "Payee 2" "Some description"
      Expenses:Groceries                    100.0 USD
      Assets:CashInHand

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", "-s" "2021-01-01", "-e", "2021-01-10", "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 1000.0
      assert br.total_expenses == 900.0
      assert br.getTotalRemaining() == 100.0
      assert br.getAccountBudget('Expenses:Groceries') == 1000.0
      assert br.getAccountExpense('Expenses:Groceries') == 900.0


def testMultipleAccountBudgets(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Clothing
2001-01-01 open Expenses:Education

2021-01-01 custom "budget" Expenses:Clothing "month"     1000.0 USD
2021-01-01 custom "budget" Expenses:Education "month"    2000.0 USD

2021-01-02 * "Test Payee 2" "Clothes etc"
    Expenses:Clothing                          300.0 USD
    Assets:CashInHand

2021-01-03 * "School" "Fees"
    Expenses:Education                        1200.0 USD
    Assets:CashInHand
  """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 3000.0
      assert br.total_expenses == 1500.0
      assert br.getTotalRemaining() == 1500.0
      assert br.getAccountBudget('Expenses:Education') == 2000.0
      assert br.getAccountExpense('Expenses:Education') == 1200.0
      assert br.getAccountBudget('Expenses:Clothing') == 1000.0
      assert br.getAccountExpense('Expenses:Clothing') == 300.0


def testBudgetRedefinitionOverridesOldValue(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Clothing
2001-01-01 open Expenses:Education

2021-01-01 custom "budget" Expenses:Clothing "month"     1000.0 USD
2021-01-01 custom "budget" Expenses:Clothing "month"    2000.0 USD

  """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 2000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 2000.0
      assert br.getAccountBudget('Expenses:Clothing') == 2000.0
      assert br.getAccountExpense('Expenses:Clothing') == 0.0

def testAutomaticallyAddsZeroBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2001-01-02 * "TestPayee" "Some description"
      Expenses:Groceries                    400.0 USD
      Assets:CashInHand
    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2001-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 0.0
      assert br.total_expenses == 400.0
      assert br.getTotalRemaining() == -400.0
      assert br.getAccountBudget('Expenses:Groceries') == 0.0
      assert br.getAccountExpense('Expenses:Groceries') == 400.0

def testYearBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education

2001-01-01 custom "budget" Expenses:Groceries "year"  12000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "biannual"  6000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "quarter"  3000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "month"  1000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "week"  250.0 RS
2001-01-01 custom "budget" Expenses:Education "year"  20000.0 RS

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-p', 'year', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 32000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 32000.0
      assert br.getAccountBudget('Expenses:Groceries') == 12000.0
      assert br.getAccountBudget('Expenses:Education') == 20000.0
 
def testMonthBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education

2001-01-01 custom "budget" Expenses:Groceries "year"  12000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "biannual"  6000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "quarter"  3000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "month"  1000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "week"  250.0 RS
2001-01-01 custom "budget" Expenses:Education "month"  2000.0 RS

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-p', 'month', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 3000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 3000.0
      assert br.getAccountBudget('Expenses:Groceries') == 1000.0
      assert br.getAccountBudget('Expenses:Education') == 2000.0

def testQuarterBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education

2001-01-01 custom "budget" Expenses:Groceries "year"  12000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "biannual"  6000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "quarter"  3000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "month"  1000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "week"  250.0 RS
2001-01-01 custom "budget" Expenses:Education "quarter"  2000.0 RS

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-p', 'quarter', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 5000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 5000.0
      assert br.getAccountBudget('Expenses:Groceries') == 3000.0
      assert br.getAccountBudget('Expenses:Education') == 2000.0
 
def testBiannualBudget(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education

2001-01-01 custom "budget" Expenses:Groceries "year"  12000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "biannual"  6000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "quarter"  3000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "month"  1000.0 RS
2001-01-01 custom "budget" Expenses:Groceries "week"  250.0 RS
2001-01-01 custom "budget" Expenses:Education "biannual"  2000.0 RS

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-p', 'biannual', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 8000.0
      assert br.total_expenses == 0.0
      assert br.getTotalRemaining() == 8000.0
      assert br.getAccountBudget('Expenses:Groceries') == 6000.0
      assert br.getAccountBudget('Expenses:Education') == 2000.0
 
def testLiabilitiesHandling(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Assets:CashInHand
2001-01-01 open Assets:CheckingAccount
2001-01-01 open Expenses:Groceries
2001-01-01 open Expenses:Education
2001-01-01 open Liabilities:CreditCard

2001-01-01 custom "budget" Expenses:Groceries "month"  12000.0 RS
2001-01-01 custom "budget" Liabilities:CreditCard "month"  6000.0 RS
2001-01-01 custom "budget" Expenses:Education "month"  2000.0 RS

2021-01-02 * "Test Payee 2" "Groceries"
    Expenses:Groceries                            900.0 RS
    Assets:CashInHand

2021-01-03 * "School" "Fees"
    Expenses:Education                           2200.0 RS
    Assets:CashInHand

2021-01-03 * "Online Shopping" "Groceries"
    Expenses:Groceries                           2500.0 RS
    Liabilities:CreditCard

2021-01-20 * "Bank" "Credit Card Payment"
    Liabilities:CreditCard                       1000.0 RS
    Assets:CheckingAccount
    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 20000.0
      assert br.total_expenses == 4100.0
      assert br.getTotalRemaining() == 15900.0

      assert br.getAccountBudget('Expenses:Groceries') == 12000.0
      assert br.getAccountBudget('Expenses:Education') == 2000.0
      assert br.getAccountBudget('Liabilities:CreditCard') == 6000.0

      assert br.getAccountExpense('Expenses:Groceries') == 900.0
      assert br.getAccountExpense('Expenses:Education') == 2200.0
      assert br.getAccountExpense('Liabilities:CreditCard') == 1000.0

def testTotalIncome(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Income:Salary
2001-01-01 open Income:Business
2001-01-01 open Assets:BankAccount
2001-01-01 open Assets:CashInHand

2021-01-02 * "Employer" "Salary"
    Assets:BankAccount                          150000.0 RS
    Income:Salary

2021-01-03 * "Misc" "Income from sales"
    Assets:CashInHand                           200000.0 RS
    Income:Business

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_income == 350000.0

def testBudgetEndDate(monkeypatch):
    entries, errors, options_map = loader.load_string("""
2001-01-01 open Expenses:Clothing
2001-01-01 open Expenses:Education
2001-01-01 open Expenses:Food
2001-01-01 open Expenses:Travel

2021-01-01 custom "budget" Expenses:Clothing "month"     1000.0 USD
2021-01-01 custom "budget" Expenses:Education "month"    2000.0 USD
2021-01-01 custom "budget" Expenses:Food "month"     1000.0 USD

2021-02-01 custom "budget" Expenses:Travel "month"    2000.0 USD

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", '-s', '2021-01-01', "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      assert br.total_budget == 4000.0
      assert br.getAccountBudget('Expenses:Travel') == 0.0
