from dataclasses import replace
from datetime import date, timedelta

from modelos import Ejemplar, EstadoEjemplar, Prestamo
from multas import calcular_multa
from repositorios import RepositorioEjemplares, RepositorioPrestamos


def validar_identificador(identificador: int) -> None:
    if type(identificador) is not int or identificador <= 0:
        raise ValueError("El identificador debe ser un entero positivo")


class ServicioReservas:
    def __init__(self, ejemplares: RepositorioEjemplares):
        self._ejemplares = ejemplares

    def reservar(self, ejemplar_id: int, usuario_id: int) -> Ejemplar:
        validar_identificador(usuario_id)
        ejemplar = self._ejemplares.obtener(ejemplar_id)
        if ejemplar is None:
            raise ValueError("El ejemplar no existe")
        if ejemplar.estado != EstadoEjemplar.DISPONIBLE:
            raise ValueError("El ejemplar no está disponible")
        reservado = replace(
            ejemplar,
            estado=EstadoEjemplar.RESERVADO,
            reservado_por=usuario_id,
        )
        self._ejemplares.actualizar(reservado)
        return reservado


class ServicioCirculacion:
    def __init__(
        self,
        ejemplares: RepositorioEjemplares,
        prestamos: RepositorioPrestamos,
    ):
        self._ejemplares = ejemplares
        self._prestamos = prestamos

    def prestar(
        self,
        prestamo_id: int,
        ejemplar_id: int,
        usuario_id: int,
        fecha: date,
        plazo_dias: int,
    ) -> Prestamo:
        validar_identificador(prestamo_id)
        validar_identificador(usuario_id)
        if type(plazo_dias) is not int or plazo_dias <= 0:
            raise ValueError("El plazo debe ser un entero positivo")
        ejemplar = self._ejemplares.obtener(ejemplar_id)
        if ejemplar is None:
            raise ValueError("El ejemplar no existe")
        if ejemplar.estado == EstadoEjemplar.PRESTADO:
            raise ValueError("El ejemplar ya está prestado")
        if (
            ejemplar.estado == EstadoEjemplar.RESERVADO
            and ejemplar.reservado_por != usuario_id
        ):
            raise ValueError("La reserva pertenece a otro usuario")
        prestamo = Prestamo(
            id=prestamo_id,
            ejemplar_id=ejemplar_id,
            usuario_id=usuario_id,
            fecha_prestamo=fecha,
            fecha_vencimiento=fecha + timedelta(days=plazo_dias),
        )
        self._prestamos.agregar(prestamo)
        self._ejemplares.actualizar(replace(
            ejemplar, estado=EstadoEjemplar.PRESTADO, reservado_por=None
        ))
        return prestamo

    def devolver(self, prestamo_id: int, fecha: date) -> Prestamo:
        prestamo = self._prestamos.obtener(prestamo_id)
        if prestamo is None:
            raise ValueError("El préstamo no existe")
        if prestamo.fecha_devolucion is not None:
            raise ValueError("El préstamo ya fue devuelto")
        if fecha < prestamo.fecha_prestamo:
            raise ValueError("La devolución no puede ser anterior al préstamo")
        ejemplar = self._ejemplares.obtener(prestamo.ejemplar_id)
        if ejemplar is None:
            raise ValueError("El ejemplar no existe")
        devuelto = replace(prestamo, fecha_devolucion=fecha)
        self._prestamos.actualizar(devuelto)
        self._ejemplares.actualizar(replace(
            ejemplar, estado=EstadoEjemplar.DISPONIBLE, reservado_por=None
        ))
        return devuelto


class ServicioMultas:
    def __init__(self, prestamos: RepositorioPrestamos):
        self._prestamos = prestamos

    def calcular_por_prestamo(self, prestamo_id: int) -> int:
        prestamo = self._prestamos.obtener(prestamo_id)
        if prestamo is None:
            raise ValueError("El préstamo no existe")
        if prestamo.fecha_devolucion is None:
            raise ValueError("El préstamo debe estar devuelto para calcular la multa final")
        return calcular_multa(
            prestamo.fecha_vencimiento, prestamo.fecha_devolucion
        )
