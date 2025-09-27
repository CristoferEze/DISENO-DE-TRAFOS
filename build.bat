@echo off
REM =================================================================
REM        SCRIPT DE COMPILACION PARA CALCULADORA DE TRANSFORMADORES
REM =================================================================
REM Este script automatiza los siguientes pasos:
REM 1. Limpia las compilaciones anteriores.
REM 2. Activa el entorno virtual de Python.
REM 3. Ejecuta PyInstaller para empaquetar la aplicación.
REM 4. Ejecuta NSIS para crear el instalador final.
REM =================================================================

SET "APP_NAME=CalculadoraTransformadores"
SET "MAIN_SCRIPT=src/main.py"
REM ICON removed per request
SET "NSIS_SCRIPT=installer.nsi"
SET "VENV_PATH=.\venv\Scripts\activate"

echo.
echo *** INICIANDO PROCESO DE COMPILACION PARA %APP_NAME% ***
echo.

REM --- PASO 1: Limpiar compilaciones anteriores ---
echo [1/4] Limpiando compilaciones anteriores...
IF EXIST build rmdir /s /q build
IF EXIST dist rmdir /s /q dist
IF EXIST "%APP_NAME%.spec" del "%APP_NAME%.spec"
echo    Limpieza completada.
echo.

REM --- PASO 2: Activar el entorno virtual ---
echo [2/4] Activando el entorno virtual de Python...
call %VENV_PATH%
echo    Entorno virtual activado.
echo.

REM --- PASO 3: Ejecutar PyInstaller ---
echo [3/4] Ejecutando PyInstaller para empaquetar la aplicacion...
REM Se recomienda usar --onedir para instaladores NSIS, es mas robusto.
pyinstaller --name "%APP_NAME%" --windowed --onedir %MAIN_SCRIPT%

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo *** ERROR: PyInstaller fallo. Abortando compilacion. ***
    exit /b 1
)
echo    PyInstaller completado con exito.
echo.

REM --- PASO 4: Ejecutar NSIS ---
echo [4/4] Ejecutando NSIS para crear el instalador...
REM Asegurate de que NSIS este en el PATH de tu sistema.
makensis %NSIS_SCRIPT%

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo *** ERROR: NSIS fallo. Abortando compilacion. ***
    exit /b 1
)
echo    NSIS completado con exito.
echo.

echo.
echo =================================================================
echo *** COMPILACION COMPLETADA CON EXITO! ***
echo Tu instalador se encuentra en la raiz del proyecto.
echo =================================================================
echo.

pause