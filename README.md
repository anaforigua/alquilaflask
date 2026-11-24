# ALQUILAPC • Servidor Flask Privado SENA

Implementación completa del sistema de liquidación de alquiler de computadores SENA en **Python + Flask**, con:

1. **Fidelidad Matemática a Python**: Mismas constantes (`vdia = 35000`, `vdia_adicional = 34300`), descuentos de sede y transporte fuera de ciudad.
2. **Ciberseguridad de Doble Capa Transversal**: Sanitización en Front y API, Gateway Rate Limiter, firmas criptográficas, consultas parametrizadas y cifrado simulado en reposo.
3. **Message Broker Asíncrono & Circuit Breaker**: Microservicios de Tarifas, Descuentos, Logística y Facturación operando de forma transparente en segundo plano.
4. **Diseño Futurista Pastel Senior-Friendly**:
   - Cero emojis (imágenes e iconos vectoriales SVG limpios).
   - Sin botón de contraste confuso.
   - Escalado de fuentes `A-` y `A+` 100% funcional.
   - Breakpoints responsivos para pantallas de $\ge 1026\text{px}$ y $\le 720\text{px}$.
   - **Impresión exclusiva del comprobante** (`@media print` suprime menús, botones y cabeceras).
   - **Valores estrictamente positivos** (sin signos `+` o `-`, con explicación clara de la resta del descuento).
5. **Enlace a Red Privada**: Corre en `http://127.0.0.1:5000` (Loopback seguro, bloqueado a redes públicas).

---

## 🚀 Cómo Ejecutarlo

1. Abre tu terminal de **PowerShell**:
   ```powershell
   cd "C:\Users\CLAUDIA\.gemini\antigravity\scratch\alquilapc-flask"
   ```

2. Instala Flask (si aún no lo tienes):
   ```powershell
   pip install flask
   ```

3. Inicia el servidor privado:
   ```powershell
   python app.py
   ```

4. Abre en tu navegador web:  
   👉 **`http://127.0.0.1:5000`**
