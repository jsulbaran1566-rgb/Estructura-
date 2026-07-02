from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.orm import relationship
from Conexion.database import Base


# ================= TIPOS DOCUMENTO =================

class TipoDocumento(Base):
    __tablename__ = "tipos_documento"
    codigo  = Column(String(4),   primary_key=True)
    nombre  = Column(String(100), nullable=False)
    usuarios = relationship("Usuario", back_populates="tipo_documento_rel")


# ================= ROLES =================

class Rol(Base):
    __tablename__ = "roles"
    id          = Column(Integer,    primary_key=True)
    nombre      = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text,       nullable=True)
    permisos    = Column(Text,       nullable=True)
    usuarios    = relationship("Usuario", back_populates="rol_rel")


# ================= USUARIOS =================

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('Activo','Inactivo')",
            name="chk_usuarios_estado",
        ),
    )

    id             = Column(Integer,     primary_key=True, index=True)
    tipo_documento = Column(String(4),   ForeignKey("tipos_documento.codigo", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    nombre         = Column(String(150), nullable=False)
    correo         = Column(String(150), unique=True, nullable=False)
    telefono       = Column(String(20),  unique=True, nullable=False)
    clave          = Column(String(255), nullable=False)
    direccion      = Column(String(200), nullable=True)
    ciudad         = Column(String(100), nullable=True)
    empresa        = Column(String(150), nullable=True)
    rol_id         = Column(Integer,     ForeignKey("roles.id", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    estado         = Column(String(20),  nullable=False, default="Activo")
    fecha_registro = Column(Date,        nullable=False,  default=date.today)

    tipo_documento_rel = relationship("TipoDocumento", back_populates="usuarios")
    rol_rel            = relationship("Rol",           back_populates="usuarios")
    lotes    = relationship("Lote",    back_populates="productor")
    ventas   = relationship("Venta",   back_populates="vendedor")
    reservas = relationship("Reserva", back_populates="comprador")
    compras  = relationship("Compra",  back_populates="comprador")


# ================= CATEGORIAS =================

class Categoria(Base):
    __tablename__ = "categorias"

    nombre = Column(String(100), primary_key=True, index=True)

    lotes = relationship("Lote", back_populates="categoria_rel")


# ================= LOTES =================

class Lote(Base):
    __tablename__ = "lotes"
    __table_args__ = (
        CheckConstraint("cantidad > 0",             name="chk_lotes_cant"),
        CheckConstraint("kg_reservados >= 0",       name="chk_lote_reservados"),
        CheckConstraint("estado IN ('Activo','Inactivo')", name="chk_lote_estado"),
    )

    id            = Column(Integer,       primary_key=True, index=True)
    producto      = Column(String(150),   nullable=False)
    cantidad      = Column(Integer,       nullable=False)
    categoria     = Column(String(100),   ForeignKey("categorias.nombre", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    productor_id  = Column(Integer,       ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    estado        = Column(String(20),    nullable=False, default="Activo")
    fecha_cosecha = Column(Date,          nullable=True)
    kg_reservados = Column(Integer,       nullable=False, default=0)
    precio_kg     = Column(Numeric(10,2), nullable=True)

    categoria_rel = relationship("Categoria",           back_populates="lotes")
    productor     = relationship("Usuario",             back_populates="lotes")
    reservas      = relationship("Reserva",             back_populates="lote")
    historial     = relationship("HistorialSeguimiento",back_populates="lote_rel")
    compras       = relationship("Compra",              back_populates="lote")
    ventas        = relationship("Venta",               back_populates="lote")


# ================= RESERVAS =================
# El estado se guarda directamente en la tabla.
# historial_reservas actúa como bitácora de cada cambio de estado.

class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_reservas_cant"),
        CheckConstraint(
            "estado IN ('Pendiente','Confirmada','Cancelada','Entregada')",
            name="chk_reserva_estado",
        ),
    )

    id           = Column(Integer, primary_key=True, index=True)
    comprador_id = Column(Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False)
    lote_id      = Column(Integer, ForeignKey("lotes.id",    ondelete="RESTRICT"), nullable=False)
    cantidad     = Column(Integer, nullable=False)
    fecha        = Column(Date,    nullable=False, default=date.today)
    estado       = Column(String(20), nullable=False, default="Pendiente")

    comprador         = relationship("Usuario", back_populates="reservas")
    lote              = relationship("Lote",      back_populates="reservas")
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
    fecha    = Column(DateTime,    nullable=False, default=datetime.now)

    lote_rel = relationship("Lote", back_populates="historial")


# ================= COMPRAS =================

class Compra(Base):
    __tablename__ = "compras"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_compras_cant"),
    )

    id           = Column(Integer,       primary_key=True, index=True)
    comprador_id = Column(Integer,       ForeignKey("usuarios.id"),  nullable=False)
    lote_id      = Column(Integer,       ForeignKey("lotes.id"),     nullable=False)
    cantidad     = Column(Integer,       nullable=False)
    fecha        = Column(Date,          nullable=False, default=date.today)
    total        = Column(Numeric(12,2), nullable=True)

    comprador = relationship("Usuario", back_populates="compras")
    lote      = relationship("Lote",      back_populates="compras")


# ================= VENTAS =================

class Venta(Base):
    __tablename__ = "ventas"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="chk_ventas_cant"),
    )

    id          = Column(Integer,       primary_key=True, index=True)
    vendedor_id = Column(Integer,       ForeignKey("usuarios.id"), nullable=False)
    lote_id     = Column(Integer,       ForeignKey("lotes.id"),    nullable=False)
    cantidad    = Column(Integer,       nullable=False)
    fecha       = Column(Date,          nullable=False, default=date.today)
    total       = Column(Numeric(12,2), nullable=True)

    vendedor = relationship("Usuario", back_populates="ventas")
    lote     = relationship("Lote",    back_populates="ventas")


# ================= HISTORIAL RESERVAS =================
# Bitácora: cada vez que cambia el estado de una reserva se inserta un registro.

class HistorialReserva(Base):
    __tablename__ = "historial_reservas"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('Pendiente','Confirmada','Cancelada','Entregada')",
            name="chk_historial_estado",
        ),
    )

    id         = Column(Integer,  primary_key=True, index=True, autoincrement=True)
    reserva_id = Column(Integer,  ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False)
    estado     = Column(String(20), nullable=False)
    fecha      = Column(DateTime,   nullable=False, default=datetime.now)

    reserva_rel = relationship("Reserva", back_populates="historial_estados")