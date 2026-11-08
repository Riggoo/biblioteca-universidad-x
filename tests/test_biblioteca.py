from datetime import date

import pytest

from modelos import Ejemplar, EstadoEjemplar, Libro
from multas import calcular_multa
from repositorios import (
    RepositorioEjemplaresMemoria,
    RepositorioLibrosMemoria,
    RepositorioPrestamosMemoria,
)
from servicios import ServicioCirculacion, ServicioMultas, ServicioReservas


@pytest.fixture
def sistema():
    ejemplares = RepositorioEjemplaresMemoria()
    ejemplares.agregar(Ejemplar(1, 10))
    prestamos = RepositorioPrestamosMemoria()
    return (
        ejemplares,
        prestamos,
        ServicioReservas(ejemplares),
        ServicioCirculacion(ejemplares, prestamos),
        ServicioMultas(prestamos),
    )


def test_buscar_titulo_sin_distinguir_mayusculas():
    libros = RepositorioLibrosMemoria()
    libro = Libro(10, "Don Quijote", "Miguel de Cervantes")
    libros.agregar(libro)
    assert libros.buscar_por_titulo("  QUIJOTE  ") == [libro]


def test_buscar_sin_coincidencias():
    libros = RepositorioLibrosMemoria()
    libros.agregar(Libro(10, "Don Quijote", "Miguel de Cervantes"))
    assert libros.buscar_por_titulo("Papelucho") == []


def test_rechazar_libro_duplicado():
    libros = RepositorioLibrosMemoria()
    libros.agregar(Libro(10, "Don Quijote", "Miguel de Cervantes"))
    with pytest.raises(ValueError, match="Ya existe un libro"):
        libros.agregar(Libro(10, "Otro título", "Otro autor"))
    assert libros.buscar_por_titulo("Don Quijote")[0].titulo == "Don Quijote"


def test_reservar_ejemplar(sistema):
    ejemplares, _, reservas, _, _ = sistema
    reservas.reservar(1, 100)
    guardado = ejemplares.obtener(1)
    assert guardado.estado == EstadoEjemplar.RESERVADO
    assert guardado.reservado_por == 100


def test_rechazar_reserva_inexistente(sistema):
    _, _, reservas, _, _ = sistema
    with pytest.raises(ValueError, match="El ejemplar no existe"):
        reservas.reservar(99, 100)


def test_rechazar_segunda_reserva(sistema):
    ejemplares, _, reservas, _, _ = sistema
    reservas.reservar(1, 100)
    with pytest.raises(ValueError, match="no está disponible"):
        reservas.reservar(1, 200)
    assert ejemplares.obtener(1).reservado_por == 100


def test_prestar_ejemplar_disponible(sistema):
    ejemplares, prestamos, _, circulacion, _ = sistema
    prestamo = circulacion.prestar(1, 1, 100, date(2026, 11, 7), 7)
    assert prestamo.fecha_vencimiento == date(2026, 11, 14)
    assert prestamos.obtener(1) == prestamo
    assert ejemplares.obtener(1).estado == EstadoEjemplar.PRESTADO


def test_prestar_reserva_al_titular(sistema):
    ejemplares, _, reservas, circulacion, _ = sistema
    reservas.reservar(1, 100)
    circulacion.prestar(1, 1, 100, date(2026, 11, 7), 7)
    assert ejemplares.obtener(1).estado == EstadoEjemplar.PRESTADO
    assert ejemplares.obtener(1).reservado_por is None


def test_rechazar_prestamo_de_reserva_ajena(sistema):
    ejemplares, prestamos, reservas, circulacion, _ = sistema
    reservas.reservar(1, 100)
    with pytest.raises(ValueError, match="otro usuario"):
        circulacion.prestar(1, 1, 200, date(2026, 11, 7), 7)
    assert prestamos.obtener(1) is None
    assert ejemplares.obtener(1).reservado_por == 100


def test_rechazar_prestamo_inexistente(sistema):
    _, prestamos, _, circulacion, _ = sistema
    with pytest.raises(ValueError, match="El ejemplar no existe"):
        circulacion.prestar(1, 99, 100, date(2026, 11, 7), 7)
    assert prestamos.obtener(1) is None


def test_rechazar_segundo_prestamo(sistema):
    _, prestamos, _, circulacion, _ = sistema
    circulacion.prestar(1, 1, 100, date(2026, 11, 7), 7)
    with pytest.raises(ValueError, match="ya está prestado"):
        circulacion.prestar(2, 1, 200, date(2026, 11, 7), 7)
    assert prestamos.obtener(2) is None


