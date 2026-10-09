@echo off
@chcp 65001 >nul
cd /d "%~dp0"
echo ===================================================
echo   Fahim - Arabic Learning Platform Backend
echo   Starting API on http://127.0.0.1:8000
echo   API Docs: http://127.0.0.1:8000/docs
echo ===================================================

set PYTHONPATH=C:\Users\athom\AppData\Roaming\Python\Python313\site-packages;%~dp0

if exist "C:\Users\athom\AppData\Local\Programs\Python\Python313\python.exe" (
    "C:\Users\athom\AppData\Local\Programs\Python\Python313\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
) else (
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
)
pause
