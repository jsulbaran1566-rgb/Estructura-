from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


# ================= CATEGORIAS =================

class CategoriaCrear(BaseModel):
    nombre: str

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre de la categoría no puede estar vacío")
        return v.strip().capitalize()


class CategoriaEditar(BaseModel):
    nombre_nuevo: str

    @field_validator("nombre_nuevo")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nuevo nombre no puede estar vacío")
        return v.strip().capitalize()


# ================= LOTES =================

class LoteCrear(BaseModel):
    id: int
    producto: str
    cantidad: int
    categoria: str
    productor_id: int
    estado: str = "Activo"
    fecha_cosecha: Optional[date] = None
    precio_kg: Optional[float] = None

    @field_validator("id", "productor_id")
    @classmethod
    def ids_positivos(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Los ids deben ser números positivos")
        return v

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: str) -> str:
        if v not in ("Activo", "Inactivo"):
            raise ValueError("El estado debe ser 'Activo' o 'Inactivo'")
        return v

    @field_validator("precio_kg")
    @classmethod
    def precio_positivo(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("El precio por kg no puede ser negativo")
        return v


class LoteEditar(BaseModel):
    producto:      Optional[str]   = None
    cantidad:      Optional[int]   = None
    categoria:     Optional[str]   = None
    estado:        Optional[str]   = None
    precio_kg:     Optional[float] = None
    fecha_cosecha: Optional[date]  = None

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("Activo", "Inactivo"):
            raise ValueError("El estado debe ser 'Activo' o 'Inactivo'")
        return v

    @field_validator("precio_kg")
    @classmethod
    def precio_positivo(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("El precio por kg no puede ser negativo")
        return v


# ================= RESERVAS =================

class ReservaCrear(BaseModel):
    id: int
    comprador_id: int
    lote_id: int
    cantidad: int

    @field_validator("id", "comprador_id", "lote_id")
    @classmethod
    def ids_positivos(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Los ids deben ser números positivos")
        return v

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v: int) -> int:
        if v < 1:
            raise ValueError("La cantidad mínima a reservar es 1")
        return v


class ReservaEditar(BaseModel):
    comprador_id: Optional[int]  = None
    fecha:        Optional[date] = None
    estado:       Optional[str]  = None

    @field_validator("comprador_id")
    @classmethod
    def comprador_positivo(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("El comprador_id debe ser un número positivo")
        return v

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: Optional[str]) -> Optional[str]:
        estados = ["Pendiente", "Confirmada", "Cancelada", "Entregada"]
        if v is not None and v not in estados:
            raise ValueError(f"Estado inválido. Opciones: {estados}")
        return v


# ================= USUARIOS =================

TIPOS_DOCUMENTO_VALIDOS = ["CC", "NIT", "CE", "PP"]
ROLES_VALIDOS   = ["Administrador", "Productor", "Comprador"]
ESTADOS_VALIDOS = ["Activo", "Inactivo"]


class UsuarioCrear(BaseModel):
    id:             int
    tipo_documento: str
    nombre:         str
    correo:         EmailStr
    telefono:       str
    clave:          str
    direccion:      Optional[str] = None
    ciudad:         Optional[str] = None
    empresa:        Optional[str] = None
    rol_id:         int
    estado:         str = "Activo"

    @field_validator("id")
    @classmethod
    def id_positivo(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El id debe ser un número positivo")
        return v

    @field_validator("tipo_documento")
    @classmethod
    def tipo_doc_valido(cls, v: str) -> str:
        if v not in TIPOS_DOCUMENTO_VALIDOS:
            raise ValueError(f"Tipo de documento inválido. Opciones: {TIPOS_DOCUMENTO_VALIDOS}")
        return v

    @field_validator("rol_id")
    @classmethod
    def rol_id_positivo(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El rol_id debe ser un número positivo")
        return v

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: str) -> str:
        if v not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Opciones: {ESTADOS_VALIDOS}")
        return v

    @field_validator("clave")
    @classmethod
    def clave_minima(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La clave debe tener al menos 6 caracteres")
        return v


class UsuarioEditar(BaseModel):
    tipo_documento: Optional[str]      = None
    nombre:         Optional[str]      = None
    correo:         Optional[EmailStr] = None
    telefono:       Optional[str]      = None
    clave:          Optional[str]      = None
    direccion:      Optional[str]      = None
    ciudad:         Optional[str]      = None
    rol_id:         Optional[int]      = None
    estado:         Optional[str]      = None

    @field_validator("tipo_documento")
    @classmethod
    def tipo_doc_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in TIPOS_DOCUMENTO_VALIDOS:
            raise ValueError(f"Tipo de documento inválido. Opciones: {TIPOS_DOCUMENTO_VALIDOS}")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip() if v else v

    @field_validator("telefono")
    @classmethod
    def telefono_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("El teléfono no puede estar vacío")
        return v.strip() if v else v

    @field_validator("rol_id")
    @classmethod
    def rol_id_positivo(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("El rol_id debe ser un número positivo")
        return v

    @field_validator("estado")
    @classmethod
    def estado_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Opciones: {ESTADOS_VALIDOS}")
        return v

# ================= ROLES =================

class RolCrear(BaseModel):
    id:          int
    nombre:      str
    descripcion: Optional[str] = None
    permisos:    Optional[str] = None

    @field_validator("id")
    @classmethod
    def id_positivo(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El id debe ser un número positivo")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre del rol no puede estar vacío")
        return v.strip()


class RolEditar(BaseModel):
    nombre:      Optional[str] = None
    descripcion: Optional[str] = None
    permisos:    Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("El nombre del rol no puede estar vacío")
        return v.strip() if v else v


# ================= TIPOS DOCUMENTO =================

class TipoDocumentoCrear(BaseModel):
    codigo: str
    nombre: str

    @field_validator("codigo")
    @classmethod
    def codigo_valido(cls, v: str) -> str:
        v = v.strip().upper()
        if not v or len(v) > 4:
            raise ValueError("El código debe tener entre 1 y 4 caracteres")
        return v

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class TipoDocumentoEditar(BaseModel):
    nombre: Optional[str] = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip() if v else v


# ================= AUTENTICACION =================

class LoginEntrada(BaseModel):
    correo: EmailStr
    clave: str

    @field_validator("clave")
    @classmethod
    def clave_no_vacia(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La clave no puede estar vacía")
        return v