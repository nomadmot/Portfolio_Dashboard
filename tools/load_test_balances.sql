DROP TABLE "main"."daily_balances"
;
CREATE TABLE "main"."daily_balances" (
    "date" DATE DEFAULT NULL,
    "account_id" BIGINT DEFAULT NULL,
    "balance" DOUBLE DEFAULT NULL
);
INSERT INTO daily_balances
    SELECT date, 1, New_Balance
        FROM read_csv('test_daily_balances.csv');