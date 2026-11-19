/*
=============================================================================
Populate Date Dimension
=============================================================================
Purpose: Generate date records from 2022-01-01 to 2025-12-31
=============================================================================
*/

USE ECommerceAnalytics;
GO

-- Populate date dimension for 4 years
DECLARE @StartDate DATE = '2022-01-01';
DECLARE @EndDate DATE = '2025-12-31';
DECLARE @CurrentDate DATE = @StartDate;

WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO dim_date (
        date_key,
        date,
        day_of_week,
        day_name,
        day_of_month,
        day_of_year,
        week_of_year,
        month,
        month_name,
        quarter,
        year,
        is_weekend,
        fiscal_year,
        fiscal_quarter
    )
    VALUES (
        CONVERT(INT, FORMAT(@CurrentDate, 'yyyyMMdd')),
        @CurrentDate,
        DATEPART(WEEKDAY, @CurrentDate),
        DATENAME(WEEKDAY, @CurrentDate),
        DAY(@CurrentDate),
        DATEPART(DAYOFYEAR, @CurrentDate),
        DATEPART(WEEK, @CurrentDate),
        MONTH(@CurrentDate),
        DATENAME(MONTH, @CurrentDate),
        DATEPART(QUARTER, @CurrentDate),
        YEAR(@CurrentDate),
        CASE WHEN DATEPART(WEEKDAY, @CurrentDate) IN (1, 7) THEN 1 ELSE 0 END,
        -- Fiscal year starts in February
        CASE WHEN MONTH(@CurrentDate) >= 2 THEN YEAR(@CurrentDate) ELSE YEAR(@CurrentDate) - 1 END,
        CASE 
            WHEN MONTH(@CurrentDate) IN (2, 3, 4) THEN 1
            WHEN MONTH(@CurrentDate) IN (5, 6, 7) THEN 2
            WHEN MONTH(@CurrentDate) IN (8, 9, 10) THEN 3
            ELSE 4
        END
    );
    
    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END

-- Mark major US holidays
UPDATE dim_date SET is_holiday = 1, holiday_name = 'New Year''s Day' 
WHERE month = 1 AND day_of_month = 1;

UPDATE dim_date SET is_holiday = 1, holiday_name = 'Independence Day' 
WHERE month = 7 AND day_of_month = 4;

UPDATE dim_date SET is_holiday = 1, holiday_name = 'Christmas' 
WHERE month = 12 AND day_of_month = 25;

-- Black Friday (4th Friday of November - simplified)
UPDATE dim_date SET is_holiday = 1, holiday_name = 'Black Friday'
WHERE month = 11 AND day_name = 'Friday' 
AND day_of_month BETWEEN 23 AND 29;

-- Cyber Monday (Monday after Black Friday)
UPDATE dim_date SET is_holiday = 1, holiday_name = 'Cyber Monday'
WHERE month = 11 AND day_name = 'Monday' 
AND day_of_month BETWEEN 26 AND 30;

GO

PRINT 'Date dimension populated';
PRINT 'Total records: ' + CAST((SELECT COUNT(*) FROM dim_date) AS VARCHAR(10));
