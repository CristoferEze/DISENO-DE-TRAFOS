# -*- coding: utf-8 -*-
import math

# ==================================================================
# SECCION DE CONFIGURACION: MODIFIQUE LOS VALORES AQUI
# ==================================================================

# --- DATOS PRINCIPALES DEL TRANSFORMADOR ---
TIPO_TRANSFORMADOR = 'trifasico' # Opciones: 'trifasico' o 'monofasico'
S_kVA = 25                  # Potencia nominal en kVA
E1_LINEA_V = 10500            # Tension de linea del primario en Volts
E2_LINEA_V = 400              # Tension de linea del secundario en Volts
FRECUENCIA_HZ = 60            # Frecuencia en Hertz
CONEXION = 'D-Yn'             # Para trifasico (ej: 'Dyn5'). No importa para monofasico.
TAPS_PCT = [2.5, 5.0]         # Lista de TAPs en %. Dejar como [] si no hay.
TIPO_ACERO = '30M5'           # Opciones: '35M6', '30M5', '27M4', '23M3'

# --- PARAMETROS DE DISENO ---
RELACION_VENTANA_RW = 3.0     # Relacion de ventana (Rw = alto/ancho).

# --- PARAMETROS AVANZADOS (Opcional, dejar en None para calculo automatico) ---
B_KGAUSS_MANUAL = None        # Ejemplo: 16.5 para 16500 gauss
C_MANUAL = None               # Ejemplo: 1.55
KC_MANUAL = None              # Ejemplo: 0.27


# ==================================================================
# --- FIN DE LA CONFIGURACION --- NO MODIFICAR DEBAJO DE ESTA LINEA ---
# ==================================================================


print("# ------------------------------------------------------------------")
print("# PROGRAMA PARA EL CALCULO Y DISENO DE TRANSFORMADORES")
print("# Version 6.2: Corrientes de Toma mostradas como Corriente de Fase")
print("# ------------------------------------------------------------------")

# SECCION 1: BASES DE DATOS
densidad_flujo_db = {1: (11, 13), 10: (13, 16), 100: (16, 17), 1000: (17, 18), 5000: (17.5, 18)}
acero_electrico_db = {'35M6': {'fa': 0.975, 'merma': 'Merma 2.5% (35M6)'}, '30M5': {'fa': 0.970, 'merma': 'Merma 3.0% (30M5)'}, '27M4': {'fa': 0.965, 'merma': 'Merma 3.5% (27M4)'}, '23M3': {'fa': 0.960, 'merma': 'Merma 4.0% (23M3)'}}
densidad_corriente_db = {'ONAN': {'Cobre': (3.0, 4.0)}}
coeficiente_kr_db = {'Merma 2.5% (35M6)': {1: {5: 0.621}, 2: {15: 0.767}, 3: {50: 0.830}, 4: {200: 0.865}, 5: {500: 0.885}, 6: {750: 0.900}}, 'Merma 3.0% (30M5)': {1: {5: 0.618}, 2: {15: 0.763}, 3: {50: 0.825}, 4: {200: 0.860}, 5: {500: 0.881}, 6: {750: 0.896}}}
constante_flujo_db = {'monofasico_columnas': (1.2, 1.9), 'trifasico_columnas': (1, 1.6)}
dimensiones_escalones_db = {1: [0.707], 2: [0.850, 0.526], 3: [0.906, 0.707, 0.424], 4: [0.934, 0.796, 0.605, 0.356], 5: [0.950, 0.846, 0.707, 0.534, 0.313], 6: [0.959, 0.875, 0.768, 0.640, 0.488, 0.281]}

# SECCION 2: FUNCIONES AUXILIARES
def get_promedio(v): return (v[0] + v[1]) / 2
def sel_clave(d, val): return min([k for k in d if k >= val] or [max(d)])
def f_dec(v): return "{:.2f}".format(v)
def f_int(v): return "{}".format(int(v))

