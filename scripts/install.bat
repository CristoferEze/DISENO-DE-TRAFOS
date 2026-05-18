@echo off
if exist .venv\Scripts\python.exe (
  echo Instalando dependencias en .venv...
  .\.venv\Scripts\python.exe -m pip install --upgrade pip
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
  echo .venv no encontrado. Ejecuta 'scripts\init' primero.
  exit /b 1
)
echo Dependencias instaladas.
