from diagrams.generator import generate_connection_diagram as generate_connection_diagram_new

def generate_connection_diagram(d, output_dir='temp'):
    """
    Wrapper de compatibilidad: delega en el nuevo paquete diagrams.
    Mantiene la API antigua para que llamadas existentes sigan funcionando.
    """
    return generate_connection_diagram_new(d, output_dir=output_dir)