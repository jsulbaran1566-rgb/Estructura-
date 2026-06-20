from datetime import date
from sqlalchemy import Column, Integer, String, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from Conexion.database import Base


# ================= USUARIOS =================

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint("rol IN ('Productor', 'Comprador', 'Administrador')", name="chk_usuarios_rol"),
    )

    id     = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    rol    = Column(String(50),  nullable=False)

    comprador = relationship("Comprador", back_populates="usuario", uselist=False)
    lotes     = relationship("Lote", back_populates="productor")
    ventas    = relationship("Venta", back_populates="vendedor")


# ================= CATEGORIAS =================

class Categoria(Base):
    __tablename__ = "categorias"

    nombre = Column(String(100), primary_key=True, index=True)

    lotes = relationship("Lote", back_populates="categoria_rel")


# ================= COMPRADORES =================
# Un comprador ES un usuario (id es FK a usuarios.id, no un id propio)

class Comprador(Base):
    __tablename__ = "compradores"

    id     = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    ciudad = Column(String(100), nullable=False)

    usuario  = relationship("Usuario", back_populates="comprador")
    reservas = relationship("Reserva", back_populates="comprador")
    compras  = relationship("Compra", back_populates="comprador")


# ================= LOTES =================

class Lote(Base):
    __tablename__ = "lotes"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_lotes_cant"),
    )

    id           = Column(Integer,     primary_key=True, index=True)
    producto     = Column(String(150), nullable=False)
    cantidad     = Column(Integer,     nullable=False)
    categoria    = Column(String(100), ForeignKey("categorias.nombre", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    productor_id = Column(Integer,     ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)

    categoria_rel = relationship("Categoria", back_populates="lotes")
    productor     = relationship("Usuario", back_populates="lotes")
    reservas      = relationship("Reserva", back_populates="lote")
    historial     = relationship("HistorialSeguimiento", back_populates="lote_rel")
    compras       = relationship("Compra", back_populates="lote")
    ventas        = relationship("Venta", back_populates="lote")


# ================= RESERVAS =================
# Ya no tiene columnas "comprador"/"producto" de texto ni "estado":
# usa FKs (comprador_id, lote_id) y el estado se rastrea en historial_reservas.

class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_reservas_cant"),
    )

    id           = Column(Integer, primary_key=True, index=True)
    comprador_id = Column(Integer, ForeignKey("compradores.id", ondelete="RESTRICT"), nullable=False)
    lote_id      = Column(Integer, ForeignKey("lotes.id", ondelete="RESTRICT"), nullable=False)
    cantidad     = Column(Integer, nullable=False)
    fecha        = Column(String(20), nullable=False, default="09/05/2026")

    comprador         = relationship("Comprador", back_populates="reservas")
    lote              = relationship("Lote", back_populates="reservas")
    historial_estados = relationship(
        "HistorialReserva",
        back_populates="reserva_rel",
        order_by="HistorialReserva.id",
    )


# ================= HISTORIAL SEGUIMIENTO =================

class HistorialSeguimiento(Base):
    __tablename__ = "historial_seguimiento"

    id       = Column(Integer,     primary_key=True, index=True, autoincrement=True)
    accion   = Column(String(200), nullable=False)
    lote     = Column(Integer,     ForeignKey("lotes.id", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    producto = Column(String(150), nullable=False)
    fecha    = Column(Date, nullable=False, default=date.today)

    lote_rel = relationship("Lote", back_populates="historial")


# ================= COMPRAS =================
# Antes: comprador/producto de texto. Ahora: comprador_id + lote_id (FKs).

class Compra(Base):
    __tablename__ = "compras"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_compras_cant"),
    )

    id           = Column(Integer, primary_key=True, index=True)
    comprador_id = Column(Integer, ForeignKey("compradores.id"), nullable=False)
    lote_id      = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    cantidad     = Column(Integer, nullable=False)
    fecha        = Column(Date, nullable=False, default=date.today)

    comprador = relationship("Comprador", back_populates="compras")
    lote      = relationship("Lote", back_populates="compras")


# ================= VENTAS =================
# Antes: "comprador" de texto (incorrecto: confundía comprador con vendedor).
# Ahora: vendedor_id (FK a usuarios = el productor que vendió) + lote_id.

class Venta(Base):
    __tablename__ = "ventas"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_ventas_cant"),
    )

    id          = Column(Integer, primary_key=True, index=True)
    vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    lote_id     = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    cantidad    = Column(Integer, nullable=False)
    fecha       = Column(Date, nullable=False, default=date.today)

    vendedor = relationship("Usuario", back_populates="ventas")
    lote     = relationship("Lote", back_populates="ventas")


# ================= HISTORIAL RESERVAS =================
# Antes: comprador/producto/cantidad de texto.
# Ahora: bitácora de cambios de estado por reserva (reserva_id + estado + fecha).

class HistorialReserva(Base):
    __tablename__ = "historial_reservas"

    id         = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False)
    estado     = Column(String(50), nullable=False)
    fecha      = Column(String(20), nullable=False, default="09/05/2026")

    reserva_rel = relationship("Reserva", back_populates="historial_estados")
