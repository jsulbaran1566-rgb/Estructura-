class ErrorUsuarioNoExiste(Exception):
    def __init__(self, id):
        self.mensaje = f"No existe un usuario con el id {id}"


class ErrorStockInsuficiente(Exception):
    def __init__(self, producto, pedido, disponible):
        self.mensaje = f"No hay suficiente stock de '{producto}'. Pedido: {pedido}, Disponible: {disponible}"