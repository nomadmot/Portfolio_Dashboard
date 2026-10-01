-- ===========================================================================
-- Table: securities
-- Run sequence: 2 of 5   Dependencies: none
-- Security directory: symbol (PK), security_name, security_type, associated_symbol.
-- ===========================================================================
BEGIN TRANSACTION;
DROP TABLE IF EXISTS securities;
CREATE TABLE securities (
	symbol VARCHAR NOT NULL,
	security_name VARCHAR NOT NULL,
	security_type VARCHAR NOT NULL,
	associated_symbol VARCHAR,
	PRIMARY KEY (symbol)
);
END TRANSACTION;
