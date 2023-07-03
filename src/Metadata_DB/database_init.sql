CREATE DATABASE IF NOT EXISTS Metadata;
USE Metadata;
-- Leaving the table creation logic to sqlalchemy

CREATE USER IF NOT EXISTS 'metadata'@'localhost' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON Metadata.* TO 'metadata'@'localhost'; -- For simplicity reasons we are granting all privileges
FLUSH PRIVILEGES;