# SECCION 3: CLASE DE DISENO
class DisenoTransformador:
    def __init__(self, tipo, S, E1, E2, f, refrig, acero, conn, taps, b_man, c_man, kc_man, rel_rw):
        self.tipo = tipo; self.S = float(S); self.E1_linea = float(E1); self.E2_linea = float(E2)
        self.f = float(f); self.refrig = refrig; self.acero = acero; self.conn = conn
        self.taps_pct = taps if taps is not None else []; self.B_man = b_man; self.C_man = c_man
        self.Kc_man = kc_man; self.rel_rw = rel_rw
        self.fases = 3 if self.tipo == 'trifasico' else 1

    def _num_esc(self, ab):
        if ab < 30: return 1;
        if ab < 50: return 2;
        if ab < 70: return 3;
        if ab < 150: return 4;
        if ab < 450: return 5;
        return 6

    def ejecutar_calculos(self):
        # 1. PARAMETROS
        if self.B_man: self.B_kgauss = self.B_man
        else: self.B_kgauss = get_promedio(densidad_flujo_db[sel_clave(densidad_flujo_db, self.S)])
        self.B_tesla = self.B_kgauss / 10.0; self.J = get_promedio(densidad_corriente_db[self.refrig]['Cobre'])
        if self.C_man: self.C = self.C_man
        else: self.C = get_promedio(constante_flujo_db['trifasico_columnas' if self.fases == 3 else 'monofasico_columnas'])
        self.fa = acero_electrico_db[self.acero]['fa']; self.merma_id = acero_electrico_db[self.acero]['merma']
        
        if self.fases==3:
            self.conn1=self.conn.split('-')[0].upper(); self.conn2=self.conn.split('-')[1].upper()
            self.E1_fase = self.E1_linea if 'D' in self.conn1 else self.E1_linea / math.sqrt(3)
            self.E2_fase = self.E2_linea if 'D' in self.conn2 else self.E2_linea / math.sqrt(3)
        else:
            self.conn1="Monofasico"; self.conn2="Monofasico"; self.E1_fase=self.E1_linea; self.E2_fase=self.E2_linea
        
        if self.Kc_man: self.Kc=self.Kc_man
        else: E1_kv=self.E1_fase/1000.0; kc_n=8 if self.S<=10 else(12 if self.S>250 else 10); self.Kc=(kc_n/(30+E1_kv))*1.15

        # 2. FLUJO, 3. AREA, 4. DIMENSIONES NUCLEO
        self.flujo = self.C * math.sqrt(self.S / self.f) * 1e6
        self.An = self.flujo / (self.B_kgauss * 1000); self.Ab = self.An / self.fa
        self.num_escalones = self._num_esc(self.Ab)
        db_kr_acero = coeficiente_kr_db.get(self.merma_id, {}); db_kr_esc = db_kr_acero.get(self.num_escalones, {})
        self.Kr = db_kr_esc[sel_clave(db_kr_esc, self.S)]
        self.D = 2 * math.sqrt(self.An / (math.pi * self.Kr))
        self.anchos = [f*self.D for f in dimensiones_escalones_db.get(self.num_escalones,[])]
        self.espesores = []; suma_e_previos = 0
        for a_i in self.anchos: e_i = (math.sqrt(self.D**2 - a_i**2) - suma_e_previos) / 2.0; self.espesores.append(e_i); suma_e_previos += 2 * e_i
        self.An_verificacion = 2 * self.fa * sum([self.anchos[i]*self.espesores[i] for i in range(len(self.anchos))])

        # 5. VENTANA
        S_VA = self.S * 1000
        J_A_m2 = self.J * 1e6; An_m2 = self.An * 1e-4
        self.Aw_m2 = (S_VA) / (3.33 * self.f * self.B_tesla * J_A_m2 * self.Kc * An_m2)
        self.Aw = self.Aw_m2 * 1e4
        self.b = math.sqrt(self.rel_rw * self.Aw); self.M = (self.Aw / self.b) + self.D
        self.c_prima = self.M - self.anchos[0]; self.c = self.M - self.D
        
        # 6. ESPIRAS
        self.N2_fase = round((self.E2_fase * 1e8) / (4.44 * self.f * self.flujo))
        self.all_pct = sorted(list(set([-p for p in self.taps_pct] + [0] + self.taps_pct)))
        self.tap_data = {}
        for pct in self.all_pct:
            E1_l_tap = self.E1_linea*(1+pct/100.0)
            E1_f_tap = E1_l_tap if (self.fases==3 and 'D' in self.conn1) else E1_l_tap/math.sqrt(3)
            N1_f_tap = round(self.N2_fase * (E1_f_tap / self.E2_fase))
            self.tap_data[pct] = {'Vlinea': E1_l_tap, 'Vfase': E1_f_tap, 'N_espiras': N1_f_tap}

        # 7. CORRIENTES Y CALIBRES
        S_dev_VA = S_VA / self.fases
        self.I1_fase_nom = S_dev_VA / self.E1_fase
        self.I2_fase = S_dev_VA / self.E2_fase
        self.s1 = self.I1_fase_nom / self.J
        self.s2 = self.I2_fase / self.J

    def mostrar_resultados(self):
        print("\n# ==============================================================")
        print("#  RESULTADOS DEL DISENO")
        print("# ==============================================================")
        # ... (secciones 1 a 5 sin cambios)
        print("\n# --- DATOS DE TABLAS ---")
        print("    * Induccion Magnetica (B): {} gauss".format(f_int(self.B_kgauss*1000)))
        print("    * Densidad de Corriente (J): {} A/mm2".format(self.J))
        print("    * Coeficiente de Plenitud de Hierro (Kr): {}".format(self.Kr))
        print("    * Coeficiente de Plenitud de Cobre (Kc): {}".format(f_dec(self.Kc)))
        print("\n# --- FLUJO MAGNETICO ---")
        print("    * Flujo (Φ): {} lineas".format(f_int(self.flujo)))
        print("\n# --- AREA DEL NUCLEO ---")
        print("    * Area Neta (An): {} cm2".format(f_dec(self.An)))
        print("    * Area Bruta (Ab): {} cm2".format(f_dec(self.Ab)))
        print("\n# --- DIMENSIONES DEL NUCLEO ({} Escalones) ---".format(self.num_escalones))
        print("    * Diametro (D): {} cm".format(f_dec(self.D)))
        for i in range(self.num_escalones): print("    * a{}: {} cm, e{}: {} cm".format(i, f_dec(self.anchos[i]), i, f_dec(self.espesores[i])))
        print("    * Verificacion An: {} cm2 (debe ser cercano a An)".format(f_dec(self.An_verificacion)))
        print("\n# --- DIMENSIONES DE LA VENTANA ---")
        print("    * Area de Ventana (Aw): {} cm2".format(f_dec(self.Aw)))
        print("    * Alto de Ventana (b): {} cm".format(f_dec(self.b)))
        print("    * Distancia entre Ejes (M): {} cm".format(f_dec(self.M)))
        print("    * Ancho de Ventana (c): {} cm".format(f_dec(self.c)))
        print("    * Ancho de Ventana (c'): {} cm".format(f_dec(self.c_prima)))

        sorted_taps = sorted(self.tap_data.keys(), reverse=True)
        if self.taps_pct:
            print("\n# --- TENSIONES EN MT (por Toma) ---")
            for i, pct in enumerate(sorted_taps): print("    * Toma {} ({:+.1f}%): {} V (Linea)".format(i+1, pct, f_int(self.tap_data[pct]['Vlinea'])))
        print("\n# --- TENSION EN BT ---")
        print("    * Tension de Linea (E2): {} V".format(f_int(self.E2_linea)))

        print("\n# --- CORRIENTE ADMISIBLE ---")
        S_dev_VA = (self.S * 1000) / self.fases
        if self.taps_pct:
            for i, pct in enumerate(sorted_taps):
                Vfase_tap = self.tap_data[pct]['Vfase']
                I_fase_tap = S_dev_VA / Vfase_tap
                print("    * Lado MT, Fase Toma {} ({:+.1f}%): {} A".format(i+1, pct, f_dec(I_fase_tap)))
        
        print("    * Lado BT, Fase (para s2): {} A".format(f_dec(self.I2_fase)))
        
        print("\n# --- NUMERO DE ESPIRAS ---")
        print("    * Bobinado Secundario (N2): {} espiras".format(self.N2_fase))
        if self.taps_pct:
            print("    * Bobinado Primario (N1):")
            for i, pct in enumerate(sorted_taps): print("        Toma {} ({:+.1f}%): {} espiras".format(i+1, pct, self.tap_data[pct]['N_espiras']))
        else: print("    * Bobinado Primario (N1): {} espiras".format(self.tap_data[0]['N_espiras']))
            
        print("\n# --- CALIBRES DE BOBINADO ---")
        print("    * Seccion Primario (s1): {} mm2".format(f_dec(self.s1)))
        print("    * Seccion Secundario (s2): {} mm2".format(f_dec(self.s2)))
        
        if self.taps_pct:
            print("\n# --- DISTRIBUCION DE ESPIRAS (TAPS) ---")
            s_k = sorted(self.tap_data.keys(), reverse=True)
            diffs = [self.tap_data[s_k[i]]['N_espiras'] - self.tap_data[s_k[i+1]]['N_espiras'] for i in range(len(s_k)-1)]
            N_max = self.tap_data[s_k[0]]['N_espiras']
            N_taps_centrales = sum(diffs)
            N_bobina_principal = int(((N_max - N_taps_centrales) / 2.0) + 0.5)

            print("    * Seccion H1 (inicio) a tap {:+.1f}%: {} espiras".format(s_k[0], N_bobina_principal))
            for i in range(len(diffs)):
                print("    * De tap {:+.1f}% a tap {:+.1f}%: {} espiras".format(s_k[i], s_k[i+1], diffs[i]))
            print("    * De tap {:+.1f}% a H2 (final): {} espiras".format(s_k[-1], N_bobina_principal))
            print("    * Verificacion Total: {} (debe ser igual a N_max={})".format(N_bobina_principal*2 + N_taps_centrales, N_max))

# SECCION 4: EJECUCION
diseno = DisenoTransformador(
    tipo=TIPO_TRANSFORMADOR, S=S_kVA, E1=E1_LINEA_V, E2=E2_LINEA_V, f=FRECUENCIA_HZ,
    refrig='ONAN', acero=TIPO_ACERO, conn=CONEXION, taps=TAPS_PCT,
    b_man=B_KGAUSS_MANUAL, c_man=C_MANUAL, kc_man=KC_MANUAL, rel_rw=RELACION_VENTANA_RW
)
diseno.ejecutar_calculos()
diseno.mostrar_resultados()
