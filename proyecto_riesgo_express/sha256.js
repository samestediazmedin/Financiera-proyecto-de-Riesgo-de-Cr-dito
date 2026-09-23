// ============================================================
// sha256.js — SHA-256 en JS puro (sin Web Crypto)
// ------------------------------------------------------------
// PROPÓSITO: implementación síncrona de SHA-256 usada como
// respaldo en login.html cuando el contexto no es seguro
// (file://) y crypto.subtle no existe.
//
// Limitación: solo entrada ASCII (contraseñas); devuelve null si
// la cadena contiene caracteres fuera de ASCII.
//
// Documentado: 2026-09-18
// ============================================================
/**
 * Calcula el hash SHA-256 de una cadena ASCII (implementación pura en JS).
 *
 * Algoritmo estándar FIPS 180-4: genera las constantes K a partir de los
 * 64 primeros primos, aplica padding PKCS#7 al mensaje, procesa bloques
 * de 64 bytes (16 palabras) con las rondas de compresión y serializa los
 * 8 registros del estado como hexadecimal (64 caracteres).
 *
 * @global
 * @param {string} ascii - Texto de entrada (solo ASCII; p. ej. una contraseña).
 * @returns {?string} Hash hexadecimal de 64 caracteres, o null si la entrada
 *   contiene caracteres no ASCII.
 */
function sha256Sync(ascii) {
  /**
   * Rotación circular a la derecha de 32 bits.
   * @param {number} v - Palabra de 32 bits.
   * @param {number} a - Cantidad de bits a rotar.
   * @returns {number} Resultado de la rotación.
   */
  function rightRotate(v, a) { return (v >>> a) | (v << (32 - a)); }
  var maxWord = Math.pow(2, 32), result = '';
  var words = [], asciiBitLength = ascii.length * 8;
  var hash = sha256Sync.h = sha256Sync.h || [];  // registros H0..H7 (fracciones de raíces de primos)
  var k = sha256Sync.k = sha256Sync.k || [];     // constantes K (raíces cúbicas de primos)
  var primeCounter = k.length, isComposite = {};
  for (var candidate = 2; primeCounter < 64; candidate++) {
    if (!isComposite[candidate]) {
      for (var i2 = 0; i2 < 313; i2 += candidate) isComposite[i2] = candidate;
      hash[primeCounter] = (Math.pow(candidate, 0.5) * maxWord) | 0;
      k[primeCounter++] = (Math.pow(candidate, 1 / 3) * maxWord) | 0;
    }
  }
  // Padding: bit '1' + ceros hasta congruente con 56 módulo 64.
  ascii += '\x80';
  while (ascii.length % 64 - 56) ascii += '\x00';
  // Conversión de bytes a palabras big-endian de 32 bits.
  for (var i = 0; i < ascii.length; i++) {
    var j = ascii.charCodeAt(i);
    if (j >> 8) return null; // no-ASCII no soportado en este fallback
    words[i >> 2] |= j << ((3 - i) % 4) * 8;
  }
  // Longitud original del mensaje en bits (64 bits big-endian al final del bloque).
  words[words.length] = (asciiBitLength / maxWord) | 0;
  words[words.length] = asciiBitLength;
  // Compresión: 64 rondas por bloque usando el plan de mensajes W y las
  // funciones Σ, σ y Ch/Maj del estándar SHA-256.
  for (var j2 = 0; j2 < words.length;) {
    var w = words.slice(j2, j2 += 16), oldHash = hash;
    hash = hash.slice(0, 8);
    for (var i3 = 0; i3 < 64; i3++) {
      var w15 = w[i3 - 15], w2 = w[i3 - 2];
      var a = hash[0], e = hash[4];
      var temp1 = hash[7]
        + (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25))
        + ((e & hash[5]) ^ ((~e) & hash[6]))
        + k[i3]
        + (w[i3] = (i3 < 16) ? w[i3] : (
          w[i3 - 16]
          + (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3))
          + w[i3 - 7]
          + (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10))
        ) | 0);
      var temp2 = (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22))
        + ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]));
      hash = [(temp1 + temp2) | 0].concat(hash);
      hash[4] = (hash[4] + temp1) | 0;
    }
    for (var i4 = 0; i4 < 8; i4++) hash[i4] = (hash[i4] + oldHash[i4]) | 0;
  }
  // Serialización final: cada registro H se emite como 4 bytes en hexadecimal.
  for (var i5 = 0; i5 < 8; i5++) {
    for (var j3 = 3; j3 + 1; j3--) {
      var b = (hash[i5] >> (j3 * 8)) & 255;
      result += ((b < 16) ? 0 : '') + b.toString(16);
    }
  }
  return result;
}
