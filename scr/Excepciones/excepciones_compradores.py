class ErrorCompradorNoEncontrado(Exception):
    def __init__(self, id: int, ciudad: str):
        self.mensaje = f"No se encontró un comprador con id {id} en la ciudad '{ciudad}'"


class ErrorCompradorYaExiste(Exception):
    def __init__(self, id: int):
        self.mensaje = f"Ya existe un comprador con el id {id}"


class ErrorConfirmacionRequerida(Exception):
    def __init__(self):
        self.mensaje = "Debe confirmar la operación con confirmar=true"


class ErrorIdInvalido(Exception):
    def __init__(self):
        self.mensaje = "El id debe ser un número positivo"
