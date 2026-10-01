-- ===========================================================================
-- Table: accounts
-- Run sequence: 1 of 5   Dependencies: none
-- Brokerage account directory: account_id (PK) + account_name.
-- ===========================================================================
BEGIN TRANSACTION;
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
	account_id INTEGER NOT NULL,
	account_name VARCHAR NOT NULL,
	PRIMARY KEY (account_id)
);
INSERT INTO accounts VALUES (1, 'Schwab Trading');
END TRANSACTION;
