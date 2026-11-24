// Interacción Front-End para ALQUILAPC Flask Edition

const VDIA = 35000;
const VDIA_ADIC = 34300;
const DOMI_FUERA = 60725.0;
const DTO_CIUDAD = 10500.0;
const DTO_ESTABLECIMIENTO = 71225.0;

let dat = { nom: '', eq: 1, dIni: 1, dAdic: 0, srv: 1 };
let escalaActual = 19;

window.addEventListener('DOMContentLoaded', () => {
  actualizar();
});

// Escalado de fuente 100% funcional (A- y A+)
function ajustarLetra(delta) {
  escalaActual = Math.max(15, Math.min(27, escalaActual + delta));
  document.documentElement.style.setProperty('--font-base-size', escalaActual + 'px');
  document.getElementById('txtEscala').textContent = escalaActual;
}

function irAlPaso(n) {
  [1, 2, 3].forEach(p => {
    document.getElementById(`step${p}`).style.display = (p === n) ? 'flex' : 'none';
    const tab = document.getElementById(`tab${p}`);
    if (p === n) tab.classList.add('active'); else tab.classList.remove('active');
  });
}

function pasarPaso2() {
  const v = document.getElementById('txtNom').value.trim();
  if (!v) { alert('Por favor ingrese su nombre para continuar.'); return; }
  irAlPaso(2);
}

function modificar(campo, delta, min) {
  dat[campo] = Math.max(min, dat[campo] + delta);
  if (campo === 'eq') document.getElementById('dspEq').textContent = dat.eq;
  if (campo === 'dIni') document.getElementById('dspDIni').textContent = dat.dIni;
  if (campo === 'dAdic') document.getElementById('dspDAdic').textContent = dat.dAdic;
  actualizar();
}

function elegirServicio(s) {
  dat.srv = s;
  [1, 2, 3].forEach(c => {
    const el = document.getElementById(`opt${c}`);
    if (c === s) el.classList.add('selected'); else el.classList.remove('selected');
  });
  actualizar();
}

function fmt(val) {
  return '$ ' + Math.max(0, val).toLocaleString('es-CO') + ' COP';
}

// Sincronización con el Backend Flask mediante API REST segura
async function actualizar() {
  dat.nom = document.getElementById('txtNom').value.trim() || 'Pendiente';

  // Primero calculamos localmente para respuesta instantánea
  const eq = dat.eq, dI = dat.dIni, dA = dat.dAdic, s = dat.srv;
  const vAlquiler = eq * dI * VDIA;
  const vAdicional = eq * dA * VDIA_ADIC;
  const subtotalEquipos = vAlquiler + vAdicional;
  const dtoFormula = (s === 3) ? (DTO_ESTABLECIMIENTO - DTO_CIUDAD) : 0.0;
  const vDomicilio = (s === 2) ? DOMI_FUERA : 0.0;
  const total = Math.max(0, vAlquiler + vAdicional - dtoFormula + vDomicilio);

  // Reflejar en la factura
  document.getElementById('recCli').textContent = dat.nom;
  document.getElementById('recEq').textContent = `${eq} ${eq === 1 ? 'computador' : 'computadores'}`;
  document.getElementById('recTie').textContent = `${dI} días iniciales ${dA > 0 ? 'y ' + dA + ' adicionales' : ''}`;

  const nombres = { 1: 'Dentro de la Ciudad', 2: 'Fuera de la Ciudad', 3: 'En Instalaciones SENA' };
  document.getElementById('recMod').textContent = nombres[s];

  document.getElementById('recDetIni').textContent = `${eq} eq × ${dI} días × $${VDIA.toLocaleString('es-CO')}`;
  document.getElementById('recMntIni').textContent = fmt(vAlquiler);

  const rA = document.getElementById('recRowAdic');
  if (dA > 0) {
    rA.style.display = 'table-row';
    document.getElementById('recDetAdic').textContent = `${eq} eq × ${dA} días × $${VDIA_ADIC.toLocaleString('es-CO')}`;
    document.getElementById('recMntAdic').textContent = fmt(vAdicional);
  } else {
    rA.style.display = 'none';
  }

  const rDesc = document.getElementById('recRowDesc');
  if (s === 3) {
    rDesc.style.display = 'table-row';
    const subtotalConDesc = subtotalEquipos - dtoFormula;
    document.getElementById('recDetDesc').textContent = `Subtotal (${fmt(subtotalEquipos)}) menos descuento de (${fmt(dtoFormula)}) = ${fmt(subtotalConDesc)}`;
    document.getElementById('recMntDesc').textContent = fmt(dtoFormula); // estrictamente en positivo
  } else {
    rDesc.style.display = 'none';
  }

  const rDomi = document.getElementById('recRowDomi');
  if (s === 2) {
    rDomi.style.display = 'table-row';
    document.getElementById('recMntDomi').textContent = fmt(vDomicilio); // estrictamente en positivo
  } else {
    rDomi.style.display = 'none';
  }

  document.getElementById('recMntTotal').textContent = fmt(total);

  // Llamada al endpoint backend en Flask para validación con 2 capas y Message Broker
  try {
    const res = await fetch('/api/liquidar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nombre: dat.nom,
        equipos: dat.eq,
        diasIniciales: dat.dIni,
        diasAdicionales: dat.dAdic,
        tipoServicio: dat.srv
      })
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById('txtFolio').textContent = `Folio: ${data.folio} • Fecha: ${data.fecha}`;
    }
  } catch (e) {
    // Si corre de modo offline sin el servidor Flask activo, el cálculo local mantiene todo funcional
  }
}

let hablando = false;
function leerVoz() {
  if (!('speechSynthesis' in window)) {
    alert('Su navegador no soporta lectura por voz.');
    return;
  }
  if (hablando) {
    window.speechSynthesis.cancel();
    hablando = false;
    document.getElementById('btnVozText').textContent = 'Escuchar Resumen por Voz';
    return;
  }
  const cli = dat.nom !== 'Pendiente' ? dat.nom : 'cliente';
  const tot = document.getElementById('recMntTotal').textContent;
  const texto = `Factura de ALQUILAPC para ${cli}. Total a pagar: ${tot}. Servicio procesado con éxito por el SENA.`;

  const utt = new SpeechSynthesisUtterance(texto);
  utt.lang = 'es-CO';
  utt.rate = 0.9;
  utt.onend = () => {
    hablando = false;
    document.getElementById('btnVozText').textContent = 'Escuchar Resumen por Voz';
  };
  hablando = true;
  document.getElementById('btnVozText').textContent = 'Detener Lectura de Voz';
  window.speechSynthesis.speak(utt);
}
