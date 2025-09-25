# src/ui/app_view.py
# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import os
import sys
import traceback
import tempfile
from pylatex import Document
from pdf2image import convert_from_path

from core.engine import DisenoTransformador
from core.database import acero_electrico_db, conexiones_normalizadas
from ui.report_builder import generate_full_report_document

class Application:
    def __init__(self):
        sg.theme('DarkBlue3')
        self.last_report_path = None
        self.window = sg.Window('Calculadora de Diseño (v14.1 - Corrección Final)', self._crear_layout())

    def _crear_container_datos_principales(self):
        tipos_de_acero = list(acero_electrico_db.keys())
        # Valor por defecto seguro para conexiones
        conn_default = conexiones_normalizadas[0] if conexiones_normalizadas else ''
        return sg.Frame('Datos Principales del Transformador', [
            [sg.Text('Tipo:', size=(18,1)),
             sg.DropDown(['trifasico', 'monofasico'], default_value='trifasico', key='-TIPO-', enable_events=True)],
            [sg.Text('Potencia Nominal (kVA):', size=(18,1)), sg.Input('25', key='-S_KVA-')],
            [sg.Text('Tensión Primario (V):', size=(18,1)), sg.Input('10500', key='-E1-')],
            [sg.Text('Tensión Secundario (V):', size=(18,1)), sg.Input('400', key='-E2-')],
            [sg.Text('Frecuencia (Hz):', size=(18,1)), sg.Input('60', key='-FREQ-')],
            # Conexión como Combo (visible sólo para trifásico)
            [sg.Text('Conexión:', size=(18,1), key='-LBL-CONN-'),
             sg.Combo(conexiones_normalizadas, default_value=conn_default, key='-CONN-', readonly=True, size=(22,1))],
            # TAPs (visible sólo para trifásico)
            [sg.Text('TAPs (%):', size=(18,1), key='-LBL-TAPS-'),
             sg.Input('2.5, 5.0', key='-TAPS-', tooltip='Separados por coma. Dejar vacío si no hay.')],
            [sg.Text('Tipo de Acero:', size=(18,1)), sg.DropDown(tipos_de_acero, default_value='30M5', key='-ACERO-')]
        ])

    def _crear_container_parametros(self):
        params_diseno = sg.Frame('Parámetros de Diseño', [[sg.Text('Relación de Ventana:', size=(18,1)), sg.Input('3.0', key='-RW-')]])
        params_avanzados = sg.Frame('Parámetros Avanzados (Opcional)', [[sg.Text('Inducción B (kGauss):', size=(18,1)), sg.Input(key='-B_MANUAL-')], [sg.Text('Constante C:', size=(18,1)), sg.Input(key='-C_MANUAL-')], [sg.Text('Coeficiente Kc:', size=(18,1)), sg.Input(key='-KC_MANUAL-')]])
        return params_diseno, params_avanzados

    def _crear_layout(self):
        main_container = self._crear_container_datos_principales()
        design_container, advanced_container = self._crear_container_parametros()
        columna_entradas = [[main_container], [design_container], [advanced_container], [sg.Button('Calcular Diseño', button_color=('white', 'green'), font=('Helvetica', 12)), sg.Button('Ver Archivo', key='-EXPORT-', disabled=True, font=('Helvetica', 12)), sg.Push(), sg.Button('Salir', font=('Helvetica', 12))]]
        
        image_element = [sg.Image(key='-IMAGE-')]

        columna_resultados = [
            [sg.Text('Procedimiento de Cálculo', font=('Helvetica', 16))],
            [sg.HorizontalSeparator()],
            [sg.Column(
                [image_element],
                size=(750, 600),
                scrollable=True,
                vertical_scroll_only=False,
                key='-COL-IMAGE-'
            )]
        ]
        return [[sg.Column(columna_entradas), sg.VSeperator(), sg.Column(columna_resultados)]]

    def _render_latex_to_file(self, latex_doc, final_png_path, dpi=200):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                pdf_basename = os.path.join(temp_dir, 'reporte')
                latex_doc.generate_pdf(pdf_basename, clean_tex=True, compiler='pdflatex')
                pdf_path = f"{pdf_basename}.pdf"
                images = convert_from_path(pdf_path, dpi=dpi)
                if images:
                    images[0].save(final_png_path, 'PNG')
                    return final_png_path
                else:
                    raise RuntimeError("pdf2image no pudo convertir el archivo PDF.")
            except Exception as e:
                print("Error al renderizar con PyLaTeX:", file=sys.stderr)
                traceback.print_exc()
                sg.popup_error("Error de LaTeX", f"No se pudo compilar el documento.\nError: {e}\n\nRevise la terminal.")
                return None

    def _manejar_calculo(self, values):
        try:
            self.last_report_path = None
            self.window['-EXPORT-'].update(disabled=True)
            
            # --- CORRECCIÓN ---
            # Las líneas que buscaban y borraban '-GRAPH-' han sido eliminadas.
            # Limpiamos la imagen actualizando su contenido con una ruta vacía.
            self.window['-IMAGE-'].update(filename='')
            # --- FIN DE LA CORRECCIÓN ---

            params = { 'tipo': values['-TIPO-'], 'S': float(values['-S_KVA-']), 'E1': float(values['-E1-']), 'E2': float(values['-E2-']), 'f': float(values['-FREQ-']), 'acero': values['-ACERO-'], 'conn': values['-CONN-'], 'taps': [float(t.strip()) for t in values['-TAPS-'].split(',')] if values['-TAPS-'].strip() else [], 'rel_rw': float(values['-RW-']), 'b_man': float(values['-B_MANUAL-']) if values['-B_MANUAL-'] else None, 'c_man': float(values['-C_MANUAL-']) if values['-C_MANUAL-'] else None, 'kc_man': float(values['-KC_MANUAL-']) if values['-KC_MANUAL-'] else None }

            diseno = DisenoTransformador(**params)
            diseno.ejecutar_calculo_completo()
            
            latex_doc = generate_full_report_document(diseno)
            
            export_dir = "exports"
            os.makedirs(export_dir, exist_ok=True)
            s_kva = values['-S_KVA-'].replace('.','p')
            filename = f"Reporte_{s_kva}kVA.png"
            filepath = os.path.join(export_dir, filename)
            
            sg.popup_quick_message('Compilando con PyLaTeX y generando imagen...', background_color='blue', text_color='white')
            saved = self._render_latex_to_file(latex_doc, filepath)

            if saved:
                self.window['-IMAGE-'].update(filename=saved)
                self.window.refresh()
                self.window['-COL-IMAGE-'].contents_changed()
                
                self.last_report_path = saved
                self.window['-EXPORT-'].update(disabled=False, text="Ver Archivo")

        except ValueError as e:
            # Log en terminal y volcado de traceback para facilitar depuración
            print("Error de Entrada: valores numéricos inválidos.", file=sys.stderr)
            traceback.print_exc()
            sg.popup_error('Error de Entrada', 'Asegúrese de que todos los campos numéricos contengan valores válidos. Revise la terminal para más detalles.')
        except Exception as e:
            # Log completo en terminal para excepciones inesperadas
            print("Error inesperado durante el cálculo:", file=sys.stderr)
            traceback.print_exc()
            sg.popup_error('Ocurrió un Error', f'No se pudo completar el proceso.\n\nDetalle: {e}')
            
    def _manejar_exportacion(self):
        if not self.last_report_path or not os.path.exists(self.last_report_path):
            sg.popup_error("Archivo de reporte no encontrado.", "Por favor, genere un cálculo primero.")
            return
        try:
            full_path = os.path.abspath(self.last_report_path)
            respuesta = sg.popup_yes_no( "El reporte ya fue guardado en:", f"\n{full_path}\n", "¿Desea abrir la carpeta contenedora?", title="Archivo de Reporte" )
            if respuesta == 'Yes':
                os.startfile(os.path.dirname(full_path))
        except Exception as e:
            sg.popup_error("Error", f"No se pudo abrir la carpeta.\n\nDetalle: {e}")

    def run(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Salir'):
                break

            # Mostrar/ocultar campos según tipo (trifásico/monofásico)
            if event == '-TIPO-':
                es_trifasico = (values.get('-TIPO-') == 'trifasico')
                # Actualizar visibilidad de los elementos de conexión y taps
                try:
                    self.window['-LBL-CONN-'].update(visible=es_trifasico)
                    self.window['-CONN-'].update(visible=es_trifasico)
                    self.window['-LBL-TAPS-'].update(visible=es_trifasico)
                    self.window['-TAPS-'].update(visible=es_trifasico)
                except Exception:
                    # Si las claves no existen por alguna razón, ignorar el fallo de visibilidad
                    pass
                continue

            elif event == 'Calcular Diseño':
                # Si es monofásico, ignorar los valores de conexión y taps
                if values.get('-TIPO-') == 'monofasico':
                    values['-CONN-'] = ''
                    values['-TAPS-'] = ''
                self._manejar_calculo(values)

            elif event == '-EXPORT-':
                self._manejar_exportacion()
        self.window.close()