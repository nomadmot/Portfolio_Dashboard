-- ===========================================================================
-- Table: notes
-- Run sequence: 5 of 5   Dependencies: none
-- Free-text notes: account_id, note_date, symbol, content.
-- ===========================================================================
BEGIN TRANSACTION;
DROP TABLE IF EXISTS notes;
CREATE TABLE notes (
	account_id INTEGER NOT NULL,
	note_date DATETIME NOT NULL,
	symbol VARCHAR NOT NULL,
	content TEXT NOT NULL
);
END TRANSACTION;
