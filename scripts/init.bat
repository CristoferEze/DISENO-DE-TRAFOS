@echo off
echo Creando entorno virtual .venv...
py -3.13 -m venv .venv 2>nul || py -3 -m venv .venv 2>nul || python -m venv .venv
if errorlevel 1 (
  echo Error creando .venv
  exit /b 1
)
echo Entorno virtual creado en .venv
