# -*- coding: utf-8 -*-
"""
MOTOR DE CÁLCULO ALQUILAPC - SENA
Basado fielmente en el programa de pruebas de software SENA ADSI CGMLTI.
Garantiza valores estrictamente positivos (sin signos + ni - y sin negativos).
"""

from typing import Dict, Any, Tuple

# Constantes oficiales del sistema SENA
VDIA = 35000          # Tarifa diaria normal
VDIA_ADICIONAL = 34300 # Tarifa diaria adicional
DOMICILIO_FUERA = 60725.0 # Valor estricto celda SENA fuera de ciudad
DTO_CIUDAD = 10500.0   # Descuento informativo ciudad y fuera de ciudad
DTO_ESTABLECIMIENTO = 71225.0 # Descuento especial sede

SERVICIOS_DISPONIBLES = {
    1: {
        "codigo": 1,
        "nombre": "Dentro de la Ciudad",
        "descripcion": "Entrega rápida en el perímetro urbano de la ciudad.",
        "costo_domicilio": 0.0,
        "descuento_visual": DTO_CIUDAD,
        "dto_formula": 0.0
    },
    2: {
        "codigo": 2,
        "nombre": "Fuera de la Ciudad",
        "descripcion": "Transporte logístico a municipios y veredas.",
        "costo_domicilio": DOMICILIO_FUERA,
        "descuento_visual": DTO_CIUDAD,
        "dto_formula": 0.0
    },
    3: {
        "codigo": 3,
        "nombre": "En Instalaciones SENA",
        "descripcion": "Uso directo en salas de cómputo del SENA.",
        "costo_domicilio": 0.0,
        "descuento_visual": DTO_ESTABLECIMIENTO,
        "dto_formula": DTO_ESTABLECIMIENTO - DTO_CIUDAD # 60.725
    }
}

def validar_entradas(nombre: str, equipos: int, diasal: int, diasad: int, opcion: int) -> Tuple[bool, list]:
    errores = []
    if not nombre or not nombre.strip():
        errores.append("El nombre del cliente no puede estar vacío.")
    if equipos <= 0:
        errores.append("La cantidad de equipos debe ser mayor a cero (sin números negativos).")
    if diasal <= 0:
        errores.append("Los días de alquiler inicial deben ser mayores a cero (sin números negativos).")
    if diasad < 0:
        errores.append("Los días adicionales no pueden ser negativos.")
    if opcion not in [1, 2, 3]:
        errores.append("El tipo de servicio debe ser 1, 2 o 3.")
    return len(errores) == 0, errores

def calculo_alquiler(equipos: int, diasal: int) -> float:
    return float(max(0, equipos) * max(0, diasal) * VDIA)

def calculo_alquiler_adicional(equipos: int, diasad: int) -> float:
    return float(max(0, equipos) * max(0, diasad) * VDIA_ADICIONAL)

def calculo_domicilio(opcion: int) -> float:
    if opcion == 2:
        return DOMICILIO_FUERA
    return 0.0

def calculo_descuento(opcion: int) -> float:
    if opcion in [1, 2]:
        return DTO_CIUDAD
    elif opcion == 3:
        return DTO_ESTABLECIMIENTO
    return 0.0

def calcular_liquidacion_completa(nombre: str, equipos: int, diasal: int, diasad: int, opcion: int) -> Dict[str, Any]:
    valido, errores = validar_entradas(nombre, equipos, diasal, diasad, opcion)
    if not valido:
        raise ValueError(" | ".join(errores))

    val_alquiler = calculo_alquiler(equipos, diasal)
    val_adicional = calculo_alquiler_adicional(equipos, diasad)
    subtotal_equipos = val_alquiler + val_adicional

    desc_visual = calculo_descuento(opcion)
    val_domicilio = calculo_domicilio(opcion)

    # Fórmula exacta de Python:
    # if opcion in [1, 2]: dto_formula = 0.0
    # elif opcion == 3: dto_formula = calculo_descuento() - 10500.0 (71.225 - 10.500 = 60.725)
    dto_formula = 0.0
    if opcion == 3:
        dto_formula = desc_visual - DTO_CIUDAD

    total_calculado = val_alquiler + val_adicional - dto_formula + val_domicilio
    total_final = max(0.0, total_calculado)

    servicio = SERVICIOS_DISPONIBLES[opcion]

    return {
        "nombre_cliente": nombre.strip(),
        "equipos": equipos,
        "dias_iniciales": diasal,
        "dias_adicionales": diasad,
        "tipo_servicio_codigo": opcion,
        "tipo_servicio_nombre": servicio["nombre"],
        "valor_dia_base": VDIA,
        "valor_dia_adicional": VDIA_ADICIONAL,
        "valor_alquiler_inicial": val_alquiler,
        "valor_dias_adicionales": val_adicional,
        "subtotal_equipos": subtotal_equipos,
        "descuento_visual": desc_visual,
        "descuento_formula_efectivo": dto_formula,
        "valor_domicilio": val_domicilio,
        "total_pagar": total_final,
        "explicacion_descuento": (
            f"Subtotal ({formatear_moneda(subtotal_equipos)}) menos descuento en sede "
            f"({formatear_moneda(dto_formula)}) = {formatear_moneda(subtotal_equipos - dto_formula)}"
        ) if dto_formula > 0 else ""
    }

def formatear_moneda(valor: float) -> str:
    val_pos = max(0.0, valor)
    # Formato colombiano: $ 1.050.000 COP
    cadena = f"{val_pos:,.0f}".replace(",", ".")
    return f"$ {cadena} COP"
