"""
Paquete de dominio.

El dominio es el núcleo de la arquitectura Onion. Contiene las entidades
de negocio y las interfaces (contratos) que definen cómo se persisten y
consultan los datos, sin ninguna dependencia de tecnologías externas.

Capas internas:
    - entities/    : Modelos de dominio (Compania, Empleado).
    - interfaces/  : Contratos abstractos de repositorios y Unit of Work.
"""
