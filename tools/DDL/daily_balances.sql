-- ===========================================================================
-- Table: daily_balances
-- Run sequence: 4 of 5   Dependencies: none
-- Ending balance per account per date: balance_date, account_id, balance.
-- ===========================================================================
BEGIN TRANSACTION;
DROP TABLE IF EXISTS daily_balances;
CREATE TABLE daily_balances (
	balance_date DATE,
	account_id BIGINT,
	balance DOUBLE
);
END TRANSACTION;
