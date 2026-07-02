class ErrorCredencialesInvalidas(Exception):
    def __init__(self):
        self.mensaje = "Correo o contraseña incorrectos, o cuenta inactiva"