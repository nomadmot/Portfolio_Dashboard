-- ===========================================================================
-- Table: market_holidays
-- Run sequence: 6 of 6   Dependencies: none
-- NYSE market holidays and early closes: Year, Date, Holiday, Status,
-- Close_Time, Notes.
-- ===========================================================================
BEGIN TRANSACTION;
DROP TABLE IF EXISTS market_holidays;
CREATE TABLE "main"."market_holidays" (
    "Year" INTEGER,
    "Date" DATE,
    "Holiday" VARCHAR,
    "Status" VARCHAR,
    "Close_Time" VARCHAR,
    "Notes" VARCHAR
);
END TRANSACTION;
