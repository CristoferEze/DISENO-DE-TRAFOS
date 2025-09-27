# src/design_phases/core_and_lamination_weights/calculation.py
# -*- coding: utf-8 -*-

import math
from core import database as db

def run(d):
    """Calcula el peso del núcleo detallado por cada escalón y sus laminaciones."""
    d.peso_por_escalon = []
    d.Qr_por_laminaciones = 0.0

    rho_g_cm3 = 7.65
    espesor_lamina_mm = db.acero_electrico_db.get(d.acero, {}).get('espesor_mm', 0.35)
    espesor_lamina_cm = espesor_lamina_mm / 10.0

    if d.fases == 3 and getattr(d, 'anchos', None) and getattr(d, 'espesores', None):
        piezas_defs = {
            '1': {'l': d.b + getattr(d, 'g', 0.0), 'w': getattr(d, 'g', 0.0), 'n_por_capa': 3},
            '2': {'l': d.c + getattr(d, 'g', 0.0), 'w': getattr(d, 'g', 0.0), 'n_por_capa': 2},
            '3': {'l': d.c + d.anchos[0] + getattr(d, 'g', 0.0), 'w': getattr(d, 'g', 0.0), 'n_por_capa': 1}
        }

        for i, espesor_escalon in enumerate(d.espesores):
            ancho_paquete_cm = (espesor_escalon * 2.0) if espesor_escalon else espesor_lamina_cm
            num_laminas = int(math.ceil(ancho_paquete_cm / espesor_lamina_cm)) if espesor_lamina_cm > 0 else 0

            peso_total_escalon = 0.0
            detalles_escalon = []

            for nombre, pieza in piezas_defs.items():
                volumen_una_lamina = pieza['l'] * pieza['w'] * espesor_lamina_cm
                peso_una_lamina_kg = (volumen_una_lamina * rho_g_cm3) / 1000.0
                peso_total_tipo = peso_una_lamina_kg * num_laminas * pieza['n_por_capa']

                detalles_escalon.append({
                    'nombre': f'Figura {nombre}',
                    'num_piezas': num_laminas * pieza['n_por_capa'],
                    'peso_kg': peso_total_tipo
                })
                peso_total_escalon += peso_total_tipo

            d.peso_por_escalon.append({
                'escalon': i + 1,
                'detalles': detalles_escalon,
                'peso_total_escalon': peso_total_escalon
            })
            d.Qr_por_laminaciones += peso_total_escalon

    # Establecer d.Qr usando laminaciones si se calculó
    if getattr(d, 'Qr_por_laminaciones', 0):
        d.Qr = d.Qr_por_laminaciones
    else:
        # fallback volumétrico
        rho_hierro_kg_cm3 = 7.65 / 1000.0
        a1 = d.anchos[0] if getattr(d, 'anchos', None) else getattr(d, 'D', 0)
        if d.fases == 3:
            volumen_hierro = (3 * d.An * d.b) + (2 * d.An * getattr(d, 'L_trifasico', (2 * d.c + 2 * d.D + a1)))
            d.Qr = volumen_hierro * rho_hierro_kg_cm3
        else:
            volumen_hierro = (2 * d.An * d.b) + (2 * d.An * getattr(d, 'L_monofasico', (d.c + d.D + a1)))
            d.Qr = volumen_hierro * rho_hierro_kg_cm3