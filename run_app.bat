@echo off
echo ===================================================
echo   AI PHARMACIST ASSISTANT - LAUNCHER
echo ===================================================

echo [1/3] Checking dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Setting up database...
python database\init_db.py
python database\load_all_medicines.py

echo.
echo [3/3] Starting Application...
echo.
echo Access the app at: http://localhost:5000/?user_id=pharma_001
echo.
python app.py
pause
