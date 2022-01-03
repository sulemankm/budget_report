# main.py

import argparse, sys
import pkg_resources  # part of setuptools
from beancount import loader
from beancount.parser import printer

from pathlib import Path
file = Path(__file__).resolve()
package_root_directory = file.parents [1]
sys.path.append(str(package_root_directory))

from budgetreport import report

def init_arg_parser():
    parser = argparse.ArgumentParser(description="Budget report for beancount files")
    parser.add_argument("-v", "--version", action="version", help="Print version number and exit",
        version='%(prog)s {}'.format(pkg_resources.require("budget_report")[0].version))
    parser.add_argument('-V', '--verbose', action='store_true', help='Print verbose output for errors')
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
        if args.verbose:
            printer.print_errors(errors)
        else:
            print('Warning: {} errors while parsing input file.'.format(len(errors)))

    br = report.generateBudgetReport(entries, options_map, args)
    br.printReport(args)

if __name__ == "__main__":
    script_main()
