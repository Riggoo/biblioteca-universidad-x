from dataclasses import dataclass
from datetime import date
from enum import Enum


class EstadoEjemplar(Enum):
    DISPONIBLE = "disponible"
    RESERVADO = "reservado"
    PRESTADO = "prestado"


@dataclass(frozen=True)
class Libro:
    id: int
    titulo: str
    autor: str


@dataclass(frozen=True)
class Ejemplar:
    id: int
    libro_id: int
    estado: EstadoEjemplar = EstadoEjemplar.DISPONIBLE
    reservado_por: int | None = None


@dataclass(frozen=True)
class Prestamo:
    id: int
    ejemplar_id: int
    usuario_id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None
