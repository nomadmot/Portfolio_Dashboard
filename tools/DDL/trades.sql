-- ===========================================================================
-- Table: trades
-- Run sequence: 3 of 5   Dependencies: accounts, securities
-- Stock/option/cash transactions; FK -> accounts + securities; CHECK on trade_type.
-- ===========================================================================
BEGIN TRANSACTION;
DROP TABLE IF EXISTS trades;
CREATE TABLE trades (
	id INTEGER NOT NULL,
	account_id INTEGER NOT NULL,
	symbol VARCHAR NOT NULL,
	trade_date DATE NOT NULL,
	trade_type VARCHAR NOT NULL,
	quantity DOUBLE NOT NULL,
	price DOUBLE NOT NULL,
	fees DOUBLE NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT chk_trade_type CHECK (trade_type IN ('BUY', 'SELL', 'TRAN', 'EXRC', 'EXPR', 'ASGN', 'DEP', 'WDL', 'DIV', 'INT', 'FEE', 'TAX', 'SPLT', 'JRNL')),
	FOREIGN KEY (account_id) REFERENCES accounts (account_id),
	FOREIGN KEY (symbol) REFERENCES securities (symbol)
);
END TRANSACTION;
