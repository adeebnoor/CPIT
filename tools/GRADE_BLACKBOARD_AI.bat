@echo off
setlocal
if "%~1"=="" (
  echo Drag the Blackboard submissions ZIP onto this file.
  pause
  exit /b 1
)
cd /d "%~dp0.."
python tools\grade_ai_assignments.py "%~1"
echo.
echo Results are in cpit455_ai_grades\
pause
