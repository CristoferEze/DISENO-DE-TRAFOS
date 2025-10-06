# src/ui/app_view.py
# -*- coding: utf-8 -*-
import PySimpleGUI as sg
import os
import sys
import traceback
import tempfile
from pylatex import Document
import fitz  # PyMuPDF (motor de renderizado integrado)
import pytinytex
import io
from PIL import Image
import subprocess

from core.engine import DisenoTransformador
from core.database import acero_electrico_db, conexiones_normalizadas
from ui.report_builder import generate_full_report_document

# Plotters del módulo nucleus_and_window (se co-localizaron ahí)
from design_phases.nucleus_and_window import core_plotter
from design_phases.core_and_lamination_weights.lamination_plotters import generate_plot 

class Application:
    def __init__(self):
        sg.theme('DarkBlue3')
        self.last_report_path = None
        self.window = sg.Window('Calculadora de Diseño (v14.1 - Corrección Final)', self._crear_layout())

    def _crear_container_datos_principales(self):
        # Crear mapeo de designaciones antiguas a claves de base de datos
        tipos_de_acero_display = []
        self.acero_map = {}  # mapeo de display -> clave de DB
        for clave, datos in acero_electrico_db.items():
            designacion = datos['designacion_antigua']
            tipos_de_acero_display.append(designacion)
            self.acero_map[designacion] = clave
        
        conn_default = 'Dyn5'  # Cambiar conexión por defecto
        return sg.Frame('Datos Principales del Transformador', [
            [sg.Text('Tipo:', size=(18,1)),
             sg.DropDown(['trifasico', 'monofasico'], default_value='trifasico', key='-TIPO-', enable_events=True)],
            [sg.Text('Potencia Nominal (kVA):', size=(18,1)), sg.Input('25', key='-S_KVA-')],
            [sg.Text('Tensión Primario (V):', size=(18,1)), sg.Input('10000', key='-E1-')],
            [sg.Text('Tensión Secundario (V):', size=(18,1)), sg.Input('400', key='-E2-')],
            [sg.Text('Frecuencia (Hz):', size=(18,1)), sg.Input('60', key='-FREQ-')],
            [sg.Text('Conexión:', size=(18,1), key='-LBL-CONN-'),
             sg.Combo(conexiones_normalizadas, default_value=conn_default, key='-CONN-', readonly=True, size=(22,1))],
            [sg.Text('TAPs (%):', size=(18,1), key='-LBL-TAPS-'),
             sg.Input('', key='-TAPS-', tooltip='Ejemplo: 2.5, 5.0, 7.5 (separados por coma). Dejar vacío si no hay TAPs.')],
            [sg.Text('Tipo de Acero:', size=(18,1)), sg.DropDown(tipos_de_acero_display, default_value='35M6', key='-ACERO-')],
            [sg.Text('Tipo de Corte:', size=(18,1)), sg.DropDown(['Recto', 'Diagonal'], default_value='Recto', key='-CUT_TYPE-')],
            [sg.Checkbox('Redondear a 2 decimales', default=True, key='-REDONDEAR-')]
        ])

    def _crear_container_parametros(self):
        # --- INICIO DE LA MODIFICACIÓN ---
        params_diseno = sg.Frame('Parámetros de Diseño', [
            [sg.Text('Relación de Ventana:', size=(18,1)), sg.Input('3.0', key='-RW-')],
            [sg.Text('Ciclo de Carga (24h):', size=(18,1), tooltip='Formato: carga_frac,horas; carga_frac,horas; ...\nEj: 1.25,2; 1,6; 0.5,8; 0.25,4; 0,4')],
            [sg.Input('1.25,2; 1,6; 0.5,8; 0.25,4; 0,4', key='-CICLO_CARGA-')]
        ])
        # --- FIN DE LA MODIFICACIÓN ---
        
        # Tab único de valores opcionales consolidado
        params_opcionales = sg.Frame('Valores Opcionales', [
            [sg.Checkbox('Usar valores opcionales', default=False, key='-USAR_OPCIONALES-', enable_events=True)],
            [sg.HorizontalSeparator()],
            [sg.Text('Parámetros de Diseño Opcionales:', font=('Helvetica', 10, 'bold'))],
            [sg.Text('Inducción B (kGauss):', size=(20,1)), sg.Input(key='-B_OPCIONAL-', disabled=True)],
            [sg.Text('Constante C:', size=(20,1)), sg.Input(key='-C_OPCIONAL-', disabled=True)],
            [sg.Text('Coeficiente Kc:', size=(20,1)), sg.Input(key='-KC_OPCIONAL-', disabled=True)],
            [sg.Text('Densidad J (A/mm²):', size=(20,1)), sg.Input(key='-J_OPCIONAL-', disabled=True)],
            [sg.HorizontalSeparator()],
            [sg.Text('Parámetros de Pérdidas Manuales:', font=('Helvetica', 10, 'bold'))],
            [sg.Text('Pérdidas Cobre Pc (W/kg):', size=(20,1)), sg.Input(key='-PC_MANUAL-', disabled=True, tooltip='Valor manual para pérdidas específicas en el cobre')],
            [sg.Text('Pérdidas Hierro Pf (W/kg):', size=(20,1)), sg.Input(key='-PF_MANUAL-', disabled=True, tooltip='Valor manual para pérdidas específicas en el hierro')],
            [sg.HorizontalSeparator()],
            [sg.Text('Parámetros de Tabla Opcionales:', font=('Helvetica', 10, 'bold'))],
            [sg.Text('Factor de Apilamiento (fa):', size=(20,1)), sg.Input(key='-FA_OPCIONAL-', disabled=True)],
            [sg.Text('Coeficiente Kr:', size=(20,1)), sg.Input(key='-KR_OPCIONAL-', disabled=True)],
            [sg.Text('Pérdidas Hierro Pf (W/kg):', size=(20,1)), sg.Input(key='-PF_OPCIONAL-', disabled=True, tooltip='Valor de tabla para pérdidas específicas en el hierro')],
            [sg.Text('Densidad Acero (kg/cm³):', size=(20,1)), sg.Input(key='-RHO_ACERO_OPCIONAL-', disabled=True)],
            [sg.Text('Densidad Cobre (kg/cm³):', size=(20,1)), sg.Input(key='-RHO_COBRE_OPCIONAL-', disabled=True)]
        ])
        return params_diseno, params_opcionales

    def _crear_layout(self):
        main_container = self._crear_container_datos_principales()
        design_container, opcionales_container = self._crear_container_parametros()
        
        # Crear pestañas (solo Principal y Opcionales)
        tab_group = sg.TabGroup([
            [sg.Tab('Principal', [[main_container], [design_container]], key='-TAB_PRINCIPAL-')],
            [sg.Tab('Opcionales', [[opcionales_container]], key='-TAB_OPCIONALES-')]
        ])
        
        columna_entradas = [
            [sg.Text('Universidad nacional del centro del Perú', font=('Helvetica', 14, 'bold'))],
            [sg.Text('"Facultad de ingenieria electrica y electronica"', font=('Helvetica', 12))],
            [tab_group],
            [sg.Button('Calcular Diseño', button_color=('white', 'green'), font=('Helvetica', 12)), sg.Button('Ver Archivo', key='-EXPORT-', disabled=True, font=('Helvetica', 12)), sg.Push(), sg.Button('Salir', font=('Helvetica', 12))]
        ]
        
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

    def _render_latex_to_file(self, latex_doc, temp_dir, final_png_path, dpi=200):
        """
        Renderiza el documento LaTeX usando el directorio temp_dir como cwd para pdflatex.
        Guarda el PNG resultante en final_png_path.
        """
        try:
            pdf_basename = os.path.join(temp_dir, 'reporte')
            
            compiler_path = pytinytex.get_pdf_latex_engine()
            if not compiler_path or not os.path.exists(compiler_path):
                raise RuntimeError("El compilador de TinyTeX no fue encontrado. Intente reiniciar la aplicación.")

            tex_path = f"{pdf_basename}.tex"
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(latex_doc.dumps())  # obtiene el contenido .tex

            cmd = [compiler_path, "--interaction=nonstopmode", tex_path]
            proc = subprocess.run(cmd, cwd=temp_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output_bytes = proc.stdout or b""
            output_text = output_bytes.decode("utf-8", errors="replace")

            if proc.returncode != 0:
                raise RuntimeError(f"pdflatex returned non-zero exit status {proc.returncode}.\nOutput:\n{output_text}")

            pdf_path = f"{pdf_basename}.pdf"
            if not os.path.exists(pdf_path):
                raise RuntimeError(f"El archivo PDF no fue generado. Output:\n{output_text}")

            # Renderizar todas las páginas y unirlas verticalmente
            doc = fitz.open(pdf_path)
            page_images = []
            try:
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(dpi=dpi)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    page_images.append(img)
            finally:
                doc.close()

            if not page_images:
                raise RuntimeError("No se encontraron páginas en el PDF para renderizar.")

            total_height = sum(img.height for img in page_images)
            max_width = max(img.width for img in page_images)
            
            stitched_image = Image.new('RGB', (max_width, total_height), 'white')
            current_y = 0
            for img in page_images:
                stitched_image.paste(img, (0, current_y))
                current_y += img.height

            stitched_image.save(final_png_path, "PNG")

            return final_png_path
        except Exception as e:
            print("Error al renderizar con PyLaTeX/TinyTeX:", file=sys.stderr)
            traceback.print_exc()
            print(f"Error de LaTeX: No se pudo compilar o renderizar el documento. Error: {e}", file=sys.stderr)
            return None

    def _manejar_calculo(self, values):
        try:
            self.last_report_path = None
            self.window['-EXPORT-'].update(disabled=True)
            self.window['-IMAGE-'].update(filename='')

            # --- AÑADIR PARSEO DEL CICLO DE CARGA ---
            ciclo_str = values.get('-CICLO_CARGA-', '') or ''
            ciclo_carga = []
            if ciclo_str.strip():
                pares = [p for p in ciclo_str.split(';') if p.strip()]
                for par in pares:
                    try:
                        carga, horas = par.split(',')
                        ciclo_carga.append((float(carga.strip()), float(horas.strip())))
                    except Exception:
                        # ignorar pares mal formateados
                        continue

            # Convertir la designación mostrada a la clave de base de datos
            acero_seleccionado = values['-ACERO-']
            acero_clave = self.acero_map.get(acero_seleccionado, acero_seleccionado)
            
            params = {
                'tipo': values['-TIPO-'],
                'S': float(values['-S_KVA-']),
                'E1': float(values['-E1-']),
                'E2': float(values['-E2-']),
                'f': float(values['-FREQ-']),
                'acero': acero_clave,
                'conn': values['-CONN-'],
                'taps': [float(t.strip()) for t in values['-TAPS-'].split(',')] if values['-TAPS-'].strip() else [],
                'rel_rw': float(values['-RW-']),
                'b_man': None,  # Campos manuales eliminados, ahora solo se usan opcionales
                'c_man': None,
                'kc_man': None,
                'ciclo_carga': ciclo_carga,
                'cut_type': values.get('-CUT_TYPE-', 'Recto'),
                'redondear_2_decimales': values.get('-REDONDEAR-', False),
                'usar_valores_opcionales': values.get('-USAR_OPCIONALES-', False),
                'b_opcional': float(values['-B_OPCIONAL-']) if values['-B_OPCIONAL-'] else None,
                'c_opcional': float(values['-C_OPCIONAL-']) if values['-C_OPCIONAL-'] else None,
                'kc_opcional': float(values['-KC_OPCIONAL-']) if values['-KC_OPCIONAL-'] else None,
                'j_opcional': float(values['-J_OPCIONAL-']) if values['-J_OPCIONAL-'] else None,
                'fa_opcional': float(values['-FA_OPCIONAL-']) if values['-FA_OPCIONAL-'] else None,
                'kr_opcional': float(values['-KR_OPCIONAL-']) if values['-KR_OPCIONAL-'] else None,
                'pf_opcional': float(values['-PF_OPCIONAL-']) if values['-PF_OPCIONAL-'] else None,
                'rho_acero_opcional': float(values['-RHO_ACERO_OPCIONAL-']) if values['-RHO_ACERO_OPCIONAL-'] else None,
                'rho_cobre_opcional': float(values['-RHO_COBRE_OPCIONAL-']) if values['-RHO_COBRE_OPCIONAL-'] else None,
                'pc_manual': float(values['-PC_MANUAL-']) if values['-PC_MANUAL-'] else None,
                'pf_manual': float(values['-PF_MANUAL-']) if values['-PF_MANUAL-'] else None
            }

            diseno = DisenoTransformador(**params)
            diseno.ejecutar_calculo_completo()
            
            export_dir = "exports"
            os.makedirs(export_dir, exist_ok=True)
            s_kva = values['-S_KVA-'].replace('.','p')
            filename = f"Reporte_{s_kva}kVA.png"
            filepath = os.path.join(export_dir, filename)

            # Orquestar creación de archivos temporales (imágenes y .tex) en un único temp_dir
            sg.popup_quick_message('Generando gráficos y compilando reporte...', background_color='blue', text_color='white')
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generar imágenes en temp_dir y guardar nombres/rutas en el objeto diseno.
                # Soportamos plotters que devuelvan una sola ruta (str) o una lista de rutas.
                core_paths = core_plotter.generate_core_plot(diseno, output_dir=temp_dir)
                if isinstance(core_paths, list):
                    diseno.core_plot_paths = core_paths
                    diseno.core_plot_path = core_paths[-1] if core_paths else None
                    diseno.core_plot_filename = os.path.basename(diseno.core_plot_path) if diseno.core_plot_path else None
                else:
                    diseno.core_plot_paths = [core_paths] if core_paths else []
                    diseno.core_plot_path = core_paths
                    diseno.core_plot_filename = os.path.basename(core_paths) if core_paths else None

                # Las imágenes de laminación ahora se generan en la fase de cálculo (calculation.run).
                # Aquí solo recogemos las rutas que quedaron registradas en diseno.peso_por_escalon.
                if hasattr(diseno, 'peso_por_escalon'):
                    lam_paths = [s.get('plot_path') for s in diseno.peso_por_escalon if s.get('plot_path')]
                    diseno.lamination_plot_paths = lam_paths
                    diseno.lamination_plot_path = lam_paths[-1] if lam_paths else None
                    diseno.lamination_plot_filename = os.path.basename(diseno.lamination_plot_path) if diseno.lamination_plot_path else None
                else:
                    diseno.lamination_plot_paths = []
                    diseno.lamination_plot_path = None
                    diseno.lamination_plot_filename = None
    
                # Generar el documento LaTeX (el renderer preferirá los nombres de archivo relativos)
                # Pasar el directorio temporal para que los plotters escriban dentro de él
                latex_doc = generate_full_report_document(diseno, work_dir=temp_dir)

                # Renderizar usando temp_dir como cwd para pdflatex y guardar PNG final en exports
                saved = self._render_latex_to_file(latex_doc, temp_dir, filepath)

                if saved:
                    # Cargar bytes de la imagen desde disco y actualizar el elemento Image de PySimpleGUI
                    with open(saved, 'rb') as f:
                        img_bytes = f.read()
                    self.window['-IMAGE-'].update(data=img_bytes)
                    self.window.refresh()
                    self.window['-COL-IMAGE-'].contents_changed()
                    
                    self.last_report_path = saved
                    self.window['-EXPORT-'].update(disabled=False, text="Ver Archivo")

        except ValueError as e:
            print("Error de Entrada: valores numéricos inválidos.", file=sys.stderr)
            traceback.print_exc()
            print('Error de Entrada: Asegúrese de que todos los campos numéricos contengan valores válidos. Revise la terminal para más detalles.', file=sys.stderr)
        except Exception as e:
            print("Error inesperado durante el cálculo:", file=sys.stderr)
            traceback.print_exc()
            print(f'Ocurrió un Error: No se pudo completar el proceso. Detalle: {e}', file=sys.stderr)
            
    def _manejar_exportacion(self):
        if not self.last_report_path or not os.path.exists(self.last_report_path):
            print("Archivo de reporte no encontrado. Por favor, genere un cálculo primero.", file=sys.stderr)
            return
        try:
            full_path = os.path.abspath(self.last_report_path)
            respuesta = sg.popup_yes_no( "El reporte ya fue guardado en:", f"\n{full_path}\n", "¿Desea abrir la carpeta contenedora?", title="Archivo de Reporte" )
            if respuesta == 'Yes':
                os.startfile(os.path.dirname(full_path))
        except Exception as e:
            print(f"No se pudo abrir la carpeta. Detalle: {e}", file=sys.stderr)

    def run(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Salir'):
                break

            if event == '-TIPO-':
                es_trifasico = (values.get('-TIPO-') == 'trifasico')
                try:
                    self.window['-LBL-CONN-'].update(visible=es_trifasico)
                    self.window['-CONN-'].update(visible=es_trifasico)
                    self.window['-LBL-TAPS-'].update(visible=es_trifasico)
                    self.window['-TAPS-'].update(visible=es_trifasico)
                except Exception:
                    pass
                continue
                
            elif event == '-USAR_OPCIONALES-':
                # Habilitar/deshabilitar campos opcionales según el checkbox
                usar_opcionales = values.get('-USAR_OPCIONALES-', False)
                try:
                    # Campos de parámetros de diseño
                    self.window['-B_OPCIONAL-'].update(disabled=not usar_opcionales)
                    self.window['-C_OPCIONAL-'].update(disabled=not usar_opcionales)
                    self.window['-KC_OPCIONAL-'].update(disabled=not usar_opcionales)
                    self.window['-J_OPCIONAL-'].update(disabled=not usar_opcionales)
                    # Campos de pérdidas manuales
                    self.window['-PC_MANUAL-'].update(disabled=not usar_opcionales)
                    self.window['-PF_MANUAL-'].update(disabled=not usar_opcionales)
                    # Campos de parámetros de tabla
                    self.window['-FA_OPCIONAL-'].update(disabled=not usar_opcionales)
                    self.window['-KR_OPCIONAL-'].update(disabled=not usar_opcionales)
                    self.window['-PF_OPCIONAL-'].update(disabled=not usar_opcionales)
                    self.window['-RHO_ACERO_OPCIONAL-'].update(disabled=not usar_opcionales)
                    self.window['-RHO_COBRE_OPCIONAL-'].update(disabled=not usar_opcionales)
                except Exception:
                    pass
                continue

            elif event == 'Calcular Diseño':
                if values.get('-TIPO-') == 'monofasico':
                    values['-CONN-'] = ''
                    values['-TAPS-'] = ''
                self._manejar_calculo(values)

            elif event == '-EXPORT-':
                self._manejar_exportacion()
        self.window.close()