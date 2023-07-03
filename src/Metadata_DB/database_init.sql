CREATE USER IF NOT EXISTS 'metadata'@'localhost' IDENTIFIED BY 'root';
GRANT ALL PRIVILEGES ON *.* TO 'metadata'@'localhost'; -- For simplicity reasons we are granting user all privileges.
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS Metadata;