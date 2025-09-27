# src/design_phases/nucleus_and_window/lamination_plotters/__init__.py
from . import monofasico_recto, monofasico_45deg, trifasico_recto, trifasico_45deg

def generate_plot(d, output_dir='temp'):
    """
    Función 'fábrica' que selecciona y ejecuta el plotter correcto
    basado en el número de fases y el tipo de corte del diseño.
    """
    cut = getattr(d, 'cut_type', 'Recto')
    fases = getattr(d, 'fases', 3)

    if fases == 3:
        if cut == 'Recto':
            return trifasico_recto.draw(d, output_dir)
        elif cut == 'Diagonal':
            return trifasico_45deg.draw(d, output_dir)
    elif fases == 1:
        if cut == 'Recto':
            return monofasico_recto.draw(d, output_dir)
        elif cut == 'Diagonal':
            return monofasico_45deg.draw(d, output_dir)

    raise ValueError(f"No hay un plotter disponible para {fases} fases con corte '{cut}'")