@pytest.mark.parametrize("plazo", [0, -1, 1.5])
def test_rechazar_plazo_invalido(sistema, plazo):
    ejemplares, prestamos, _, circulacion, _ = sistema
    with pytest.raises(ValueError, match="El plazo"):
        circulacion.prestar(1, 1, 100, date(2026, 11, 7), plazo)
    assert prestamos.obtener(1) is None
    assert ejemplares.obtener(1).estado == EstadoEjemplar.DISPONIBLE


def test_rechazar_identificador_usuario_invalido(sistema):
    _, _, reservas, _, _ = sistema
    with pytest.raises(ValueError, match="identificador"):
        reservas.reservar(1, 0)


def test_rechazar_identificador_prestamo_duplicado(sistema):
    ejemplares, prestamos, _, circulacion, _ = sistema
    ejemplares.agregar(Ejemplar(2, 10))
    primero = circulacion.prestar(1, 1, 100, date(2026, 11, 7), 7)
    with pytest.raises(ValueError, match="Ya existe un préstamo"):
        circulacion.prestar(1, 2, 200, date(2026, 11, 7), 7)
    assert prestamos.obtener(1) == primero
    assert ejemplares.obtener(2).estado == EstadoEjemplar.DISPONIBLE


def test_devolver_libera_ejemplar_y_conserva_prestamo(sistema):
    ejemplares, prestamos, _, circulacion, _ = sistema
    circulacion.prestar(1, 1, 100, date(2026, 11, 7), 7)
    circulacion.devolver(1, date(2026, 11, 14))
    assert prestamos.obtener(1).fecha_devolucion == date(2026, 11, 14)
    assert ejemplares.obtener(1).estado == EstadoEjemplar.DISPONIBLE
    circulacion.prestar(2, 1, 200, date(2026, 11, 15), 7)
    assert prestamos.obtener(1).fecha_devolucion == date(2026, 11, 14)
    assert prestamos.obtener(2).fecha_devolucion is None


def test_rechazar_devolucion_repetida(sistema):
    _, prestamos, _, circulacion, _ = sistema
    circulacion.prestar(1, 1, 100, date(2026, 11, 7), 7)
    circulacion.devolver(1, date(2026, 11, 14))
    with pytest.raises(ValueError, match="ya fue devuelto"):
        circulacion.devolver(1, date(2026, 11, 17))
    assert prestamos.obtener(1).fecha_devolucion == date(2026, 11, 14)


def test_rechazar_devolucion_anterior_al_prestamo(sistema):
    ejemplares, prestamos, _, circulacion, _ = sistema
    circulacion.prestar(1, 1, 100, date(2026, 11, 7), 7)
    with pytest.raises(ValueError, match="anterior al préstamo"):
        circulacion.devolver(1, date(2026, 11, 6))
    assert prestamos.obtener(1).fecha_devolucion is None
    assert ejemplares.obtener(1).estado == EstadoEjemplar.PRESTADO


def test_rechazar_devolucion_inexistente(sistema):
    _, _, _, circulacion, _ = sistema
    with pytest.raises(ValueError, match="El préstamo no existe"):
        circulacion.devolver(99, date(2026, 11, 14))


@pytest.mark.parametrize("dia, esperado", [(12, 0), (14, 0), (15, 1000), (17, 3000)])
def test_calcular_multa_en_pesos(dia, esperado):
    assert calcular_multa(date(2026, 11, 14), date(2026, 11, dia)) == esperado


def test_calcular_multa_del_prestamo_devuelto(sistema):
    _, _, _, circulacion, multas = sistema
    circulacion.prestar(1, 1, 100, date(2026, 11, 7), 7)
    circulacion.devolver(1, date(2026, 11, 17))
    assert multas.calcular_por_prestamo(1) == 3000


def test_rechazar_multa_final_de_prestamo_activo(sistema):
    _, _, _, circulacion, multas = sistema
    circulacion.prestar(1, 1, 100, date(2026, 11, 7), 7)
    with pytest.raises(ValueError, match="debe estar devuelto"):
        multas.calcular_por_prestamo(1)


def test_rechazar_multa_de_prestamo_inexistente(sistema):
    _, _, _, _, multas = sistema
    with pytest.raises(ValueError, match="El préstamo no existe"):
        multas.calcular_por_prestamo(99)
