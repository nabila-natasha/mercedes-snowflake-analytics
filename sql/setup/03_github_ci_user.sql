/***************************************************************************************************
Project :   Mercedes-Benz Vehicle Analytics
Task    :   GitHub Actions Snowflake Service User
Day     :   2
Purpose :   Create dedicated Snowflake identity for GitHub Actions
***************************************************************************************************/
USE ROLE ACCOUNTADMIN;

ALTER SESSION SET QUERY_TAG =
'{"project":"mercedes","task":"github_ci_user","day":"2"}';


-- Create dedicated machine/service user
CREATE USER IF NOT EXISTS MERC_GITHUB_CI
    DEFAULT_ROLE = MERC_CI_CD
    DEFAULT_WAREHOUSE = TRANSFORM_WH
    MUST_CHANGE_PASSWORD = FALSE;

-- Assign CI/CD role
GRANT ROLE MERC_CI_CD
    TO USER MERC_GITHUB_CI;