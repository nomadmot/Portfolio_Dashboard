DROP TABLE trades_new;

CREATE TABLE trades_new (
	id INTEGER NOT NULL, 
	account_id INTEGER NOT NULL, 
	symbol VARCHAR NOT NULL, 
	trade_date DATE NOT NULL, 
	trade_type VARCHAR NOT NULL, 
	quantity FLOAT NOT NULL, 
	price FLOAT NOT NULL, 
	fees FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_trade_type CHECK (trade_type IN ('BUY', 'SELL', 'TRAN', 'EXRC', 'EXPR', 'ASGN')), 
	FOREIGN KEY(account_id) REFERENCES accounts (id), 
	FOREIGN KEY(symbol) REFERENCES securities (symbol)
);