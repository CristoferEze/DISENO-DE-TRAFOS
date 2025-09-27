# src/main.py
import sys
from setup.dependency_checker import ensure_tinytex_is_installed
from ui.app_view import Application

def main():
    """
    Punto de entrada principal de la aplicación.
    1. Verifica e instala las dependencias necesarias.
    2. Inicia la interfaz gráfica de usuario.
    """
    # Paso 1: Asegurarse de que TinyTeX (y otras futuras dependencias) esté listo.
    ensure_tinytex_is_installed()

    # Paso 2: Si la verificación fue exitosa, crear y correr la aplicación.
    app = Application()
    app.run()

if __name__ == "__main__":
    # Asegura que la UI se vea bien en diferentes DPIs (opcional pero recomendado)
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass  # Solo para Windows

    main()
    sys.exit(0)