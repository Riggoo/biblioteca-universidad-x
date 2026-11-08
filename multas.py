from datetime import date


TARIFA_DIARIA_PESOS = 1000


def calcular_multa(vencimiento: date, devolucion: date) -> int:
    """Calcula la multa en pesos chilenos, a $1.000 por día de atraso."""
    dias_atraso = max(0, (devolucion - vencimiento).days)
    return dias_atraso * TARIFA_DIARIA_PESOS
