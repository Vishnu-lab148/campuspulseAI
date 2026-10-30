-- Optional dated aggregate history table for Progress trends in Db2 mode.
CREATE TABLE CAMPUSPULSE_HISTORY (
    RECORD_DATE DATE NOT NULL PRIMARY KEY,
    AVG_ATTENDANCE DECIMAL(5,2) NOT NULL,
    AVG_SCORE DECIMAL(5,2) NOT NULL
);
