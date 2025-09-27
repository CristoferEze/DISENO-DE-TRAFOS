@echo off
REM =================================================================
REM        SCRIPT DE PUBLICACION PARA GITHUB RELEASES
REM =================================================================
REM Este script automatiza la creacion de una nueva release en GitHub.
REM Prerrequisitos:
REM 1. GitHub CLI instalado (`winget install GitHub.cli`) y autenticado.
REM 2. Un archivo .env en la raiz con GITHUB_TOKEN=ghp_...
REM =================================================================

SET "REPO=CristoferEze/DISENO-DE-TRAFOS"
SET "SETUP_FILE=CalculadoraTransformadores_Setup.exe"

echo.
echo *** INICIANDO PROCESO DE PUBLICACION EN GITHUB ***
echo Repositorio: %REPO%
echo.

REM --- PASO 1: Obtener la version para la release ---
set /p VERSION_TAG="=> Por favor, introduce la etiqueta de la version (ej: v1.0.1): "
IF "%VERSION_TAG%"=="" (
    echo.
    echo *** ERROR: La etiqueta de la version no puede estar vacia. Abortando. ***
    exit /b 1
)

REM --- PASO 2: Cargar el token de GitHub desde .env ---
echo.
echo [1/4] Cargando token de GitHub desde .env...
IF NOT EXIST .env (
    echo *** ERROR: No se encuentra el archivo .env. Por favor, crealo con tu GITHUB_TOKEN. ***
    exit /b 1
)
FOR /F "tokens=1,2 delims==" %%A IN (.env) DO (
    IF "%%A"=="GITHUB_TOKEN" SET GITHUB_TOKEN=%%B
)
IF NOT DEFINED GITHUB_TOKEN (
    echo *** ERROR: No se encontro la variable GITHUB_TOKEN en el archivo .env. ***
    exit /b 1
)
echo    Token cargado.
echo.

REM --- PASO 3: Construir el instalador ---
echo [2/4] Ejecutando el script de compilacion (build.bat)...
call build.bat
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo *** ERROR: El script build.bat fallo. Abortando publicacion. ***
    exit /b 1
)
IF NOT EXIST %SETUP_FILE% (
    echo.
    echo *** ERROR: El archivo del instalador (%SETUP_FILE%) no fue encontrado despues de la compilacion. ***
    exit /b 1
)
echo    Compilacion completada.
echo.

REM --- PASO 4: Crear la Release en GitHub ---
echo [3/4] Creando la release %VERSION_TAG% en GitHub...
gh release create %VERSION_TAG% "%SETUP_FILE%" --repo %REPO% --title "Release %VERSION_TAG%" --notes "Lanzamiento automatico de la version %VERSION_TAG%."

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo *** ERROR: Falla al crear la release en GitHub. Comprueba tu token y la conexion. ***
    exit /b 1
)
echo    Release creada y archivo subido con exito.
echo.

echo [4/4] Limpiando el instalador local...
del %SETUP_FILE%
echo.

echo =================================================================
echo *** PUBLICACION COMPLETADA CON EXITO! ***
echo La version %VERSION_TAG% ya esta disponible en las Releases de tu repositorio.
echo https://github.com/%REPO%/releases
echo =================================================================
echo.
pause