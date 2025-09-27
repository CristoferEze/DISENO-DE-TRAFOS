# src/design_phases/nucleus_and_window/lamination_plotters/__init__.py
import os
from . import monofasico_recto, monofasico_45deg, trifasico_recto, trifasico_45deg

def generate_plot(d, output_dir='temp', step_index=0):
    """
    Función 'fábrica' que selecciona y ejecuta el plotter correcto
    basado en el número de fases y el tipo de corte del diseño.

    Propagamos 'step_index' al plotter para que pueda personalizar el título
    y el nombre del archivo. Cada plotter debe devolver la ruta absoluta
    del archivo generado.

    Nota: step_index por defecto es 0 para ser robusto ante llamadas antiguas
    que no pasen explícitamente el índice.
    """
    cut = getattr(d, 'cut_type', 'Recto')
    fases = getattr(d, 'fases', 3)

    # Asegurarse de que el directorio de salida sea absoluto
    absolute_output_dir = os.path.abspath(output_dir)

    if fases == 3:
        if cut == 'Recto':
            return trifasico_recto.draw(d, absolute_output_dir, step_index=step_index)
        elif cut == 'Diagonal':
            return trifasico_45deg.draw(d, absolute_output_dir, step_index=step_index)
    elif fases == 1:
        if cut == 'Recto':
            return monofasico_recto.draw(d, absolute_output_dir, step_index=step_index)
        elif cut == 'Diagonal':
            return monofasico_45deg.draw(d, absolute_output_dir, step_index=step_index)

    raise ValueError(f"No hay un plotter disponible para {fases} fases con corte '{cut}'")