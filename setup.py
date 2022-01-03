from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()
    
setup(name='budget_report',
      version='0.3',
      description='Budget report for beancount files',
      long_description=readme(),
      long_description_content_type="text/markdown",
      keywords='beancount budget ledger hledger',
      url='http://github.com/sulemankm/budget_report',
      project_urls={
          "Bug Tracker": "https://github.com/sulemankm/budget_report/issues",
      },
      author='Suleman Khalid',
      author_email='sulemankm@yahoo.com',
      license='GPL-v3',
      packages=find_packages(include=['budgetreport']),
      install_requires=[
          'beancount',
          'tabulate'
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
#      scripts=['bin/budget-report.py']
      entry_points={
        'console_scripts': ['budget-report=budgetreport.main:script_main']
      },
      zip_safe=False)
