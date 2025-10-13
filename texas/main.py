# Modulo: principal
# -----------------------------------------------------------------
# Este es el script principal.
# Modifique los valores en la seccion "CONFIGURACION DEL DISENO"
# y luego ejecute el programa (Ctrl+R).
# -----------------------------------------------------------------

import calc_nucleus, calc_windings, calc_core_weights, calc_losses, calc_daily_perf

class DesignData:
    def _num_esc(self, Ab):
        if Ab <= 12.5: return 1; 
        elif Ab <= 50: return 2; 
        elif Ab <= 125: return 3
        elif Ab <= 250: return 4; 
        elif Ab <= 600: return 5; 
        return 6

# =================================================================
#               >>>>> CONFIGURACION DEL DISENO <<<<<
#             Modifique los valores en esta seccion
# =================================================================
d = DesignData()

# -- Datos Generales del Transformador --
d.S = 25
d.f = 60
d.fases = 3
d.refrig = 'ONAN'
d.material_conductor = 'Cobre'
d.acero = 'M-5'
d.conn = 'Dyn5'
d.cut_type = 'Recto' # Opciones: 'Recto', 'Diagonal'
d.E1_linea = 10000
d.E2_linea = 400
d.taps_pct = []
d.rel_rw = 3

# -- Opciones de Calculo y Valores Manuales --
d.usar_valores_opcionales = False # Poner en True para usar el valor de abajo
d.Pf_opcional = None # Ejemplo: Perdidas especificas en el hierro (W/kg)

# -- Ciclo de Carga para Rendimiento Diario --
ciclos_disponibles = {
    'Industrial (24h)': [(1.0, 8), (0.75, 8), (0.50, 8)],
    'Residencial': [(0.8, 6), (0.4, 10), (0.1, 8)],
    'Personalizado': [(1.0, 8), (0.5, 12), (0.0, 4)]
}
d.ciclo_carga_nombre = 'Residencial'
d.ciclo_carga = ciclos_disponibles[d.ciclo_carga_nombre]
d.redondear_2_decimales = True
# =================================================================
#          FIN DE LA SECCION DE CONFIGURACION
# =================================================================


def mostrar_datos_de_entrada(d):
    print("="*30); print("    DATOS INICIALES DE CALCULO"); print("="*30)
    print("Potencia (S): {} kVA".format(getattr(d, 'S', 'N/A')))
    print("Fases: {}".format(getattr(d, 'fases', 'N/A')))
    print("Tipo de Corte: {}".format(getattr(d, 'cut_type', 'N/A')))
    print("Ciclo Diario: {}".format(getattr(d, 'ciclo_carga_nombre', 'N/A')))
    if getattr(d, 'usar_valores_opcionales', False):
        print("MODO: Usando valores opcionales.")
    print("="*30 + "\n")

