-- Create the database
CREATE DATABASE BudgetApp;
USE BudgetApp;

-- Table for payment methods
CREATE TABLE PaymentMethods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    method_name VARCHAR(50) NOT NULL
);

-- Table for transactions
CREATE TABLE Transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('Earning', 'Expense') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    payment_method_id INT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (payment_method_id) REFERENCES PaymentMethods(id)
);