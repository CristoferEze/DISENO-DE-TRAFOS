# Proyecto: Calculadora de Diseño de Transformadores

Este repositorio contiene una herramienta de cálculo y generación de reportes para el diseño de transformadores eléctricos. El software automatiza fases de diseño como núcleo, ventana, bobinados, pérdidas y rendimiento diario, y produce reportes renderizados en LaTeX para visualización.

Propósito
- Facilitar el cálculo y la documentación del diseño de transformadores en proyectos académicos y de ingeniería.

Requisitos
- Python 3.8+
- Paquetes: matplotlib, numpy, scipy, pandas (instalar vía pip)
- Sistema con LaTeX si se usa renderizado avanzado con usetex en matplotlib

Instalación rápida
1. Clonar el repositorio:
   git clone <url-del-repositorio>
2. Crear y activar un entorno virtual (recomendado):
   python -m venv venv
   source venv/bin/activate  # o venv\Scripts\activate en Windows
3. Instalar dependencias:
   pip install -r requirements.txt

Uso
- Ejecutar la aplicación principal:
  python src/main.py
- Interfaz gráfica (si está disponible) mostrará opciones para ingresar parámetros y generar reportes.
- Los módulos de cálculo están organizados en src/design_phases y pueden reutilizarse o probarse individualmente.

Estructura básica del proyecto
- src/core: núcleo del cálculo (engine, database, utils)
- src/design_phases: fases de diseño (núcleo, bobinas, pérdidas, rendimiento, etc.)
- src/ui: interfaz y generación de reportes
- temp/: imágenes y archivos temporales generados en el proceso

Contribución
- Se aceptan PR para mejorar cálculos, añadir validaciones y mejorar la documentación.

Créditos
- Elaborado por C.E.A.T., Facultad de Ingeniería Eléctrica y Electrónica (FIEE), Universidad Nacional del Centro del Perú (UNCP).

Licencia
- Revisar el archivo LICENSE en el repositorio para detalles sobre la licencia.
