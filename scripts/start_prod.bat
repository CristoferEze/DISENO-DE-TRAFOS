@echo off
set PRODUCTION=1
if exist .venv\Scripts\python.exe (
  .\.venv\Scripts\python.exe src\main.py
) else (
  python src\main.py
)
