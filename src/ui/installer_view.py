# src/ui/installer_view.py
# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import threading

def _download_thread_target(window, download_function):
    """Función que se ejecuta en un hilo para descargar TinyTeX sin congelar la UI."""
    try:
        download_function()
        window.write_event_value('-DOWNLOAD_COMPLETE-', '')
    except Exception as e:
        window.write_event_value('-DOWNLOAD_ERROR-', str(e))

def show_installation_prompt():
    """Muestra un diálogo para confirmar si el usuario desea instalar TinyTeX."""
    # Intentamos usar una ventana; si falla (modo consola), caemos a input()
    try:
        choice = sg.popup_yes_no(
            "Se necesita instalar el motor LaTeX (TinyTeX) para generar reportes.\n"
            "Este proceso descargará aproximadamente 200-300 MB y puede tardar varios minutos.\n\n"
            "¿Desea continuar con la instalación?",
            title="Instalación requerida"
        )
        return choice == 'Yes'
    except Exception:
        resp_input = input("¿Desea continuar con la instalación? [y/N]: ").strip().lower()
        return resp_input == 'y'

def show_progress_window(download_function):
    """
    Muestra la ventana de progreso mientras se ejecuta la descarga en un hilo.
    Retorna el evento final ('-DOWNLOAD_COMPLETE-' o '-DOWNLOAD_ERROR-') y los valores.
    """
    layout = [
        [sg.Text("Instalando TinyTeX...")],
        [sg.Image(data=sg.DEFAULT_BASE64_LOADING_GIF, key='-GIF-')]
    ]
    progress_window = sg.Window("Instalación en Progreso", layout, modal=True, finalize=True)

    # Inicia el hilo de descarga, pasando la función real de descarga
    threading.Thread(target=_download_thread_target, args=(progress_window, download_function), daemon=True).start()

    final_event = None
    final_values = None

    while True:
        event, values = progress_window.read(timeout=100)
        try:
            progress_window['-GIF-'].update_animation(sg.DEFAULT_BASE64_LOADING_GIF, time_between_frames=100)
        except Exception:
            pass

        if event in (sg.WIN_CLOSED, '-DOWNLOAD_COMPLETE-', '-DOWNLOAD_ERROR-'):
            final_event = event
            final_values = values
            break

    progress_window.close()
    return final_event, final_values