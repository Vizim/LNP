LOAD DATA
INFILE '/opt/oracle/temp/fake_data1.csv'
INTO TABLE FAKE_DATA
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
    Name                CHAR,
    Email               CHAR,
    "Phone Number"      CHAR,
    Address             CHAR,
    Birthdate           DATE "YYYY-MM-DD",
    Company             CHAR,
    "Credit Card Number" CHAR,
    "Favorite Color"    CHAR,
    Website             CHAR
)
