# src/backend/engine.py

# -*- coding: utf-8 -*-
import math
from . import database as db
from . import utils 

class DisenoTransformador:
    """
    Clase que encapsula TODA la lógica y el estado para el diseño
    de un transformador. Su única responsabilidad es CALCULAR.
    """
    # El constructor (__init__), _inicializar_propiedades, y todos los
    # métodos de cálculo (_calcular_parametros_base, _calcular_nucleo, etc.)
    # permanecen EXACTAMENTE IGUALES a la versión anterior.
    
    # <<<--- ELIMINAR POR COMPLETO ---<<<
    # Se eliminan los métodos 'generar_reporte_latex' y '_latex_paso'.
    # La clase ya no sabe nada sobre LaTeX ni sobre cómo mostrarse.
    def __init__(self, **kwargs):
        self.tipo = kwargs.get('tipo', 'trifasico')
        self.S = float(kwargs.get('S', 25))
        self.E1_linea = float(kwargs.get('E1', 10500))
        self.E2_linea = float(kwargs.get('E2', 400))
        self.f = float(kwargs.get('f', 60))
        self.acero = kwargs.get('acero', '30M5')
        self.conn = kwargs.get('conn', 'D-Yn')
        self.taps_pct = kwargs.get('taps', [])
        self.rel_rw = float(kwargs.get('rel_rw', 3.0))
        self.refrig = 'ONAN'
        self.fases = 3 if self.tipo == 'trifasico' else 1
        self.B_man = kwargs.get('b_man')
        self.C_man = kwargs.get('c_man')
        self.Kc_man = kwargs.get('kc_man')
        self._inicializar_propiedades()

    def _inicializar_propiedades(self):
        self.B_kgauss = self.B_tesla = self.J = self.C = self.fa = self.merma_id = None
        self.E1_fase = self.E2_fase = self.conn1 = self.conn2 = None
        self.Kc = self.flujo = self.An = self.Ab = None
        self.num_escalones = self.Kr = self.D = None
        self.anchos = self.espesores = []
        self.An_verificacion = None
        self.Aw = self.b = self.M = self.c = self.c_prima = None
        self.N2_fase = self.tap_data = None
        self.I1_fase_nom = self.I2_fase = self.s1 = self.s2 = None

    def ejecutar_calculo_completo(self):
        self._calcular_parametros_base()
        self._calcular_tensiones_fase()
        self._calcular_kc()
        self._calcular_nucleo()
        self._calcular_ventana()
        self._calcular_devanados_y_corrientes()

    def _calcular_parametros_base(self):
        self.B_kgauss = self.B_man if self.B_man else utils.get_promedio(db.densidad_flujo_db[utils.sel_clave(db.densidad_flujo_db, self.S)])
        self.B_tesla = self.B_kgauss / 10.0
        self.J = utils.get_promedio(db.densidad_corriente_db[self.refrig]['Cobre'])
        self.fa = db.acero_electrico_db[self.acero]['fa']
        self.merma_id = db.acero_electrico_db[self.acero]['merma']
        tipo_nucleo_key = f"{self.tipo}_columnas"
        self.C = self.C_man if self.C_man else utils.get_promedio(db.constante_flujo_db[tipo_nucleo_key])
        
    def _calcular_tensiones_fase(self):
        if self.fases == 3:
            self.conn1, self.conn2 = self.conn.upper().split('-')
            self.E1_fase = self.E1_linea if 'D' in self.conn1 else self.E1_linea / math.sqrt(3)
            self.E2_fase = self.E2_linea if 'D' in self.conn2 else self.E2_linea / math.sqrt(3)
        else:
            self.conn1 = self.conn2 = "Monofasico"
            self.E1_fase = self.E1_linea
            self.E2_fase = self.E2_linea

    def _calcular_kc(self):
        if self.Kc_man:
            self.Kc = self.Kc_man
        else:
            E1_kv = self.E1_fase / 1000.0
            kc_n = 8 if self.S <= 10 else (10 if 10 < self.S <= 250 else 12)
            self.Kc = (kc_n / (30 + E1_kv)) * 1.15

    def _num_esc(self, ab):
        if ab < 30: return 1
        if ab < 50: return 2
        if ab < 70: return 3
        if ab < 150: return 4
        if ab < 450: return 5
        return 6

    def _calcular_nucleo(self):
        self.flujo = self.C * math.sqrt(self.S / self.f) * 1e6
        self.An = self.flujo / (self.B_kgauss * 1000)
        self.Ab = self.An / self.fa
        self.num_escalones = self._num_esc(self.Ab)
        db_kr_acero = db.coeficiente_kr_db.get(self.merma_id, {})
        db_kr_esc = db_kr_acero.get(self.num_escalones, {})
        self.Kr = db_kr_esc[utils.sel_clave(db_kr_esc, self.S)]
        self.D = 2 * math.sqrt(self.An / (math.pi * self.Kr))
        self.anchos = [factor * self.D for factor in db.dimensiones_escalones_db.get(self.num_escalones, [])]
        self.espesores = []
        suma_e_previos = 0
        for a_i in self.anchos:
            e_i = (math.sqrt(self.D**2 - a_i**2) - suma_e_previos) / 2.0
            self.espesores.append(e_i)
            suma_e_previos += 2 * e_i
        self.An_verificacion = 2 * self.fa * sum([self.anchos[i] * self.espesores[i] for i in range(len(self.anchos))])

    def _calcular_ventana(self):
        S_VA = self.S * 1000
        J_A_m2 = self.J * 1e6
        An_m2 = self.An * 1e-4
        self.Aw_m2 = (S_VA) / (3.33 * self.f * self.B_tesla * J_A_m2 * self.Kc * An_m2)
        self.Aw = self.Aw_m2 * 1e4
        self.b = math.sqrt(self.rel_rw * self.Aw)
        self.M = (self.Aw / self.b) + self.D
        self.c_prima = self.M - self.anchos[0]
        self.c = self.M - self.D
        
    def _calcular_devanados_y_corrientes(self):
        self.N2_fase = round((self.E2_fase * 1e8) / (4.44 * self.f * self.flujo))
        all_pct = sorted(list(set([-p for p in self.taps_pct] + [0] + self.taps_pct)))
        self.tap_data = {}
        for pct in all_pct:
            E1_l_tap = self.E1_linea * (1 + pct / 100.0)
            E1_f_tap = E1_l_tap if (self.fases == 3 and 'D' in self.conn1) else E1_l_tap / math.sqrt(3)
            N1_f_tap = round(self.N2_fase * (E1_f_tap / self.E2_fase))
            self.tap_data[pct] = {'Vlinea': E1_l_tap, 'Vfase': E1_f_tap, 'N_espiras': N1_f_tap}
        S_dev_VA = (self.S * 1000) / self.fases
        self.I1_fase_nom = S_dev_VA / self.E1_fase
        self.I2_fase = S_dev_VA / self.E2_fase
        self.s1 = self.I1_fase_nom / self.J
        self.s2 = self.I2_fase / self.J