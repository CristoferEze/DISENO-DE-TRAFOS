@echo off
if exist .venv\Scripts\python.exe (
  .\.venv\Scripts\python.exe -m pip freeze > requirements.txt
) else (
  python -m pip freeze > requirements.txt
)
echo requirements.txt actualizado.
