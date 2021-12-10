# Budget Report for Beancount Ledgers

## 1. Introcudtion

If you use the text-based ledger system ie `beancount`, and feel the need for a tools to track your expenses against your budget, then this tool may be what you need.

`budget_report` is a simple tool to read beancount ledger files as input and generate simple budget report based on the budget entries within the input beancount file. 

## 2. Installation

The simplest way to install and use `budget_report` is via pip:  

`pip install budget_report`, for installing globally

or  

`pip install budget_report --user`, if you want to install for local user  

or  

`pip install --user --no-cache-dir`, if you get error during installation saying something like *`ERROR: Failed building wheel for budget-report`*.

## 3. How-To Use

Using `budget_report` with your beancount files is a two step process:  

1. Specify your budget in the beancount files,  
2. Specifying the transactions to include in a particular budger and  
3. Generate budget report using `budget-report` script provided by this package.


### 3.1 Specifying Budget in beancount files

You specify your budget by entering a sequenct of beancount `custom` directives in the following format:  

`<Date> custom "budget" <Account> <Amount> <Currency>`

Where:  

- **Date** is in the formate **YYYY-MM-DD**,   
- **Account** is the name of the account you want to specify budget followed by 2 or more spaces,  
- **Amount** is a number specifying the budget amount allocated for this account,  
- **Currency** is the currency in which budget is specified.  

Here is an example budget:  

    2021-12-06 custom "budget" Liabilities:CreditCard   10000 RS  
    2021-12-06 custom "budget" Expenses:Car:Fuel         5000 RS  
    2021-12-06 custom "budget" Expenses:Clothing        10000 RS  
    2021-12-06 custom "budget" Expenses:Education:Fees  11000 RS  
    2021-12-06 custom "budget" Expenses:Food:DiningOut   3000 RS  
    2021-12-06 custom "budget" Expenses:Groceries       50000 RS   
    2021-12-06 custom "budget" Expenses:Medicine         2000 RS     
    2021-12-06 custom "budget" Expenses:PocketMoney     10000 RS  

Please note that:   

a. Any budgets entries in the beancount file would override any previously specified entries for the same account.  
b. The budget entries could also be put into a separate file such as `mybudget.bean` and included into your main ledger file as below:  

    include "mybudget.bean"

### 3.2 Specifying Transaction to include in budget  

There are two ways you can tell `budget-report` which transactions to include while computing budget report:  

a. Using budget name tags in your beancount ledger, and specifying the same tag at `budget-report` command line, or   
b. Giving start date as command line argument.   

#### 3.2.1  Using Budget Tags

Tags can be used in your beancount ledger to specify transactions to include in a particular budget report.  The easiest way to use beancount `pushtag` and `poptag` directive as below.  However, individullay tagging each transaction with a tag should also work.

    pushtag #Budget-Dec21 ; or any tag you want to use to name your budget!
    
    ....
    << transactions go here! >>
    ....

    poptag #Budget-Dec21  

Later, you can specify the same tag at `budget-report` command line using `-t` or `--tag` option, while generating budget report.

#### 3.2.2

Another way to tell `budget-report` which ledger entries to include in budget calculation, is to give it a start date (`-s` or `--start-date` command line option) and/or an end date (`-e` or `--end-date` command line option).  `budget-report` will include all transactions in the ledger falling at or after the given start date and at or before the given end date.

Note: Both the tag and start/end dates could be given together to fine tune the filtering, if that makes sense in your case.

### 3.3 Generating Budget report

After you have added the budget entries in your beancount file, you can generate the budget report by calling the `budget-report` script provided by this package from your shell console as below:  

`$ budget-report -t Budget-Dec21 /path/to/your/beancount_file.bean`, or  

`$ budget-report -s 2021-12-01 -e 2021-12-31 /path/to/your/beancount_file.bean`  

Notes:  

a. If end data is omitted, all entries in the ledger at/after the start date would be included in the computation.  
b. If start date is omitted, and only end date is given, all entries at/before the end date would be included.  
c. If both tag and start/end dates are given, bothe will be used to filter the entries in the ledger.

# Help at Command Line

You can get help about all `budget-report` options at the command line using the -h switch.

    $ budget-report -h
    usage: budget-report [-h] [-v] [-t TAG] [-s START_DATE] [-e END_DATE] filename

    Budget report for beancount files

    positional arguments:
    filename              Name of beancount file to process

    optional arguments:
    -h, --help            show this help message and exit
    -v, --version         Print version number and exit
    -t TAG, --tag TAG     Budget tag to use
    -s START_DATE, --start-date START_DATE
                            Budget start date
    -e END_DATE, --end-date END_DATE
                            Budget end date