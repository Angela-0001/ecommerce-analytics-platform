@echo off
echo ===================================================
echo  E-COMMERCE ANALYTICS - Running All Scripts
echo ===================================================
echo.

echo Step 1: Generating Data...
cd /d "%~dp0python\data_generation"
python generate_ecommerce_data.py
if errorlevel 1 (
    echo ERROR: Data generation failed!
    pause
    exit /b 1
)
echo.

echo Step 2: Customer Segmentation...
cd /d "%~dp0python\analysis"
python customer_segmentation.py
if errorlevel 1 (
    echo ERROR: Customer segmentation failed!
    pause
    exit /b 1
)
echo.

echo Step 3: Sales Forecasting...
python sales_forecasting.py
if errorlevel 1 (
    echo ERROR: Sales forecasting failed!
    pause
    exit /b 1
)
echo.

echo Step 4: Export to Excel...
python export_to_excel.py
if errorlevel 1 (
    echo ERROR: Excel export failed!
    pause
    exit /b 1
)
echo.

echo ===================================================
echo  ALL ANALYTICS COMPLETE!
echo ===================================================
echo.
echo Check these folders for outputs:
echo  - data\sample\          (CSV files)
echo  - data\processed\       (Cleaned data + segments)
echo  - python\analysis\      (Charts and visualizations)
echo  - excel\ad_hoc_analysis\ (Excel workbooks)
echo.
pause
