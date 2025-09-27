# src/design_phases/nucleus_and_window/lamination_plotter.py
"""Adaptador backward-compatible: redirige a la nueva carpeta lamination_plotters.
Mantiene la API antigua generate_lamination_plot(diseno, output_dir).
"""
import os
from .lamination_plotters import generate_plot

def generate_lamination_plot(d, output_dir='temp'):
    """Llama a la fábrica de plotters respetando la interfaz previa."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Asegurar valor por defecto para cut_type
    if not getattr(d, 'cut_type', None):
        d.cut_type = 'Recto'
    return generate_plot(d, output_dir)