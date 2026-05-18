# src/design_phases/nucleus_and_window/lamination_plotter.py
"""Adaptador backward-compatible: redirige a la nueva carpeta lamination_plotters.
Mantiene la API antigua generate_lamination_plot(diseno, output_dir).
"""
import os
import tempfile
from .lamination_plotters import generate_plot


def _resolve_output_dir(output_dir):
    if not output_dir or output_dir == 'temp':
        return tempfile.gettempdir()
    return output_dir


def generate_lamination_plot(d, output_dir=None):
    """Llama a la fábrica de plotters respetando la interfaz previa."""
    output_dir = _resolve_output_dir(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    # Asegurar valor por defecto para cut_type
    if not getattr(d, 'cut_type', None):
        d.cut_type = 'Recto'
    return generate_plot(d, output_dir)