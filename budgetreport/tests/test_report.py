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

def testCorrectlyReadsBudgetPeriodicity(monkeypatch):
    entries, errors, options_map = loader.load_string("""
    2001-01-01 open Assets:CashInHand
    2001-01-01 open Expenses:Groceries

    2001-01-01 custom "budget" Expenses:Groceries "year"  12000.0 RS
    2001-01-01 custom "budget" Expenses:Groceries "biannual"  6000.0 RS
    2001-01-01 custom "budget" Expenses:Groceries "quarter"  3000.0 RS
    2001-01-01 custom "budget" Expenses:Groceries "month"  1000.0 RS
    2001-01-01 custom "budget" Expenses:Groceries "week"  250.0 RS
    2001-01-01 custom "budget" Expenses:Groceries "day"  30.0 RS

    """)

    with monkeypatch.context() as m:
      m.setattr(sys, "argv", ["prog", "testfile.bean"])

      parser = main.init_arg_parser()
      test_args = parser.parse_args()

      br = report.generateBudgetReport(entries, options_map, test_args)
      # assert br.total_budget == 0.0
      # assert br.total_expenses == 400.0
      # assert br.getTotalRemaining() == -400.0
      # assert br.getAccountBudget('Expenses:Groceries') == 0.0
      # assert br.getAccountExpense('Expenses:Groceries', 'year') == 12000.0
      # assert br.getAccountExpense('Expenses:Groceries', 'biannual') == 6000.0
      # assert br.getAccountExpense('Expenses:Groceries', 'quarter') == 3000.0
      # assert br.getAccountExpense('Expenses:Groceries', 'month') == 1000.0
      # assert br.getAccountExpense('Expenses:Groceries', 'week') == 250.0
      # assert br.getAccountExpense('Expenses:Groceries', 'day') == 30.0
 
