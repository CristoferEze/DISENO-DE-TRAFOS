@echo off
echo Publicando instalador (usa el build ya generado)...
REM Este script llama al publish.bat de raíz (si existe), o incluye la lógica si prefieres.
if exist ..\publish.bat (
  cmd /c ..\publish.bat
) else (
  echo publish.bat original no encontrado. Asegurate de tener un instalador generado.
  exit /b 1
)