def mostrar_resultados_completos(d):
    def f(val, dec=2): return round(val, dec) if isinstance(val, (int, float)) else "N/A"
    
    print("\n\n" + "="*30); print("  INFORME COMPLETO DEL DISENO"); print("="*30)
    
    print("\n# --- PARAMETROS BASE DE CALCULO ---")
    print("Constante de Flujo C: {}".format(f(getattr(d, 'C', 0), 4)))
    print("Constante de Ventana Kc: {}".format(f(getattr(d, 'Kc_original', 0), 4)))
    print("Coeficiente Plenitud Kr (Kf): {}".format(f(getattr(d, 'Kr_original', 0), 4)))
    
    # << CORRECCION: Se anaden Flujo, An, Ab y D aqui >>
    print("\n# --- NUCLEO Y VENTANA ---")
    print("Flujo Magnetico (kilolineas): {}".format(f(getattr(d, 'flujo_kilolineas', 0))))
    print("Area Neta An (cm2): {}".format(f(getattr(d, 'An', 0))))
    print("Area Bruta Ab (cm2): {}".format(f(getattr(d, 'Ab', 0))))
    print("Diametro Circunscrito D (cm): {}".format(f(getattr(d, 'D', 0))))
    print("Area de Ventana Aw (cm2): {}".format(f(getattr(d, 'Aw', 0))))
    print("Altura de Ventana b (cm): {}".format(f(getattr(d, 'b', 0))))
    print("Distancia entre columnas M (cm): {}".format(f(getattr(d, 'M', 0))))
    print("Ancho de Ventana c (cm): {}".format(f(getattr(d, 'c', 0))))
    print("Ancho de Ventana c' (cm): {}".format(f(getattr(d, 'c_prima', 0))))
    
    if getattr(d, 'anchos', None):
        print("\n# --- DIMENSIONES DE ESCALONES ---")
        for i in range(len(d.anchos)):
            print("  Escalon {}: Ancho a{} = {} cm, Espesor e{} = {} cm".format(i+1, i+1, f(d.anchos[i]), i+1, f(d.espesores[i])))
    
    print("\n# --- DEVANADOS, CORRIENTES Y CONDUCTORES ---")
    print("Espiras Primario N1: {}".format(getattr(d, 'N1_fase', 0)))
    print("Espiras Secundario N2: {}".format(getattr(d, 'N2_fase', 0)))
    print("Corriente Fase Primario I1 (A): {}".format(f(getattr(d, 'I1_fase_nom', 0))))
    print("Corriente Fase Secundario I2 (A): {}".format(f(getattr(d, 'I2_fase', 0))))
    print("Seccion Conductor Primario s1 (mm2): {}".format(f(getattr(d, 's1', 0))))
    print("Seccion Conductor Secundario s2 (mm2): {}".format(f(getattr(d, 's2', 0))))
    print("Calibre AWG Primario: {}".format(getattr(d, 'awg1', 'N/A')))
    print("Calibre AWG Secundario: {}".format(getattr(d, 'awg2', 'N/A')))

    print("\n# --- PESO DE COBRE (CALCULO FISICO) ---")
    print("Radio medio rm (cm): {}".format(f(getattr(d, 'rm', 0))))
    print("Longitud media espira lm (m): {}".format(f(getattr(d, 'lm', 0))))
    print("Longitud total bobinado primario Lb1 (m): {}".format(f(getattr(d, 'Lb1', 0))))
    print("Peso bobinado primario Qb1 (kg): {}".format(f(getattr(d, 'Qb1', 0))))
    print("Longitud total bobinado secundario Lb2 (m): {}".format(f(getattr(d, 'Lb2', 0))))
    print("Peso bobinado secundario Qb2 (kg): {}".format(f(getattr(d, 'Qb2', 0))))
    print("Qc Total (Suma Fisica) (kg): {}".format(f(getattr(d, 'Qc_total', 0))))

    print("\n# --- PESO DE HIERRO (LAMINACIONES FISICAS) ---")
    if getattr(d, 'peso_por_escalon', None):
        for pe in d.peso_por_escalon:
            print("  Escalon {}: Peso total = {} kg".format(pe.get('escalon'), f(pe.get('peso_total_escalon',0))))
            for det in pe.get('detalles', []):
                extra = ", Area={} cm2".format(f(det['area_cm2'])) if 'area_cm2' in det else ""
                print("    - {}: {} pz, Peso={} kg{}".format(det.get('nombre'), det.get('num_piezas'), f(det.get('peso_kg')), extra))
    print("Qr Total (Suma Fisica) (kg): {}".format(f(getattr(d, 'Qr', 0))))

    print("\n# --- PERDIDAS (FORMULAS EMPIRICAS) ---")
    print("Peso Cobre (Empirico) para perdidas (kg): {}".format(f(getattr(d, 'Qc_used_for_losses', 0))))
    print("Perdidas Cobre Wc (W): {}".format(f(getattr(d, 'Wc', 0))))
    print("Peso Hierro (Empirico) para perdidas (kg): {}".format(f(getattr(d, 'Qf_used_for_losses', 0))))
    print("Perdidas Hierro Especificas Pf (W/kg): {}".format(f(getattr(d, 'Pf', 0), 4)))
    print("Perdidas Hierro Wf (W): {}".format(f(getattr(d, 'Wf', 0))))

    print("\n# --- RENDIMIENTO (PLENA CARGA) ---")
    print("Rendimiento a plena carga (%): {}".format(f(getattr(d, 'rendimiento', 0))))
    
    if getattr(d, 'detalles_ciclo', None):
        print("\n# --- DESEMPENO DIARIO (Ciclo: {}) ---".format(getattr(d, 'ciclo_carga_nombre', 'N/A')))
        print("  Resumen Diario:")
        print("    Energia Salida Total (kWh/d): {}".format(f(getattr(d, 'energia_salida_total', 0))))
        print("    Energia Perdida Cobre Total (kWh/d): {}".format(f(getattr(d, 'energia_perdida_cobre_total', 0))))
        print("    Energia Perdida Hierro Total (kWh/d): {}".format(f(getattr(d, 'energia_perdida_hierro_total', 0))))
        print("    Rendimiento Diario (%): {}".format(f(getattr(d, 'rendimiento_diario', 0), 4)))
    
    print("\n" + "="*30); print("         FIN DEL INFORME"); print("="*30)

# -----------------------------------------------------------------
#                  EJECUCION DEL PROGRAMA
# -----------------------------------------------------------------
mostrar_datos_de_entrada(d)
print("Iniciando calculos...")
try:
    calc_nucleus.run(d); print("1. Nucleo y Ventana... OK")
    calc_windings.run(d); print("2. Devanados y TAPs... OK")
    calc_core_weights.run(d); print("3. Peso del Nucleo... OK")
    calc_losses.run(d); print("4. Perdidas y Rendimiento... OK")
    calc_daily_perf.run(d); print("5. Rendimiento Diario... OK")
    print("\nCalculos finalizados con exito.")
    mostrar_resultados_completos(d)
except Exception as e:
    print("\n!!! ERROR DURANTE EL CALCULO: {}".format(e))