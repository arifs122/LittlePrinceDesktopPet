#!/usr/bin/env bash
# Little Prince - Linux kurulum betigi.
# Uygulamayi ~/.local altina kurar ve baslatici olusturur.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="@APP_NAME@"
PREFIX="${XDG_DATA_HOME:-$HOME/.local/share}/littleprince"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"

mkdir -p "$PREFIX" "$BIN_DIR" "$APPS_DIR"
install -m 755 "$HERE/$APP" "$PREFIX/$APP"
install -m 644 "$HERE/littleprince.png" "$PREFIX/littleprince.png"
ln -sfn "$PREFIX/$APP" "$BIN_DIR/littleprince"

cat > "$APPS_DIR/littleprince.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Little Prince
Comment=A tiny Little Prince who lives on your desktop
Exec=$PREFIX/$APP
Icon=$PREFIX/littleprince.png
Terminal=false
Categories=Game;Amusement;
StartupNotify=false
EOF

chmod +x "$APPS_DIR/littleprince.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
fi

echo "Kuruldu: $PREFIX/$APP"
echo "Baslatmak icin: littleprince"
echo "Kaldirmak icin:"
echo "  rm -f '$BIN_DIR/littleprince' '$APPS_DIR/littleprince.desktop'"
echo "  rm -rf '$PREFIX'"
