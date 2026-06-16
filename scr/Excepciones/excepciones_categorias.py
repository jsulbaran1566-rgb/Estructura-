class ErrorCategoriaNoEncontrada(Exception):
    def __init__(self, nombre: str):
        self.mensaje = f"No se encontró la categoría '{nombre}'"


class ErrorCategoriaYaExiste(Exception):
    def __init__(self, nombre: str):
        self.mensaje = f"La categoría '{nombre}' ya existe"


class ErrorCantidadMinNegativa(Exception):
    def __init__(self):
        self.mensaje = "El valor de cantidad_min no puede ser negativo"
