@echo off
REM =================================================================
REM        SCRIPT DE PUBLICACION (SOLO PUBLICACION)
REM =================================================================
REM Este script TOMA un instalador YA CREADO y lo publica en GitHub Releases.
REM NO COMPILA EL PROYECTO. Debes ejecutar 'build.bat' primero.
REM
REM Prerrequisitos:
REM 1. Ejecutar 'build.bat' para crear el archivo del instalador.
REM 2. GitHub CLI instalado (`winget install GitHub.cli`) y autenticado.
REM 3. Un archivo .env en la raiz con GITHUB_TOKEN y APP_VERSION.
REM =================================================================

SET "REPO=CristoferEze/DISENO-DE-TRAFOS"
SET "SETUP_FILE=CalculadoraTransformadores_Setup.exe"

echo.
echo *** INICIANDO PROCESO DE PUBLICACION EN GITHUB ***
echo Repositorio: %REPO%
echo.

REM --- PASO 1: Cargar configuracion desde .env (Token y Version) ---
echo [1/3] Cargando configuracion desde .env...
IF NOT EXIST .env (
    echo *** ERROR: No se encuentra el archivo .env. ***
    exit /b 1
)

REM Limpiar variables previas para asegurar una lectura limpia
SET "GITHUB_TOKEN="
SET "VERSION_TAG="

REM Leer el archivo .env linea por linea
FOR /F "usebackq tokens=1,2 delims==" %%A IN (".env") DO (
    IF "%%A"=="GITHUB_TOKEN" SET "GITHUB_TOKEN=%%B"
    IF "%%A"=="APP_VERSION" SET "VERSION_TAG=%%B"
)

REM Validar que las variables se hayan cargado
IF NOT DEFINED GITHUB_TOKEN (
    echo *** ERROR: No se encontro la variable GITHUB_TOKEN en el archivo .env. ***
    exit /b 1
)
IF NOT DEFINED VERSION_TAG (
    echo *** ERROR: No se encontro la variable APP_VERSION en el archivo .env. ***
    exit /b 1
)
echo    Token cargado.
echo    Version a publicar: %VERSION_TAG%
echo.

REM --- PASO 2: Verificar que el instalador YA EXISTA ---
echo [2/3] Verificando que el archivo '%SETUP_FILE%' exista...
IF NOT EXIST %SETUP_FILE% (
    echo.
    echo *** ERROR: El archivo del instalador no fue encontrado. ***
    echo Por favor, ejecuta 'build.bat' primero para compilar la aplicacion.
    exit /b 1
)
echo    Archivo de instalacion encontrado y listo para publicar.
echo.

REM --- PASO 3: Crear la Release en GitHub ---
echo [3/3] Creando y subiendo la release %VERSION_TAG% a GitHub...
gh release create %VERSION_TAG% "%SETUP_FILE%" --repo %REPO% --title "Release %VERSION_TAG%" --notes "Lanzamiento de la version %VERSION_TAG%."

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo *** ERROR: Falla al crear la release en GitHub. Comprueba tu token y la conexion. ***
    exit /b 1
)
echo    Release creada y archivo subido con exito.
echo.

REM --- Limpieza Post-Publicacion ---
echo Limpiando el instalador local...
del %SETUP_FILE%
echo.

echo =================================================================
echo *** PUBLICACION COMPLETADA CON EXITO! ***
echo La version %VERSION_TAG% ya esta disponible en las Releases de tu repositorio.
echo https://github.com/%REPO%/releases
echo =================================================================
echo.
pause