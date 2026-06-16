from typing import Optional
from pydantic import BaseModel


# ================= CATEGORIAS =================

class CategoriaCrear(BaseModel):
    nombre: str


# ================= COMPRADORES =================

class CompradorCrear(BaseModel):
    id: int
    nombre: str
    ciudad: str


# ================= LOTES =================

class LoteCrear(BaseModel):
    id: int
    producto: str
    cantidad: int
    categoria: str


class LoteEditar(BaseModel):
    cantidad:  Optional[int] = None
    categoria: Optional[str] = None


# ================= RESERVAS =================

class ReservaCrear(BaseModel):
    producto: str
    cantidad: int


# ================= USUARIOS =================

class UsuarioCrear(BaseModel):
    id: int
    nombre: str
    rol: str


class UsuarioEditar(BaseModel):
    nombre: Optional[str]  = None
    activo: Optional[bool] = True