# -*- coding: utf-8 -*-
"""
APLICACIÓN WEB FLASK - ALQUILAPC SENA
Enlazado exclusivamente a la red privada (127.0.0.1).
Implementa ciberseguridad de doble capa y orquestación con Message Broker.
"""

import os
import time
from flask import Flask, render_template, request, jsonify
from core.calculator import calcular_liquidacion_completa, formatear_moneda, SERVICIOS_DISPONIBLES
from core.security import TwoLayerSecurityEngine
from core.broker import ResilientMessageBroker

app = Flask(__name__)
security = TwoLayerSecurityEngine.get_instance()
broker = ResilientMessageBroker.get_instance()

# Middleware de Seguridad: Cabeceras HTTP de Protección
@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self' data:;"
    )
    return response

@app.route("/")
def index():
    return render_template("index.html", servicios=SERVICIOS_DISPONIBLES)

@app.route("/api/liquidar", methods=["POST"])
def liquidar_alquiler():
    client_ip = request.remote_addr or "127.0.0.1"

    # CAPA 1 (APIs): Rate Limiting
    if not security.check_rate_limit(client_ip, max_requests=80, window_sec=60):
        return jsonify({"error": "Demasiadas peticiones. Por favor espere unos segundos."}), 429

    data = request.get_json() or {}

    raw_nombre = data.get("nombre", "")
    equipos = int(data.get("equipos", 1))
    diasal = int(data.get("diasIniciales", 1))
    diasad = int(data.get("diasAdicionales", 0))
    opcion = int(data.get("tipoServicio", 1))

    # CAPA 1 (FRONT/API): Sanitización estricta
    nombre_seguro = security.sanitize_input(raw_nombre, "Nombre Cliente")
    if not nombre_seguro:
        return jsonify({"error": "El nombre del cliente no puede estar vacío."}), 400

    # CAPA 1 (MICROSERVICIOS): Orquestación con Message Broker y Circuit Breaker
    res_broker = broker.orchestrate_alquiler(equipos, diasal, diasad, opcion)

    # Cálculo y Desglose Oficial SENA
    subtotal_equipos = res_broker["alquiler_base"] + res_broker["alquiler_adicional"]
    dto_formula = res_broker["dto_formula"]
    subtotal_con_desc = subtotal_equipos - dto_formula

    # CAPA 2 (DATABASE): Cifrado en reposo simulado
    security.encrypt_data_at_rest(f"Cliente:{nombre_seguro}|Total:{res_broker['total']}")

    folio = f"SENA-FLASK-{int(time.time())}"
    client_signature = security.generate_integrity_signature({
        "nombre": nombre_seguro,
        "equipos": equipos,
        "total": res_broker["total"]
    })

    return jsonify({
        "status": "SUCCESS",
        "folio": folio,
        "fecha": time.strftime("%d/%m/%Y %H:%M"),
        "firma": client_signature,
        "cliente": nombre_seguro,
        "equipos": equipos,
        "dias_iniciales": diasal,
        "dias_adicionales": diasad,
        "tipo_servicio_codigo": opcion,
        "tipo_servicio_nombre": SERVICIOS_DISPONIBLES[opcion]["nombre"],
        "valor_alquiler_inicial": res_broker["alquiler_base"],
        "valor_alquiler_inicial_fmt": formatear_moneda(res_broker["alquiler_base"]),
        "valor_dias_adicionales": res_broker["alquiler_adicional"],
        "valor_dias_adicionales_fmt": formatear_moneda(res_broker["alquiler_adicional"]),
        "subtotal_equipos": subtotal_equipos,
        "subtotal_equipos_fmt": formatear_moneda(subtotal_equipos),
        "descuento_sede": dto_formula,
        "descuento_sede_fmt": formatear_moneda(dto_formula),
        "explicacion_descuento": (
            f"Subtotal ({formatear_moneda(subtotal_equipos)}) menos descuento de ({formatear_moneda(dto_formula)}) = {formatear_moneda(subtotal_con_desc)}"
        ) if dto_formula > 0 else "",
        "valor_domicilio": res_broker["domicilio"],
        "valor_domicilio_fmt": formatear_moneda(res_broker["domicilio"]),
        "total": res_broker["total"],
        "total_fmt": formatear_moneda(res_broker["total"])
    })

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" ALQUILAPC • SERVIDOR PRIVADO FLASK SENA")
    print(" Enlazado exclusivamente a la red privada (Loopback 127.0.0.1)")
    print(" Abre en tu navegador: http://127.0.0.1:5000")
    print("="*70 + "\n")
    # Forzar ejecución en interfaz privada local
    app.run(host="127.0.0.1", port=5000, debug=False)
