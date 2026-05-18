# Modulo: principal
# -----------------------------------------------------------------
# Este es el script principal.
# Modifique los valores en la seccion "CONFIGURACION DEL DISENO"
# y luego ejecute el programa (Ctrl+R).
# -----------------------------------------------------------------

import calc_nucleus, calc_windings, calc_core_weights, calc_losses, calc_daily_perf, math

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
d.cut_type = 'Diagonal' # Opciones: 'Recto', 'Diagonal'
d.E1_linea = 10500
d.E2_linea = 400
# Sin taps (el usuario pidió sin taps)
d.taps_pct = []
d.conn = 'Dyn5'  # Conexión dada en la transcripción
d.rel_rw = 3

# -- Opciones de Calculo y Valores Manuales --
d.usar_valores_opcionales = False # Poner en True para usar el valor de abajo
d.Pf_opcional = None    # Valor manual de Pf (prioridad alta)
d.Pc_opcional = None    # Valor manual de Pc (pérdidas cobre)
d.B_opcional = None   # Inducción B (kGauss)
d.J_opcional = None   # Densidad de corriente J (A/mm2)
d.fa_opcional = 0.975  # Factor de apilamiento fa (opcional por defecto solicitado)
d.C_opcional = None   # Constante de flujo C
d.Kc_opcional = None  # Constante Kc (ventana)
d.Kr_opcional = 0.825  # Coeficiente Kr/Kf (Kf) - valor opcional por defecto solicitado
d.rho_acero_opcional = None  # Densidad acero (kg/cm3)
d.rho_cobre_opcional = None  # Densidad cobre (kg/cm3)
d.espesor_lamina_mm_opcional = 0.30  # Espesor de lamina (mm) según M-5 0.30 mm
d.acero_opcional = None  # Clave de acero alternativa (ej. 'M-6')

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
    def fv(val, dec=2): return round(val, dec) if isinstance(val, (int, float)) else "N/A"
    print("\n\n" + "="*30)
    print("  EXAMEN - INFORME DEL DISEÑO")
    print("="*30)
    
    print("\n1. Datos de tablas")
    print("Se establecen los parámetros base para el diseño:")
    print("Densidad de flujo (B): {} gauss ({} T).".format(fv(getattr(d, 'B_kgauss', 0)*1000, 0), fv(getattr(d, 'B_tesla', 0), 2)))
    print("Densidad de corriente (J): {} A/mm².".format(fv(getattr(d, 'J', 0), 2)))
    print("Factores de diseño: Kf = {} y Kc = {}.".format(fv(getattr(d, 'Kr_original', getattr(d, 'Kr', 0)), 3), fv(getattr(d, 'Kc_original', getattr(d, 'Kc', 0)), 2)))

    print("\n2. Cálculos realizados")
    print("a) Flujo magnético (Phi)")
    print("Se utiliza una fórmula empírica basada en la potencia (S) y la frecuencia (f):")
    print("Phi = {} * sqrt({} / {}) * 10^6 = {} klineas".format(fv(getattr(d, 'C', 0), 4), getattr(d, 'S', 0), getattr(d, 'f', 0), fv(getattr(d, 'flujo_kilolineas', getattr(d, 'flujo', 0)/1000), 2)))

    print("\nb) Área del hierro")
    print("Área neta (An): Relación entre el flujo y la densidad de flujo.")
    print("An = {} / {} = {} cm²".format(fv(getattr(d, 'flujo_kilolineas', 0), 2), fv(getattr(d, 'B_kgauss', 0), 2), fv(getattr(d, 'An', 0), 2)))
    print("Área bruta (Ab): Considerando el factor de apilamiento.")
    print("Ab = {} / {} = {} cm²".format(fv(getattr(d, 'An', 0), 2), fv(getattr(d, 'fa_original', 0), 3), fv(getattr(d, 'Ab', 0), 2)))

    print("\nc) Dimensiones del núcleo")
    print("Se determinan los diámetros y anchos de las láminas para aproximar la sección circular del núcleo:")
    print("Diámetro (D):")
    # Mostrar siempre Kr/Kf original con 3 decimales para evitar confusión por redondeos
    kr_val = getattr(d, 'Kr_original', getattr(d, 'Kr', 0))
    print("D = 2 * sqrt({} / (pi * {})) = {} cm".format(fv(getattr(d, 'An', 0), 2), fv(kr_val, 3), fv(getattr(d, 'D', 0), 2)))
    print("Anchos de lámina:")
    if getattr(d, 'anchos', None):
        for i in range(len(d.anchos)):
            factor = d.anchos[i] / d.D if d.D else 0
            print("a{} = {}({}) = {} cm".format(i+1, fv(factor, 3), fv(d.D, 2), fv(d.anchos[i], 2)))

        # Desarrollo paso a paso de los cálculos de a_i y e_i (para trazabilidad)
        print("\nDesarrollo de cálculos de a_i y e_i:")
        suma_previos = 0.0
        for i in range(len(d.anchos)):
            ancho_actual = d.anchos[i]
            factor = ancho_actual / d.D if d.D else 0.0
            a_calc = factor * d.D
            sqrt_term = math.sqrt(d.D**2 - ancho_actual**2) if d.D > ancho_actual else 0.0
            if i == 0:
                e_calc = sqrt_term / 2.0
                print(f"a{i+1} = {factor:.3f} * D = {a_calc:.3f} cm")
                print(f"e{i+1} = sqrt(D^2 - a{i+1}^2) / 2 = {sqrt_term:.3f} / 2 = {e_calc:.3f} cm")
            else:
                e_calc = (sqrt_term - suma_previos) / 2.0
                prevs_str = ' + '.join([f"{d.espesores[k]:.3f}" for k in range(i)])
                print(f"a{i+1} = {factor:.3f} * D = {a_calc:.3f} cm")
                print(f"e{i+1} = (sqrt(D^2 - a{i+1}^2) - 2({prevs_str})) / 2 = ({sqrt_term:.3f} - {suma_previos:.3f}) / 2 = {e_calc:.3f} cm")
            suma_previos += 2.0 * d.espesores[i]
    
    print("\ne) Espesores y dimensionamiento del núcleo y la ventana")
    print("Espesores del paquete:")
    if getattr(d, 'espesores', None):
        suma_previos = 0
        for i in range(len(d.espesores)):
            ancho_actual = d.anchos[i] if d.anchos else 0
            if i == 0:
                print("e1 = sqrt({}^2 - {}^2) / 2 = {} cm".format(fv(getattr(d, 'D', 0), 2), fv(ancho_actual, 2), fv(d.espesores[i], 2)))
            else:
                ancho_prev = d.anchos[i-1] if d.anchos else 0
                suma_str = " + ".join(["{}".format(fv(d.espesores[k], 2)) for k in range(i)])
                print("e{} = (sqrt({}^2 - {}^2) - 2({})) / 2 = {} cm".format(i+1, fv(getattr(d, 'D', 0), 2), fv(ancho_actual, 2), suma_str, fv(d.espesores[i], 2)))
                
    Aw_m2 = getattr(d, 'Aw', 0)
    print("Área de la ventana (Aw):")
    constante_ventana = 2.22 if getattr(d, 'fases', 3) == 1 else 3.33
    print("Aw = ({} * 10^8) / ({} * {} * {} * {} * {} * {}) = {} cm²".format(getattr(d, 'S', 0)*1000, constante_ventana, getattr(d, 'f', 0), fv(getattr(d, 'B_kgauss', 0)*1000, 0), fv(getattr(d, 'Kc_original', 0), 2), fv(getattr(d, 'J', 0), 2), fv(getattr(d, 'An', 0), 2), fv(Aw_m2, 2)))
    
    print("Ancho del núcleo (b):")
    rel_rw = getattr(d, 'rel_rw', 3)
    b_val = getattr(d, 'b', 0)
    print("b = sqrt({} * {}) = {} cm".format(rel_rw, fv(Aw_m2, 2), fv(b_val, 2)))
    
    print("Distancia entre centros de columnas (M):")
    M_val = getattr(d, 'M', (Aw_m2 / b_val + d.D) if b_val else 0)
    print("M = {} / {} + {} = {} cm".format(fv(Aw_m2, 2), fv(b_val, 2), fv(getattr(d, 'D', 0), 2), fv(M_val, 2)))
    
    print("Ancho de la ventana (c):")
    c_val = getattr(d, 'c', M_val - getattr(d, 'D', 0))
    print("c = {} - {} = {} cm".format(fv(M_val, 2), fv(getattr(d, 'D', 0), 2), fv(c_val, 2)))

    print("\nd) Tensiones y TAPs (Regulación)")
    print("Tensión prim. por derivaciones:")
    if getattr(d, 'tap_data', None):
        for pct, data in sorted(d.tap_data.items(), reverse=True):
            signo = "+" if pct > 0 else ""
            print("  Tap {}{}%: V_linea = {} V | V_fase = {} V".format(signo, pct, fv(data['Vlinea'], 1), fv(data['Vfase'], 1)))

    print("\ne) Número de espiras")
    print("Bobinado secundario (N2):")
    print("N2 = ({} * 10^8) / (4.44 * {} * {} * {}) = {} espiras".format(fv(getattr(d, 'E2_fase', 0), 0), getattr(d, 'f', 0), fv(getattr(d, 'B_kgauss', 0)*1000, 0), fv(getattr(d, 'An', 0), 2), int(getattr(d, 'N2_fase', 0))))
    print("Bobinado primario por derivaciones (N1):")
    if getattr(d, 'tap_data', None):
        for pct, data in sorted(d.tap_data.items(), reverse=True):
            signo = "+" if pct > 0 else ""
            print("  N1 ({}{}%) = ({} / {}) * {} = {} espiras".format(signo, pct, fv(data['Vfase'], 1), fv(getattr(d, 'E2_fase', 0), 0), int(getattr(d, 'N2_fase', 0)), data['N_espiras']))

    print("\nf) Corrientes admisibles")
    print("En el bobinado secundario (I2):")
    S_dev_VA = getattr(d, 'S', 0) * 1000
    if getattr(d, 'fases', 3) == 3:
        S_dev_VA = (getattr(d, 'S', 0) * 1000) / 3
    print("I2 = {} / {} = {} A".format(S_dev_VA, fv(getattr(d, 'E2_fase', 0), 0), fv(getattr(d, 'I2_fase', 0), 2)))
    print("En el bobinado primario (I1):")
    if getattr(d, 'tap_data', None):
        for pct, data in sorted(d.tap_data.items(), reverse=True):
            signo = "+" if pct > 0 else ""
            print("  I1 ({}{}%) = {} / {} = {} A".format(signo, pct, S_dev_VA, fv(data['Vfase'], 1), fv(data['I1'], 2)))

    print("\ng) Calibres de los conductores")
    print("Sección del conductor secundario (s2):")
    print("s2 = {} / {} = {} mm²".format(fv(getattr(d, 'I2_fase', 0), 2), fv(getattr(d, 'J', 0), 2), fv(getattr(d, 's2', 0), 2)))
    if getattr(d, 'awg2', '') == 'Pletina':
        print(" -> Pletina de Cobre: w = {} mm, t = {} mm | Scu = {} mm²".format(fv(getattr(d, 'pletina2_w', 0), 2), fv(getattr(d, 'pletina2_t', 0), 2), fv(getattr(d, 's2_real', 0), 2)))
    else:
        print(" -> AWG {}".format(getattr(d, 'awg2', 'N/A')))
        
    print("Sección del conductor primario (s1) usando I1 máxima:")
    print("s1 = {} / {} = {} mm²".format(fv(getattr(d, 'I1_max', 0), 2), fv(getattr(d, 'J', 0), 2), fv(getattr(d, 's1', 0), 2)))
    print(" -> AWG {}  (Diametro: {} mm)".format(getattr(d, 'awg1', 'N/A'), fv(getattr(d, 'diam_c1_usado', 0), 2)))

    print("\nh) Bobinas y aislamiento")
    print("Bobina de B.T. (Baja Tensión)")
    b_val_mm = fv(getattr(d, 'b', 0) * 10, 1)
    d_c_bt = getattr(d, 'd_c_bt', 6.5)
    e_y_bt = getattr(d, 'e_y_bt', 1.5)
    margen_total_bt = getattr(d, 'margen_total_bt', 8.0)
    print("Altura de la bobina: Hb2 = {} - 2({}) = {} mm".format(b_val_mm, margen_total_bt, fv(getattr(d, 'Hb2', 0), 1)))
    print("Número de espiras por capa: Ne/cb2 = {} / {} = {} espiras / capa".format(fv(getattr(d, 'Hb2', 0), 1), fv(getattr(d, 'ancho_c2_usado', 5.8), 2), int(getattr(d, 'Ne_cb2', 0))))
    capas_completas_bt = math.floor(getattr(d, 'Nc_b2', 0))
    sobrante_bt = int(getattr(d, 'N2_fase', 0)) - capas_completas_bt * int(getattr(d, 'Ne_cb2', 0))
    print("Número de capas por bobina: Nc/b2 = {} / {} = {} -> {} capas / ({} * {} + 1 * {})".format(int(getattr(d, 'N2_fase', 0)), int(getattr(d, 'Ne_cb2', 0)), fv(getattr(d, 'Nc_b2', 0), 2), math.ceil(getattr(d, 'Nc_b2', 0)), capas_completas_bt, int(getattr(d, 'Ne_cb2', 0)), sobrante_bt))
    print("Tensión de impulso (Vc2) = 2 * ({} / {}) * 0.25 = {} kV".format(getattr(d, 'BIL2', 10), math.ceil(getattr(d, 'Nc_b2', 0) or 1), fv(getattr(d, 'Vc2', 0), 2)))
    print("Aislamiento entre capas: delta_e = 3.5 * ({} / 40.0) = {} mm".format(fv(getattr(d, 'Vc2', 0), 2), fv(getattr(d, 'delta_s2', 0), 2)))

    print("\nBobina de M.T. (Media Tensión)")
    d_c_mt = getattr(d, 'd_c_mt', 13.0)
    e_y_mt = getattr(d, 'e_y_mt', 2.0)
    margen_total_mt = getattr(d, 'margen_total_mt', 15.0)
    print("Altura de la bobina: Hb1 = {} - 2({}) = {} mm".format(b_val_mm, margen_total_mt, fv(getattr(d, 'Hb1', 0), 1)))
    print("Número de espiras por capa: Ne/cb1 = {} / {} = {} espiras / capa".format(fv(getattr(d, 'Hb1', 0), 1), fv(getattr(d, 'diam_c1_usado', 0.63), 2), int(getattr(d, 'Ne_cb1', 0))))
    capas_completas_mt = math.floor(getattr(d, 'Nc_b1', 0))
    sobrante_mt = int(getattr(d, 'N1_fase', 0)) - capas_completas_mt * int(getattr(d, 'Ne_cb1', 0))
    print("Número de capas por bobina: Nc/b1 = {} / {} = {} -> {} capas / ({} * {} + 1 * {})".format(int(getattr(d, 'N1_fase', 0)), int(getattr(d, 'Ne_cb1', 0)), fv(getattr(d, 'Nc_b1', 0), 2), math.ceil(getattr(d, 'Nc_b1', 0)), capas_completas_mt, int(getattr(d, 'Ne_cb1', 0)), sobrante_mt))
    print("Tensión de impulso (Vc1) = 2 * ({} / {}) * 0.75 = {} kV".format(getattr(d, 'BIL1', 95), math.ceil(getattr(d, 'Nc_b1', 0) or 1), fv(getattr(d, 'Vc1', 0), 2)))
    print("Aislamiento entre capas: delta_e = 5.0 * ({} / 40.0) = {} mm".format(fv(getattr(d, 'Vc1', 0), 2), fv(getattr(d, 'delta_s1', 0), 2)))
    if getattr(d, 'tap_data', None):
        items = sorted(list(d.tap_data.items()), reverse=True)
        if len(items) >= 2:
            # taps diff
            n_taps = []
            for i in range(len(items)-1):
                n_taps.append(abs(items[i][1]['N_espiras'] - items[i+1][1]['N_espiras']))
            min_esp = items[-1][1]['N_espiras']
            esp_1 = int(min_esp / 2)
            esp_2 = min_esp - esp_1
            print("Derivaciones (Nodos 6 4 2 1 3 5):")
            print(" - Extremo 1: {} espiras".format(esp_1))
            for i, val in enumerate(n_taps):
                print(" - Paso {}: {} espiras".format(i+1, val))
            print(" - Extremo 2: {} espiras".format(esp_2))

    if getattr(d, 'detalles_ciclo', None):
        print("\n4. RENDIMIENTO DIARIO")
        print("Rendimiento Diario (%): {}".format(fv(getattr(d, 'rendimiento_diario', 0), 4)))
    
    print("\n" + "="*30)
    print("         FIN DEL INFORME")
    print("="*30)

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