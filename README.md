# Budget Report for Beancount Ledgers

## 1. Introduction

If you use the text-based ledger system ie [beancount](https://github.com/beancount/beancount), and feel the need for a tools to track your expenses against your budget, then this tool may be what you need.

`budget-report` is a simple tool to read beancount ledger files as input and generate simple budget report based on the budget entries within the input beancount file. 

## 2. Installation

The simplest way to install and use `budget-report` is via pip:  

`pip install budget-report`, for installing globally

or  

`pip install budget-report --user`, if you want to install for local user  

## 3. How-To Use

Using `budget-report` with your beancount files is a three step process:  

1. Specify your budget in the beancount files,  
2. Specifying the transactions to include in a particular budget and  
3. Generate budget report using `budget-report` script provided by this package.


### 3.1 Specifying Budget in beancount files

You specify your budget by entering a sequenct of beancount `custom` directives in the following format:  

`<Date> custom "budget" <Account> <Period> <Amount> <Currency>`

Where:  

- **Date** is in the formate **YYYY-MM-DD**,   
- **Account** is the name of the account you want to specify budget followed by 2 or more spaces,  
- **Period** is the applicable period of the budget ie one of "year", "biannual", "quarter", "month", "week" or "day"
- **Amount** is a number specifying the budget amount allocated for this account,  
- **Currency** is the currency in which budget is specified.  

Here is an example budget:  

    2021-12-06 custom "budget" Liabilities:CreditCard "month"   10000 RS  
    2021-12-06 custom "budget" Expenses:Car:Fuel "month"         5000 RS  
    2021-12-06 custom "budget" Expenses:Clothing "month"        10000 RS  
    2021-12-06 custom "budget" Expenses:Education:Fees "month"  11000 RS  
    2021-12-06 custom "budget" Expenses:Food:DiningOut "month"   3000 RS  
    2021-12-06 custom "budget" Expenses:Groceries "month"       50000 RS   
    2021-12-06 custom "budget" Expenses:Medicine "month"         2000 RS     
    2021-12-06 custom "budget" Expenses:PocketMoney "month"     10000 RS  

Please note that:   

a. Any budgets entries in the beancount file would override any previously specified entries for the same account.  
b. The budget entries could also be put into a separate file such as `mybudget.bean` and included into your main ledger file as below:  

    include "mybudget.bean"

### 3.2 Specifying Transaction to include in budget  

By default, `bean-report` includes all transactions with dates falling within the specified budget report period (ie via the -p or --period switch on command line).  If no report period is given, the period is assumed to be "month" (ie current month's budget report would be generated).

a. The default start and/or end date(s) may be overridden by giving other values as command line arguments (-s and -e options), which would then overried the reports's start and end dates.  This may be usefule when say, you are generating report of one month (or other period), but some of the tranactions from a previous (or next) month/period should actually be counted in this budget's report.   

a. Budget name tags can also be used in your beancount ledger to identify/enclose transactions to include in a budget report.  Then the same tag may be specified at the command line while generating the budget report.

#### 3.2.1  Using Budget Tags

Tags can be used in your beancount ledger to specify transactions to include in a particular budget report.  The easiest way is to use beancount `pushtag` and `poptag` directive as below.  However, individullay tagging each transaction with a tag should also work.

    pushtag #Budget-Dec21 ; or any tag you want to use to name your budget!
    
    ....
    << transactions go here! >>
    ....

    poptag #Budget-Dec21  

Later, you can specify the same tag at `budget-report` command line using `-t` or `--tag` option, while generating budget report.

Note: If `budget-report` encounters a posting in the ledger with the budget tag, it is included into the bugetted postings regardless of the existence a corresponding `budget` directive.  If no corresponding `budget` directive entry is found, an entry for the posting account with zero budget value is automatically added for this purpose.  

#### 3.2.2 Using start and end dates  

Another way to tell `budget-report` which ledger entries to include in budget calculation, is to give it a start date (`-s` or `--start-date` command line option) and/or an end date (`-e` or `--end-date` command line option).  `budget-report` will include all transactions in the ledger falling at or after the given start date and at or before the given end date.

Note: Both the tag and start/end dates could be given together to fine tune the filtering, if that makes sense in your case.

### 3.3 Generating Budget report

After you have added the budget entries in your beancount file, you can generate the budget report by calling the `budget-report` script provided by this package from your shell console as below:  

`$ budget-report -t Budget-Dec21 /path/to/your/beancount_file.bean`, or  

`$ budget-report -s 2021-12-01 -e 2021-12-31 /path/to/your/beancount_file.bean`  

It would generate output similar to that shown below:

    Budget Report:
      Period: 'month' (2021-12-01 to 2021-12-31)
	Total Income: 150,000.00
	Total Budget: 108,000.00
	Budget Surplus/Deficit: 42,000.00

    Account                    Budget    Expense    (%)    Remaining    (%)
    -----------------------  --------  ---------  -----  -----------  -----
    Liabilities:CreditCard    10000.0     5000.0   50.0       5000.0   50.0
    Expenses:Car:Fuel          5000.0     1000.0   20.0       4000.0   80.0
    Expenses:Clothing         10000.0     5000.0   50.0       5000.0   50.0
    Expenses:Education:Fees   11000.0     5000.0   45.5       6000.0   54.5
    Expenses:Food:DiningOut   10000.0     3000.0   30.0       7000.0   70.0
    Expenses:Gardening            0.0     2000.0             -2000.0
    Expenses:Groceries        50000.0    10800.0   21.6      39200.0   78.4
    Expenses:Medicine          2000.0     1000.0   50.0       1000.0   50.0
    Expenses:PocketMoney      10000.0     6000.0   60.0       4000.0   40.0
    Totals                   108000.0    38800.0   35.9      69200.0   64.1

Notes:  

a. If end date is omitted, all entries in the ledger at/after the start date would be included in the computation.  
b. If start date is omitted, and only end date is given, all entries at/before the end date would be included.  
c. If both tag and start/end dates are given, bothe will be used to filter the entries in the ledger.

# Help at Command Line

You can get help about all `budget-report` options at the command line using the -h switch.

    usage: budget-report [-h] [-v] [-V] [-t TAG] [-s START_DATE] [-e END_DATE] [-p PERIOD] filename

    Budget report for beancount files

    positional arguments:
      filename              Name of beancount file to process

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         Print version number and exit
      -V, --verbose         Print verbose output for errors
      -t TAG, --tag TAG     Budget tag to use
      -s START_DATE, --start-date START_DATE
                            Budget start date
      -e END_DATE, --end-date END_DATE
                            Budget end date
      -p PERIOD, --period PERIOD
                            Budget period
 
