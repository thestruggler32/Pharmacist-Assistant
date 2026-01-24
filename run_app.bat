@echo off
echo Starting AI Prescription Assistant...
echo Setting environment variables...
set DISABLE_MODEL_SOURCE_CHECK=True
set PYTHONIOENCODING=utf-8

echo Installing/Verifying dependencies...
pip install -r requirements.txt

echo.
echo ===================================================
echo  To enable 95%% accuracy, make sure MISTRAL_API_KEY 
echo  is set in your .env file!
echo ===================================================
echo.

echo Starting Flask Server...
python app.py
pause
