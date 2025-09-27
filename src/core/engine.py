# src/core/engine.py
# -*- coding: utf-8 -*-

import math
from design_phases.nucleus_and_window import calculation as nucleus_calc
from design_phases.windings_and_taps import calculation as windings_calc
from design_phases.weights_and_losses import calculation as weights_calc

class DisenoTransformador:
    """
    Clase que encapsula el ESTADO del diseño.
    La lógica de cálculo está organizada por fases en design_phases.
    """
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
        windings_calc.run(self)
        
        # Nueva fase: cálculo de pesos y pérdidas
        weights_calc.run(self)