from datetime import date

from modelos import Ejemplar, Libro
from repositorios import (
    RepositorioEjemplaresMemoria,
    RepositorioLibrosMemoria,
    RepositorioPrestamosMemoria,
)
from servicios import ServicioCirculacion, ServicioMultas, ServicioReservas


def main():
    libros = RepositorioLibrosMemoria()
    ejemplares = RepositorioEjemplaresMemoria()
    prestamos = RepositorioPrestamosMemoria()

    libros.agregar(Libro(1, "Don Quijote", "Miguel de Cervantes"))
    ejemplares.agregar(Ejemplar(id=1, libro_id=1))

    reservas = ServicioReservas(ejemplares)
    circulacion = ServicioCirculacion(ejemplares, prestamos)
    multas = ServicioMultas(prestamos)

    print("BIBLIOTECA UNIVERSIDAD X")
    print("Demostración con datos de ejemplo en memoria")

    print("\n1. Buscar un libro")
    for libro in libros.buscar_por_titulo("quijote"):
        print(f"{libro.titulo} — {libro.autor}")

    print("\n2. Reservar el ejemplar para el usuario 100")
    reservado = reservas.reservar(1, 100)
    print(f"Estado: {reservado.estado.value}")

    print("\n3. Registrar el préstamo al usuario 100")
    prestamo = circulacion.prestar(
        1, 1, 100, date(2026, 11, 7), plazo_dias=7
    )
    print(f"Fecha de vencimiento: {prestamo.fecha_vencimiento:%d-%m-%Y}")

    print("\n4. Registrar la devolución")
    devuelto = circulacion.devolver(1, date(2026, 11, 17))
    print(f"Fecha de devolución: {devuelto.fecha_devolucion:%d-%m-%Y}")

    print("\n5. Calcular la multa: $1.000 diarios")
    monto_pesos = multas.calcular_por_prestamo(1)
    monto_formateado = f"{monto_pesos:,}".replace(",", ".")
    print(f"Multa por tres días de atraso: ${monto_formateado} CLP")


if __name__ == "__main__":
    main()
