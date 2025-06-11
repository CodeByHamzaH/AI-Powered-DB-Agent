-- =============================
--  OfficeDB Schema Definition
-- =============================

-- 1. Create Database
CREATE DATABASE IF NOT EXISTS OfficeDB;
USE OfficeDB;

-- 2. Create Table: Departments
CREATE TABLE IF NOT EXISTS Departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100)
);

-- 3. Create Table: Employees
CREATE TABLE IF NOT EXISTS Employees (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    hire_date DATE NOT NULL,
    job_title VARCHAR(50),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

-- 4. Create Table: Payroll
CREATE TABLE IF NOT EXISTS Payroll (
    payroll_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    salary DECIMAL(10, 2) NOT NULL CHECK (salary >= 0),
    bonus DECIMAL(10, 2) DEFAULT 0.00 CHECK (bonus >= 0),
    pay_date DATE NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);
