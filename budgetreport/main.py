#!/usr/bin/env python3
# main.py

import argparse
import pkg_resources  # part of setuptools
from budgetreport import report
from beancount import loader

def init_arg_parser():
    parser = argparse.ArgumentParser(description="Budget report for beancount files")
    parser.add_argument("-v", "--version", action="version", help="Print version number and exit",
        version='%(prog)s {}'.format(pkg_resources.require("budget_report")[0].version))
    parser.add_argument("-t", "--tag", help="Budget tag to use")
    parser.add_argument("-s", "--start-date", help="Budget start date")
    parser.add_argument("-e", "--end-date", help="Budget end date")
    parser.add_argument("-p", "--period", help="Budget period")
    parser.add_argument("filename", help="Name of beancount file to process")
    return parser

def script_main():
    parser = init_arg_parser()
    args = parser.parse_args()

    entries, errors, options_map = loader.load_file(args.filename)
    if errors:
        print(errors)
        #assert False

    br = report.generateBudgetReport(entries, options_map, args)
    br.printReport()

if __name__ == "__main__":
    script_main()
