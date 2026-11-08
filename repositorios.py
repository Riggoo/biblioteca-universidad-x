from abc import ABC, abstractmethod

from modelos import Ejemplar, Libro, Prestamo


class RepositorioLibros(ABC):
    @abstractmethod
    def agregar(self, libro: Libro) -> None:
        pass

    @abstractmethod
    def buscar_por_titulo(self, texto: str) -> list[Libro]:
        pass


class RepositorioLibrosMemoria(RepositorioLibros):
    def __init__(self):
        self._libros: dict[int, Libro] = {}

    def agregar(self, libro: Libro) -> None:
        if libro.id in self._libros:
            raise ValueError("Ya existe un libro con ese identificador")
        self._libros[libro.id] = libro

    def buscar_por_titulo(self, texto: str) -> list[Libro]:
        consulta = texto.strip().casefold()
        return [
            libro for libro in self._libros.values()
            if consulta in libro.titulo.casefold()
        ]


class RepositorioEjemplares(ABC):
    @abstractmethod
    def agregar(self, ejemplar: Ejemplar) -> None:
        pass

    @abstractmethod
    def obtener(self, ejemplar_id: int) -> Ejemplar | None:
        pass

    @abstractmethod
    def actualizar(self, ejemplar: Ejemplar) -> None:
        pass


class RepositorioEjemplaresMemoria(RepositorioEjemplares):
    def __init__(self):
        self._ejemplares: dict[int, Ejemplar] = {}

    def agregar(self, ejemplar: Ejemplar) -> None:
        if ejemplar.id in self._ejemplares:
            raise ValueError("Ya existe un ejemplar con ese identificador")
        self._ejemplares[ejemplar.id] = ejemplar

    def obtener(self, ejemplar_id: int) -> Ejemplar | None:
        return self._ejemplares.get(ejemplar_id)

    def actualizar(self, ejemplar: Ejemplar) -> None:
        if ejemplar.id not in self._ejemplares:
            raise ValueError("El ejemplar no existe")
        self._ejemplares[ejemplar.id] = ejemplar


class RepositorioPrestamos(ABC):
    @abstractmethod
    def agregar(self, prestamo: Prestamo) -> None:
        pass

    @abstractmethod
    def obtener(self, prestamo_id: int) -> Prestamo | None:
        pass

    @abstractmethod
    def actualizar(self, prestamo: Prestamo) -> None:
        pass


class RepositorioPrestamosMemoria(RepositorioPrestamos):
    def __init__(self):
        self._prestamos: dict[int, Prestamo] = {}

    def agregar(self, prestamo: Prestamo) -> None:
        if prestamo.id in self._prestamos:
            raise ValueError("Ya existe un préstamo con ese identificador")
        self._prestamos[prestamo.id] = prestamo

    def obtener(self, prestamo_id: int) -> Prestamo | None:
        return self._prestamos.get(prestamo_id)

    def actualizar(self, prestamo: Prestamo) -> None:
        if prestamo.id not in self._prestamos:
            raise ValueError("El préstamo no existe")
        self._prestamos[prestamo.id] = prestamo
