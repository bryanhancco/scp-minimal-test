#!/bin/bash
echo "======================================"
echo "  SCP Smart Contracts - Setup Linux"
echo "======================================"

PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "❌ Python no encontrado. Instálalo primero."
    exit 1
fi
echo "✓ Python encontrado: $($PYTHON --version)"

if [ ! -d ".venv" ]; then
    $PYTHON -m venv .venv
    echo "✓ Entorno virtual creado"
else
    echo "⚠ Entorno virtual ya existe, reutilizando..."
fi

.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q
echo "✓ Dependencias instaladas"

CHROME_BIN=$(command -v chromium-browser || command -v chromium || command -v google-chrome || command -v google-chrome-stable)
if [ -z "$CHROME_BIN" ]; then
    echo "⚠ No se detectó Chrome/Chromium. Instálalo con:"
    echo "  Fedora/RHEL:  sudo dnf install chromium"
    echo "  Ubuntu/Debian: sudo apt install chromium-browser"
else
    CHROME_VERSION=$($CHROME_BIN --version 2>/dev/null | grep -oP '\d+' | head -1)
    echo "✓ Chromium/Chrome detectado: versión $CHROME_VERSION"
fi

CHROMEDRIVER=$(command -v chromedriver)
if [ -n "$CHROMEDRIVER" ]; then
    echo "✓ ChromeDriver del sistema detectado: $CHROMEDRIVER"
else
    echo "⚠ ChromeDriver no encontrado en PATH. webdriver-manager lo descargará automáticamente."
    echo "  O instálalo manualmente:"
    echo "  Fedora/RHEL:  sudo dnf install chromium-driver"
    echo "  Ubuntu/Debian: sudo apt install chromium-driver"
fi

echo ""
echo "======================================"
echo "  ✅ Setup completado"
echo "======================================"
echo ""
echo "Para ejecutar el proyecto:"
echo "  .venv/bin/python src/main.py"
echo ""
echo "O activa el entorno primero:"
echo "  source .venv/bin/activate"
echo "  python src/main.py"