; installer.nsi - Script para la Calculadora de Transformadores

; --- Información General ---
Name "Calculadora de Transformadores"
OutFile "CalculadoraTransformadores_Setup.exe"
InstallDir "$PROGRAMFILES64\CalculadoraTransformadores"
RequestExecutionLevel admin

; --- Interfaz Gráfica ---
!include "MUI2.nsh"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "Spanish"

; --- Sección de Instalación ---
Section "Calculadora de Transformadores (Requerido)"
  SetOutPath $INSTDIR
  
  ; Copia todo el contenido de la carpeta generada por PyInstaller (--onedir)
  File /r "dist\CalculadoraTransformadores\*.*"

  WriteUninstaller "$INSTDIR\uninstall.exe"
  CreateDirectory "$SMPROGAccess-group\Calculadora de Transformadores"
  CreateShortCut "$SMPROGAccess-group\Calculadora de Transformadores\Calculadora.lnk" "$INSTDIR\CalculadoraTransformadores.exe" ""
  CreateShortCut "$DESKTOP\Calculadora de Transformadores.lnk" "$INSTDIR\CalculadoraTransformadores.exe" ""

  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraTransformadores" "DisplayName" "Calculadora de Transformadores"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraTransformadores" "UninstallString" '"$INSTDIR\uninstall.exe"'
SectionEnd

; --- Sección del Desinstalador ---
Section "Uninstall"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGAccess-group\Calculadora de Transformadores\Calculadora.lnk"
  Delete "$DESKTOP\Calculadora de Transformadores.lnk"
  RMDir "$SMPROGAccess-group\Calculadora de Transformadores"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\CalculadoraTransformadores"
SectionEnd