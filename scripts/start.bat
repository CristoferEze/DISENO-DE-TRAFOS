@echo off
if exist .venv\Scripts\python.exe (
  .\.venv\Scripts\python.exe src\main.py
) else (
  echo .venv no encontrado. Ejecuta 'scripts\init' y 'scripts\install' primero.
  exit /b 1
)
