-- ==========================================
-- FINAL SQL SCRIPT : BANKING MANAGEMENT SYSTEM
-- ==========================================
DROP DATABASE IF EXISTS bank_miniproject2;
CREATE DATABASE bank_miniproject2;
USE bank_miniproject2;

-- ==========================================
-- Branch
-- ==========================================
CREATE TABLE Branch (
    Branch_ID INT PRIMARY KEY,
    Branch_Name VARCHAR(100) NOT NULL UNIQUE,
    Location VARCHAR(100) NOT NULL DEFAULT 'Unknown'
);

INSERT INTO Branch VALUES
(101, 'Main Branch', 'Bangalore'),
(102, 'City Branch', 'Hyderabad'),
(103, 'Tech Park Branch', 'Chennai'),
(104, 'Central Branch', 'Mumbai'),
(105, 'Airport Branch', 'Delhi');

-- ==========================================
-- Customer
-- ==========================================
CREATE TABLE Customer (
    CUS_ID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    DOB DATE NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    PhoneNo VARCHAR(15) NOT NULL UNIQUE,
    CompNo VARCHAR(20) DEFAULT 'N/A',
    Branch_ID INT,
    FOREIGN KEY (Branch_ID) REFERENCES Branch(Branch_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CHECK (Email LIKE '%@%.%'),
    CHECK (PhoneNo REGEXP '^[0-9]{10}$')
);

-- ✅ DOB Validation using Trigger (future date prevention)
DELIMITER //
CREATE TRIGGER Validate_Customer_DOB_Insert
BEFORE INSERT ON Customer
FOR EACH ROW
BEGIN
    IF NEW.DOB > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid DOB: cannot be a future date';
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER Validate_Customer_DOB_Update
BEFORE UPDATE ON Customer
FOR EACH ROW
BEGIN
    IF NEW.DOB > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid DOB: cannot be a future date';
    END IF;
END //
DELIMITER ;

INSERT INTO Customer VALUES
(1, 'Ravi Kumar', '1990-05-12', 'ravi.kumar@email.com', '9876543210', 'C1001', 101),
(2, 'Anita Sharma', '1988-08-25', 'anita.sharma@email.com', '9876543211', 'C1002', 102),
(3, 'Vikram Singh', '1995-02-15', 'vikram.singh@email.com', '9876543212', 'C1003', 103),
(4, 'Sneha Rao', '1992-07-19', 'sneha.rao@email.com', '9876543213', 'C1004', 104),
(5, 'Arjun Mehta', '1985-11-10', 'arjun.mehta@email.com', '9876543214', 'C1005', 105);

-- ==========================================
-- Account
-- ==========================================
CREATE TABLE Account (
    Account_ID INT PRIMARY KEY,
    Acc_Type VARCHAR(20) NOT NULL DEFAULT 'Saving'
        CHECK (Acc_Type IN ('Saving', 'Current', 'Fixed')),
    Opened_Date DATE NOT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'Active'
        CHECK (Status IN ('Active', 'Closed', 'Frozen')),
    Balance DECIMAL(18,2) NOT NULL DEFAULT 0
        CHECK (Balance >= 0),
    CUS_ID INT NOT NULL,
    FOREIGN KEY (CUS_ID) REFERENCES Customer(CUS_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

INSERT INTO Account VALUES
(401, 'Saving', '2020-01-15', 'Active', 150000, 1),
(402, 'Current', '2021-03-12', 'Active', 300000, 2),
(403, 'Saving', '2022-07-10', 'Frozen', 50000, 3),
(404, 'Fixed', '2019-09-05', 'Closed', 1000000, 4),
(405, 'Saving', '2023-04-20', 'Active', 200000, 5);

-- ==========================================
-- Transactions
-- ==========================================
CREATE TABLE Transactions (
    Transaction_ID INT AUTO_INCREMENT PRIMARY KEY,
    Description VARCHAR(200) DEFAULT 'N/A',
    Date_of_Transaction DATE NOT NULL,
    Type VARCHAR(20) NOT NULL
        CHECK (Type IN ('Deposit', 'Withdraw', 'Transfer')),
    Amount DECIMAL(18,2) NOT NULL CHECK (Amount > 0),
    Account_ID INT NOT NULL,
    FOREIGN KEY (Account_ID) REFERENCES Account(Account_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

INSERT INTO Transactions (Description, Date_of_Transaction, Type, Amount, Account_ID) VALUES
('Salary Credit', '2023-07-01', 'Deposit', 50000, 401),
('ATM Withdrawal', '2023-07-05', 'Withdraw', 10000, 401),
('NEFT Transfer to Rahul', '2023-07-10', 'Transfer', 25000, 402),
('Car Loan EMI Payment', '2023-07-12', 'Withdraw', 15000, 403),
('FD Maturity Credit', '2023-07-15', 'Deposit', 1000000, 404);

-- ==========================================
-- LoanTypes and Loans
-- ==========================================
CREATE TABLE LoanTypes (
    Type_Name VARCHAR(30) PRIMARY KEY,
    Default_Interest DECIMAL(5,2) NOT NULL CHECK (Default_Interest >= 0)
);

INSERT INTO LoanTypes VALUES
('Home', 7.5),
('Personal', 10.2),
('Car', 8.75),
('Education', 6.9),
('Gold', 9.1);

CREATE TABLE Loan (
    Loan_ID INT PRIMARY KEY,
    Interest_Rate DECIMAL(5,2) NOT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    Loan_Type VARCHAR(30) NOT NULL,
    Loan_Amount DECIMAL(18,2) NOT NULL,
    StartDate DATE NOT NULL,
    CUS_ID INT NOT NULL,
    Branch_ID INT,
    FOREIGN KEY (CUS_ID) REFERENCES Customer(CUS_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (Branch_ID) REFERENCES Branch(Branch_ID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CHECK (Interest_Rate BETWEEN 0 AND 100),
    CHECK (Loan_Amount >= 0)
);

INSERT INTO Loan VALUES
(301, 7.50, 'Approved', 'Home', 2500000, '2022-05-10', 1, 101),
(302, 10.20, 'Pending', 'Personal', 500000, '2023-02-15', 2, 102),
(303, 8.75, 'Approved', 'Car', 800000, '2021-11-20', 3, 103),
(304, 6.90, 'Closed', 'Education', 0, '2020-07-01', 4, 104),
(305, 7.20, 'Approved', 'Home', 2000000, '2023-06-18', 5, 105);

-- ==========================================
-- Beneficiary
-- ==========================================
CREATE TABLE Beneficiary (
    ID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Branch_AccNo VARCHAR(50) NOT NULL UNIQUE,
    PhoneNo VARCHAR(15),
    CUS_ID INT,
    FOREIGN KEY (CUS_ID) REFERENCES Customer(CUS_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CHECK (PhoneNo IS NULL OR PhoneNo REGEXP '^[0-9]{10}$')
);

INSERT INTO Beneficiary VALUES
(201, 'Priya Reddy', 'SAV401', '9876000001', 1),
(202, 'Rahul Verma', 'SAV402', '9876000002', 2),
(203, 'Kiran Nair', 'SAV403', '9876000003', 3),
(204, 'Meena Iyer', 'SAV404', '9876000004', 4),
(205, 'Sameer Khan', 'SAV405', '9876000005', 5);

-- ==========================================
-- AuditLog
-- ==========================================
CREATE TABLE AuditLog (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Action VARCHAR(100),
    Details VARCHAR(255),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO AuditLog (Action, Details)
VALUES ('System Init', 'Initial data load completed');

-- ==========================================
-- Stored Procedures
-- ==========================================
DELIMITER //
CREATE PROCEDURE DepositAmount(IN acc_id INT, IN amt DECIMAL(18,2))
BEGIN
    DECLARE cnt INT DEFAULT 0;
    SELECT COUNT(*) INTO cnt FROM Account WHERE Account_ID = acc_id;
    IF cnt = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account Not Found';
    ELSE
        UPDATE Account SET Balance = Balance + amt WHERE Account_ID = acc_id;
        INSERT INTO Transactions (Description, Date_of_Transaction, Type, Amount, Account_ID)
        VALUES (CONCAT('Cash Deposit by acc ', acc_id), CURDATE(), 'Deposit', amt, acc_id);
    END IF;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE WithdrawAmount(IN acc_id INT, IN amt DECIMAL(18,2))
BEGIN
    DECLARE cnt INT DEFAULT 0;
    DECLARE bal DECIMAL(18,2);
    SELECT COUNT(*) INTO cnt FROM Account WHERE Account_ID = acc_id;
    IF cnt = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account Not Found';
    END IF;
    SELECT Balance INTO bal FROM Account WHERE Account_ID = acc_id;
    IF bal >= amt THEN
        UPDATE Account SET Balance = Balance - amt WHERE Account_ID = acc_id;
        INSERT INTO Transactions (Description, Date_of_Transaction, Type, Amount, Account_ID)
        VALUES (CONCAT('Cash Withdrawal by acc ', acc_id), CURDATE(), 'Withdraw', amt, acc_id);
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient Balance!';
    END IF;
END //
DELIMITER ;

-- ==========================================
-- Functions
-- ==========================================
DELIMITER //
CREATE FUNCTION GetCustomerAge(cus_dob DATE)
RETURNS INT DETERMINISTIC
RETURN TIMESTAMPDIFF(YEAR, cus_dob, CURDATE());
//
DELIMITER ;

DELIMITER //
CREATE FUNCTION GetTotalBalance(branch_id INT)
RETURNS DECIMAL(18,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(18,2);
    SELECT SUM(a.Balance) INTO total
    FROM Account a
    JOIN Customer c ON a.CUS_ID = c.CUS_ID
    WHERE c.Branch_ID = branch_id;
    RETURN IFNULL(total, 0);
END //
DELIMITER ;

-- ==========================================
-- Triggers
-- ==========================================
DELIMITER //
CREATE TRIGGER Loan_Status_Check
BEFORE UPDATE ON Loan
FOR EACH ROW
BEGIN
    IF NEW.Loan_Amount = 0 THEN
        SET NEW.Status = 'Closed';
    ELSE
        SET NEW.Status = 'Approved';
    END IF;
END //
DELIMITER ;

-- ==========================================
-- Views
-- ==========================================
CREATE VIEW BranchPerformance AS
SELECT b.Branch_ID, b.Branch_Name, GetTotalBalance(b.Branch_ID) AS TotalBalance
FROM Branch b;

CREATE VIEW CustomerLoanSummary AS
SELECT c.CUS_ID, c.Name, IFNULL(SUM(l.Loan_Amount),0) AS Total_Loan
FROM Customer c
LEFT JOIN Loan l ON c.CUS_ID = l.CUS_ID
GROUP BY c.CUS_ID, c.Name;

CREATE VIEW HighValueCustomers AS
SELECT
  c.CUS_ID,
  c.Name,
  (SELECT IFNULL(SUM(a.Balance),0) FROM Account a WHERE a.CUS_ID = c.CUS_ID) AS TotalBalance
FROM Customer c
WHERE
  (SELECT IFNULL(SUM(a2.Balance),0) FROM Account a2 WHERE a2.CUS_ID = c.CUS_ID) >
  (
    SELECT AVG(sum_bal) FROM (
        SELECT IFNULL(SUM(Balance),0) AS sum_bal FROM Account GROUP BY CUS_ID
    ) AS derived
  );

-- ==========================================
-- Verification Queries
-- ==========================================
SELECT COUNT(*) AS Branches FROM Branch;
SELECT COUNT(*) AS Customers FROM Customer;
SELECT COUNT(*) AS Accounts FROM Account;
SELECT COUNT(*) AS Loans FROM Loan;
SELECT COUNT(*) AS Beneficiaries FROM Beneficiary;
SELECT COUNT(*) AS Transactions FROM Transactions;
