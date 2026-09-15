// ============================================================
// datos.js — Simulación de la unión de las 3 bases de datos
// ------------------------------------------------------------
// Cruce conceptual por ID de cliente entre:
//   1) Base de Clientes        (id, nombre)
//   2) Base de Créditos        (monto, plazo, tasa)
//   3) Base de Historial/Mora  (moraDias, score, probDefault)
// Montos en COP (pesos colombianos).
// ============================================================

const baseDatosConsolidada = [
  {
    id: "CLI-001",
    nombre: "Empresa Alfa S.A.S.",
    monto: 120000000,      // COP expuestos
    plazo: 24,             // meses
    tasa: 11.5,            // % efectivo anual
    moraDias: 0,
    score: 820,
    probDefault: 0.03,     // 3% probabilidad de incumplimiento
    estado: "Bajo"
  },
  {
    id: "CLI-002",
    nombre: "Inversiones Beta S.A.",
    monto: 85000000,
    plazo: 36,
    tasa: 16.0,
    moraDias: 45,
    score: 610,
    probDefault: 0.18,
    estado: "Medio"
  },
  {
    id: "CLI-003",
    nombre: "Distribuidora Gamma Ltda.",
    monto: 210000000,
    plazo: 48,
    tasa: 22.5,
    moraDias: 95,
    score: 480,
    probDefault: 0.42,
    estado: "Alto"
  },
  {
    id: "CLI-004",
    nombre: "Servicios Delta S.A.S.",
    monto: 45000000,
    plazo: 12,
    tasa: 10.0,
    moraDias: 12,
    score: 730,
    probDefault: 0.07,
    estado: "Bajo"
  },
  {
    id: "CLI-005",
    nombre: "Grupo Epsilon S.A.",
    monto: 160000000,
    plazo: 36,
    tasa: 18.5,
    moraDias: 65,
    score: 540,
    probDefault: 0.27,
    estado: "Medio"
  },
  {
    id: "CLI-006",
    nombre: "Comercializadora Zeta",
    monto: 95000000,
    plazo: 24,
    tasa: 24.0,
    moraDias: 110,
    score: 420,
    probDefault: 0.55,
    estado: "Alto"
  }
];