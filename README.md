# Bank-Management-System
This GitHub repository contains the complete source code and database implementation for the Bank Management System developed as part of the DBMS Mini Project. The project demonstrates full integration of a relational database (MySQL) with a Python-based GUI using Tkinter.
Project Workflow
1. System Initialization

The MySQL database is created using the bank2.sql file.

Tables, constraints, triggers, stored procedures, functions, and views are automatically set up.

Initial sample data is inserted for branches, customers, accounts, loans, etc.

The Python application connects to the database using mysql-connector-python.

2. Launching the Application

Run the GUI using:

python bank_gui2.py


The Tkinter application opens with a Dashboard showing:

Total Customers

Total Accounts

Total Balance

Total Loans

3. Customer Workflow

User opens the Customers tab.

Performs actions:

Add a new customer

Update existing customer

Delete customer

View customer list

Built-in validation checks Email, Phone, and DOB.

The trigger prevents invalid DOB entries.

SQL function GetCustomerAge() is used when clicking "Check Age".

4. Account Workflow

In the Accounts tab, user can:

Add an account

Delete an account

Deposit money

Withdraw money

Deposit and Withdraw buttons call stored procedures:

DepositAmount()

WithdrawAmount()

Every transaction is automatically added to the Transactions table.

5. Loan Workflow

In the Loans tab, the user enters loan details.

Interest rate auto-fills based on the selected loan type (from LoanTypes table).

User can:

Add loan

Update loan

Delete loan

Trigger Loan_Status_Check updates the loan status automatically if loan amount becomes zero.

6. Beneficiary Management Workflow

In the Beneficiaries tab, the user can:

Add new beneficiaries

Search by Customer ID

Delete beneficiary

View all beneficiaries

Phone number validation prevents faulty entries.

Beneficiary account numbers are verified before transfers.

7. Fund Transfer Workflow

User selects From Account, Beneficiary Account, and Amount.

System performs:

Check if sender account exists

Check if beneficiary exists

Check sufficient account balance

Updates sender/receiver balances accordingly.

Automatically inserts a transaction record of type Transfer.

8. Transactions Workflow

The Transactions tab shows all deposit, withdrawal, and transfer logs.

User can search for transactions by Account ID.

Data is pulled directly from the Transactions table.

9. Reporting Workflow

The Reports tab provides:

Branch Totals

Uses SQL function GetTotalBalance(branch_id)

Shows total balance held in each branch

Top Customers

Displays top 5 customers based on total account balance

Customer Loan Summary

Uses SQL view CustomerLoanSummary.

Customer Search Report

Shows customer’s total balance + total loan amount.

10. Exit Workflow

User simply closes the GUI window.

All changes remain saved in MySQL permanently.
