/** Config Tailwind para compilacion estatica local (espejo del config inline). */
module.exports = {
  darkMode: 'class',
  content: ["./login.html", "./index.html", "./index.mejorado.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        brand: { 50:'#f0f6ff', 100:'#e0edff', 200:'#c7ddff', 500:'#3b82f6', 600:'#2563eb', 700:'#1d4ed8', 900:'#1e3a8a' },
        risk: { low:'#10b981', medium:'#f59e0b', high:'#ef4444', alt:'#8b5cf6' }
      }
    }
  }
}
