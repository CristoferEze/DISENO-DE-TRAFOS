# src/setup/dependency_checker.py
import os
import sys
import pytinytex
from ui import installer_view

def _perform_download():
    """Función que encapsula la llamada a la descarga de TinyTeX."""
    pytinytex.download_tinytex(variation=2)

def ensure_tinytex_is_installed():
    """
    Verifica si TinyTeX está instalado y, si no, coordina el proceso de instalación
    usando la vista del instalador (UI) para la interacción con el usuario.
    """
    try:
        tinytex_path = pytinytex.get_tinytex_path()
        if os.path.exists(tinytex_path):
            # Ya está instalado, no hacemos nada.
            return
    except Exception:
        # No está instalado o no se pudo determinar la ruta.
        pass

    # 1. Preguntar al usuario si desea instalar (usando la vista)
    if not installer_view.show_installation_prompt():
        print("Instalación Cancelada: la aplicación se cerrará.")
        sys.exit(0)

    # 2. Mostrar la ventana de progreso (usando la vista)
    #    Le pasamos la función que debe ejecutar en segundo plano.
    event, values = installer_view.show_progress_window(_perform_download)

    # 3. Manejar el resultado
    if event == '-DOWNLOAD_ERROR-':
        error_message = values.get('-DOWNLOAD_ERROR-') if isinstance(values, dict) else str(values)
        print(f"Error Crítico de Instalación: No se pudo instalar TinyTeX.\nError: {error_message}", file=sys.stderr)
        sys.exit(1)
    
    if event != '-DOWNLOAD_COMPLETE-':
        print("La instalación no se completó. La aplicación se cerrará.", file=sys.stderr)
        sys.exit(1)

    print("Instalación de TinyTeX Completada. Ahora se verificarán los paquetes adicionales.")
