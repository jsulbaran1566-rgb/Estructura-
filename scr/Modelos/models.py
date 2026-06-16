from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey
from Conexion.database import Base


def fecha_actual():
    """Genera la fecha de hoy en formato dd/mm/aaaa, para usarla como valor por defecto."""
    return datetime.now().strftime("%d/%m/%Y")


# ================= USUARIOS =================

class Usuario(Base):
    __tablename__ = "usuarios"

    id     = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    rol    = Column(String(50),  nullable=False)


# ================= CATEGORIAS =================

class Categoria(Base):
    __tablename__ = "categorias"

    nombre = Column(String(100), primary_key=True, index=True)


# ================= LOTES =================

class Lote(Base):
    __tablename__ = "lotes"

    id        = Column(Integer,     primary_key=True, index=True)
    producto  = Column(String(150), nullable=False)
    cantidad  = Column(Integer,     nullable=False)
    categoria = Column(String(100), ForeignKey("categorias.nombre"), nullable=False)


# ================= COMPRADORES =================

class Comprador(Base):
    __tablename__ = "compradores"

    id     = Column(Integer,     primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    ciudad = Column(String(100), nullable=False)


# ================= RESERVAS =================

class Reserva(Base):
    __tablename__ = "reservas"

    id        = Column(Integer,    primary_key=True, index=True)
    comprador = Column(String(150), nullable=False)
    producto  = Column(String(150), nullable=False)
    cantidad  = Column(Integer,     nullable=False)
    fecha     = Column(String(20),  nullable=False, default=fecha_actual)


# ================= HISTORIAL SEGUIMIENTO =================

class HistorialSeguimiento(Base):
    __tablename__ = "historial_seguimiento"

    id       = Column(Integer,     primary_key=True, index=True, autoincrement=True)
    accion   = Column(String(200), nullable=False)
    lote     = Column(Integer,     ForeignKey("lotes.id"), nullable=True)
    producto = Column(String(150), nullable=False)
    fecha    = Column(String(20),  nullable=False, default=fecha_actual)


# ================= COMPRAS =================

class Compra(Base):
    __tablename__ = "compras"

    id        = Column(Integer,     primary_key=True, index=True)
    comprador = Column(String(150), nullable=False)
    producto  = Column(String(150), nullable=False)
    cantidad  = Column(Integer,     nullable=False)
    fecha     = Column(String(20),  nullable=False, default=fecha_actual)


# ================= VENTAS =================

class Venta(Base):
    __tablename__ = "ventas"

    id        = Column(Integer,     primary_key=True, index=True)
    comprador = Column(String(150), nullable=False)
    producto  = Column(String(150), nullable=False)
    cantidad  = Column(Integer,     nullable=False)
    fecha     = Column(String(20),  nullable=False, default=fecha_actual)


# ================= HISTORIAL RESERVAS =================

class HistorialReserva(Base):
    __tablename__ = "historial_reservas"

    id        = Column(Integer,     primary_key=True, index=True, autoincrement=True)
    comprador = Column(String(150), nullable=False)
    producto  = Column(String(150), nullable=False)
    cantidad  = Column(Integer,     nullable=False)
    fecha     = Column(String(20),  nullable=False, default=fecha_actual)