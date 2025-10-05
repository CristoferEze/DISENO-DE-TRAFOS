# src/core/engine.py
# -*- coding: utf-8 -*-

import math
from design_phases.nucleus_and_window import calculation as nucleus_calc
from design_phases.windings_and_taps import calculation as windings_calc
from design_phases.core_and_lamination_weights import calculation as core_weights_calc
from design_phases.losses_and_performance import calculation as losses_perf_calc
from design_phases.daily_performance import calculation as daily_perf_calc

class DisenoTransformador:
    """
    Clase que encapsula el ESTADO del diseño.
    La lógica de cálculo está organizada por fases en design_phases.
    """
    def __init__(self, **kwargs):
        self.tipo = kwargs.get('tipo', 'trifasico')
        self.S = float(kwargs.get('S', 25))  # Cambiar valor inicial a 50 kVA
        self.E1_linea = float(kwargs.get('E1', 10000))  # Cambiar valor inicial a 13200 V
        self.E2_linea = float(kwargs.get('E2', 400))
        self.f = float(kwargs.get('f', 60))
        self.acero = kwargs.get('acero', '35M6')
        self.conn = kwargs.get('conn', 'Dyn5')  # Cambiar conexión por defecto a Dyn5
        self.taps_pct = kwargs.get('taps', [])
        self.rel_rw = float(kwargs.get('rel_rw', 3.0))
        self.refrig = 'ONAN'
        self.fases = 3 if self.tipo == 'trifasico' else 1
        self.B_man = kwargs.get('b_man')
        self.C_man = kwargs.get('c_man')
        self.Kc_man = kwargs.get('kc_man')
        # Nuevo: tipo de corte para los plotters ('Recto' o 'Diagonal')
        self.cut_type = kwargs.get('cut_type', 'Recto')
        # Nuevos: opciones de redondeo y valores opcionales
        self.redondear_2_decimales = kwargs.get('redondear_2_decimales', False)
        self.usar_valores_opcionales = kwargs.get('usar_valores_opcionales', False)
        # Valores opcionales de parámetros de diseño
        self.B_opcional = kwargs.get('b_opcional')
        self.C_opcional = kwargs.get('c_opcional')
        self.Kc_opcional = kwargs.get('kc_opcional')
        self.J_opcional = kwargs.get('j_opcional')
        # Valores opcionales de parámetros de tabla
        self.fa_opcional = kwargs.get('fa_opcional')
        self.Kr_opcional = kwargs.get('kr_opcional')
        self.Pf_opcional = kwargs.get('pf_opcional')
        self.rho_acero_opcional = kwargs.get('rho_acero_opcional')
        self.rho_cobre_opcional = kwargs.get('rho_cobre_opcional')
        # Asegurar que el ciclo de carga pasado en kwargs quede registrado en el objeto.
        # Puede ser None o una lista de tuplas (carga_frac, horas).
        self.ciclo_carga = kwargs.get('ciclo_carga', None)
        self._inicializar_propiedades()

    def _inicializar_propiedades(self):
        self.B_kgauss = self.B_tesla = self.J = self.C = self.fa = self.merma_id = None
        self.E1_fase = self.E2_fase = self.conn1 = self.conn2 = None
        self.Kc = self.flujo = self.An = self.Ab = None
        self.num_escalones = self.Kr = self.D = None
        self.anchos = []
        self.espesores = []
        self.An_verificacion = None
        self.Aw = self.b = self.M = self.c = self.c_prima = None
        self.N2_fase = None
        self.tap_data = {}
        self.I1_fase_nom = self.I2_fase = self.s1 = self.s2 = None

        # Nuevas propiedades para resultados de TAPs
        self.tap_currents = {}
        self.tap_distribution = {}

    def _num_esc(self, ab):
        if ab < 30:
            return 1
        if ab < 50:
            return 2
        if ab < 70:
            return 3
        if ab < 150:
            return 4
        if ab < 450:
            return 5
        return 6

    def ejecutar_calculo_completo(self):
        """
        Orquesta la ejecución de los cálculos llamando a cada fase de diseño
        en el orden correcto.
        """
        nucleus_calc.run(self)

        # Devanados y TAPs (ahora también calcula peso del cobre por bobinado)
        windings_calc.run(self)
        
        # Núcleo: peso detallado por escalón / laminaciones
        core_weights_calc.run(self)

        # Pérdidas y rendimiento (usa Qc por bobinado y Qr detallado)
        losses_perf_calc.run(self)

        # Rendimiento diario (usa d.ciclo_carga si está presente)
        daily_perf_calc.run(self)