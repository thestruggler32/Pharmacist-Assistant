@echo off
echo Starting Full Stack Pharmacy App...

echo Starting Backend (Flask)...
start "Flask Backend" cmd /k "cd backend && python app.py"

echo Starting Frontend (Vite)...
start "Vite Frontend" cmd /k "cd frontend && npm run dev"

echo ===================================================
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:5000
echo ===================================================
pause
